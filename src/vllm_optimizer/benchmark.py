from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from .artifacts import read_json, write_json
from .discovery import DiscoveryTarget
from .redaction import REDACTION, redact_data
from .serve_profiles import ServeProfile
from .smoke import build_smoke_serve_plan, parse_remote_smoke_output, run_preflight, sh_quote
from .ssh import SshExecutor


class BenchmarkError(ValueError):
    """Raised when benchmark inputs are invalid."""


@dataclass(frozen=True)
class PromptCase:
    case_id: str
    messages: tuple[dict[str, str], ...]
    max_tokens: int
    temperature: float


@dataclass(frozen=True)
class PromptSet:
    prompt_set_id: str
    cases: tuple[PromptCase, ...]


def load_prompt_set(path: Path) -> PromptSet:
    data = read_json(path)
    prompt_set_id = data.get("prompt_set_id")
    cases = data.get("cases")
    errors: list[str] = []
    if not isinstance(prompt_set_id, str) or not prompt_set_id:
        errors.append("prompt_set_id is required")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty array")
        cases = []

    parsed_cases: list[PromptCase] = []
    for index, item in enumerate(cases):
        if not isinstance(item, dict):
            errors.append(f"cases[{index}] must be an object")
            continue
        case_id = item.get("case_id")
        messages = item.get("messages")
        max_tokens = item.get("max_tokens")
        temperature = item.get("temperature", 0)
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"cases[{index}].case_id is required")
            case_id = ""
        if not isinstance(messages, list) or not messages:
            errors.append(f"cases[{index}].messages must be a non-empty array")
            messages = []
        if not isinstance(max_tokens, int) or max_tokens < 1:
            errors.append(f"cases[{index}].max_tokens must be a positive integer")
            max_tokens = 1
        if not isinstance(temperature, int | float):
            errors.append(f"cases[{index}].temperature must be a number")
            temperature = 0
        parsed_cases.append(
            PromptCase(
                case_id=case_id,
                messages=tuple(messages),
                max_tokens=max_tokens,
                temperature=float(temperature),
            )
        )

    if errors:
        raise BenchmarkError("; ".join(errors))
    return PromptSet(prompt_set_id=prompt_set_id, cases=tuple(parsed_cases))


def build_benchmark_plan(profile: ServeProfile, prompt_set: PromptSet) -> dict[str, Any]:
    return {
        "profile_id": profile.profile_id,
        "prompt_set_id": prompt_set.prompt_set_id,
        "mode": "dry-run",
        "will_execute": False,
        "serve_plan": build_smoke_serve_plan(profile),
        "request_sequence": [
            {
                "case_id": case.case_id,
                "max_tokens": case.max_tokens,
                "temperature": case.temperature,
            }
            for case in prompt_set.cases
        ],
        "metrics": ["duration_ms", "prompt_tokens", "completion_tokens", "total_tokens", "tokens_per_second"],
    }


def summarize_metrics(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    success = [item for item in metrics if item.get("status") == "success"]
    failures = [item for item in metrics if item.get("status") != "success"]
    durations = [float(item["duration_ms"]) for item in success if isinstance(item.get("duration_ms"), int | float)]
    total_tokens = sum(int(item.get("total_tokens", 0) or 0) for item in success)
    total_seconds = sum(float(item.get("duration_ms", 0) or 0) for item in success) / 1000
    return {
        "success_count": len(success),
        "failure_count": len(failures),
        "mean_latency_ms": mean(durations) if durations else None,
        "total_tokens": total_tokens,
        "aggregate_tokens_per_second": total_tokens / total_seconds if total_seconds > 0 else None,
    }


def save_benchmark_artifacts(
    out_dir: Path,
    target: DiscoveryTarget,
    plan: dict[str, Any],
    prompt_set: PromptSet,
    responses: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
    server_log: str,
    cleanup: dict[str, Any],
) -> dict[str, Any]:
    summary = summarize_metrics(metrics)
    secrets = list(target.redact_values)
    artifacts = {
        "plan": plan,
        "prompts": prompt_set_to_dict(prompt_set),
        "responses": {"responses": responses},
        "metrics": {"metrics": metrics},
        "summary": summary,
        "server_log": {"log": server_log},
        "cleanup": cleanup,
    }
    counts = 0
    redacted: dict[str, Any] = {}
    for key, value in artifacts.items():
        redacted_value, count = redact_data(value, secrets)
        redacted[key] = redacted_value
        counts += count
    paths = {
        "plan": out_dir / "plan.json",
        "prompts": out_dir / "prompts.json",
        "responses": out_dir / "responses.json",
        "metrics": out_dir / "metrics.json",
        "summary": out_dir / "summary.json",
        "server_log": out_dir / "server-log.json",
        "cleanup": out_dir / "cleanup.json",
        "redaction": out_dir / "redaction-report.json",
    }
    for key, path in paths.items():
        if key == "redaction":
            continue
        write_json(path, redacted[key])
    report = {
        "replacement": REDACTION,
        "redacted_value_count": counts,
        "artifact_paths": {key: str(path) for key, path in paths.items()},
    }
    write_json(paths["redaction"], report)
    return {"summary": redacted["summary"], "artifact_paths": report["artifact_paths"]}


def run_baseline_benchmark(
    target: DiscoveryTarget,
    profile: ServeProfile,
    prompt_set: PromptSet,
    out_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    plan = build_benchmark_plan(profile, prompt_set)
    preflight = run_preflight(target, profile)
    if not preflight["safe"]:
        return save_benchmark_artifacts(
            out_dir,
            target,
            plan,
            prompt_set,
            [],
            [{"case_id": "preflight", "status": "failed", "error": "unsafe preflight"}],
            "",
            {},
        )

    script = build_remote_benchmark_script(profile, prompt_set, timeout_seconds)
    result = SshExecutor(target.ssh_destination).run(
        "benchmark-run", script, timeout_seconds + 60
    )
    parsed = parse_remote_benchmark_output(result.stdout)
    metrics = parsed["metrics"]
    if result.exit_code != 0 and not metrics:
        metrics = [{"case_id": "benchmark", "status": "failed", "error": result.stderr}]
    return save_benchmark_artifacts(
        out_dir,
        target,
        plan,
        prompt_set,
        parsed["responses"],
        metrics,
        parsed["server_log"],
        parsed["cleanup"],
    )


def build_remote_benchmark_script(
    profile: ServeProfile, prompt_set: PromptSet, timeout_seconds: int
) -> str:
    from .serve_profiles import render_vllm_serve_command, shell_join

    serve_command = shell_join(render_vllm_serve_command(profile))
    cases_json = json_dump(
        [
            {
                "case_id": case.case_id,
                "messages": list(case.messages),
                "max_tokens": case.max_tokens,
                "temperature": case.temperature,
            }
            for case in prompt_set.cases
        ]
    )
    return f"""
set -u
LOG=$(mktemp /tmp/vllm-benchmark-{profile.profile_id}.XXXXXX.log)
PID=""
cleanup() {{
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    for i in $(seq 1 30); do
      kill -0 "$PID" 2>/dev/null || break
      sleep 1
    done
    kill -9 "$PID" 2>/dev/null || true
  fi
}}
trap cleanup EXIT
{serve_command} >"$LOG" 2>&1 &
PID=$!
READY=0
START=$(date +%s)
while [ $(( $(date +%s) - START )) -lt {timeout_seconds} ]; do
  if curl -fsS http://127.0.0.1:{profile.port}/v1/models >/tmp/vllm-benchmark-models.json 2>/tmp/vllm-benchmark-curl.err; then
    READY=1
    break
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    break
  fi
  sleep 2
done
echo __VLLM_BENCHMARK_RESPONSES_START__
if [ "$READY" -eq 1 ]; then
  CASES={sh_quote(cases_json)}
  printf '%s' "$CASES" | python3 -c '
import json, subprocess, time
cases = json.load(__import__("sys").stdin)
for case in cases:
    body = {{
        "model": "{profile.served_model_name}",
        "messages": case["messages"],
        "max_tokens": case["max_tokens"],
        "temperature": case["temperature"],
    }}
    started = time.perf_counter()
    proc = subprocess.run(
        ["curl", "-sS", "-w", "\\nHTTP_STATUS:%{{http_code}}\\n", "-H", "Content-Type: application/json", "-d", json.dumps(body), "http://127.0.0.1:{profile.port}/v1/chat/completions"],
        text=True,
        capture_output=True,
    )
    duration_ms = int((time.perf_counter() - started) * 1000)
    print(json.dumps({{"case_id": case["case_id"], "duration_ms": duration_ms, "stdout": proc.stdout, "stderr": proc.stderr, "exit_code": proc.returncode}}))
'
fi
cleanup
if kill -0 "$PID" 2>/dev/null; then CLEANED=false; else CLEANED=true; fi
echo __VLLM_BENCHMARK_CLEANUP_START__
printf '{{"cleaned":%s,"ready":%s,"pid":"%s"}}\\n' "$CLEANED" "$READY" "$PID"
echo __VLLM_BENCHMARK_LOG_START__
cat "$LOG" 2>/dev/null || true
test "$READY" -eq 1
"""


def parse_remote_benchmark_output(stdout: str) -> dict[str, Any]:
    responses_text = section(stdout, "__VLLM_BENCHMARK_RESPONSES_START__", "__VLLM_BENCHMARK_CLEANUP_START__")
    cleanup_text = section(stdout, "__VLLM_BENCHMARK_CLEANUP_START__", "__VLLM_BENCHMARK_LOG_START__")
    server_log = stdout.split("__VLLM_BENCHMARK_LOG_START__", 1)[1] if "__VLLM_BENCHMARK_LOG_START__" in stdout else ""
    responses: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    for line in responses_text.splitlines():
        line = line.strip()
        if not line:
            continue
        row = json_load(line)
        responses.append(row)
        metrics.append(metric_from_response(row))
    return {
        "responses": responses,
        "metrics": metrics,
        "cleanup": json_load(cleanup_text.strip().splitlines()[0]) if cleanup_text.strip() else {},
        "server_log": server_log.strip(),
    }


def metric_from_response(row: dict[str, Any]) -> dict[str, Any]:
    raw = str(row.get("stdout", ""))
    status = "failed"
    http_status = None
    payload_text = raw
    if "HTTP_STATUS:" in raw:
        payload_text, status_text = raw.rsplit("HTTP_STATUS:", 1)
        http_status = status_text.strip()
        status = "success" if http_status == "200" and row.get("exit_code") == 0 else "failed"
    payload = json_load(payload_text.strip()) if payload_text.strip().startswith("{") else {}
    usage = payload.get("usage", {}) if isinstance(payload, dict) else {}
    total_tokens = usage.get("total_tokens")
    duration_ms = row.get("duration_ms")
    tokens_per_second = None
    if isinstance(total_tokens, int) and isinstance(duration_ms, int | float) and duration_ms > 0:
        tokens_per_second = total_tokens / (duration_ms / 1000)
    return {
        "case_id": row.get("case_id"),
        "status": status,
        "http_status": http_status,
        "duration_ms": duration_ms,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": total_tokens,
        "tokens_per_second": tokens_per_second,
    }


def prompt_set_to_dict(prompt_set: PromptSet) -> dict[str, Any]:
    return {
        "prompt_set_id": prompt_set.prompt_set_id,
        "cases": [
            {
                "case_id": case.case_id,
                "messages": list(case.messages),
                "max_tokens": case.max_tokens,
                "temperature": case.temperature,
            }
            for case in prompt_set.cases
        ],
    }


def json_dump(value: Any) -> str:
    import json

    return json.dumps(value, separators=(",", ":"))


def json_load(value: str) -> dict[str, Any]:
    import json

    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return {"raw": value}
    return data if isinstance(data, dict) else {"value": data}


def section(text: str, start: str, end: str) -> str:
    if start not in text:
        return ""
    after = text.split(start, 1)[1]
    if end not in after:
        return after
    return after.split(end, 1)[0]
