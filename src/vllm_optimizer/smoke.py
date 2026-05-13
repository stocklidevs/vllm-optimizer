from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .artifacts import write_json
from .discovery import DiscoveryTarget
from .redaction import REDACTION, redact_data
from .serve_profiles import ServeProfile, render_vllm_serve_command, shell_join
from .ssh import SshExecutor


class SmokeServeError(ValueError):
    """Raised when smoke serve cannot run safely."""


def build_smoke_serve_plan(profile: ServeProfile) -> dict[str, Any]:
    serve_command = render_vllm_serve_command(profile)
    return {
        "profile_id": profile.profile_id,
        "mode": "dry-run",
        "will_execute": False,
        "classification": "session-mutating",
        "preflight_checks": [
            f"port {profile.port} must be free",
            f"no matching vLLM process for {profile.served_model_name}",
        ],
        "serve_command": serve_command,
        "serve_command_line": shell_join(serve_command),
        "readiness": {
            "url": f"http://127.0.0.1:{profile.port}/v1/models",
            "timeout_seconds": 900,
        },
        "smoke_request": {
            "url": f"http://127.0.0.1:{profile.port}/v1/chat/completions",
            "messages": [{"role": "user", "content": "Say OK."}],
            "max_tokens": 4,
        },
        "cleanup": ["terminate managed vLLM process", "verify process exit"],
    }


def run_smoke_serve(
    target: DiscoveryTarget,
    profile: ServeProfile,
    out_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    preflight = run_preflight(target, profile)
    if not preflight["safe"]:
        return save_smoke_artifacts(
            out_dir=out_dir,
            target=target,
            plan=build_smoke_serve_plan(profile),
            summary={"status": "refused", "preflight": preflight},
            server_log="",
            response={},
            cleanup={},
        )

    script = build_remote_smoke_script(profile, timeout_seconds)
    result = SshExecutor(target.ssh_destination).run("smoke-serve", script, timeout_seconds + 30)
    parsed = parse_remote_smoke_output(result.stdout)
    server_log = parsed.get("server_log", "")
    summary = {
        "status": "completed" if result.exit_code == 0 else "failed",
        "exit_code": result.exit_code,
        "stderr": result.stderr,
        "preflight": preflight,
        "remote_summary": parsed.get("summary", {}),
    }
    return save_smoke_artifacts(
        out_dir=out_dir,
        target=target,
        plan=build_smoke_serve_plan(profile),
        summary=summary,
        server_log=server_log,
        response=parsed.get("response", {}),
        cleanup=parsed.get("cleanup", {}),
    )


def run_preflight(target: DiscoveryTarget, profile: ServeProfile) -> dict[str, Any]:
    executor = SshExecutor(target.ssh_destination)
    port_command = f"ss -ltn | grep -E ':{profile.port}[[:space:]]' || true"
    process_command = (
        "ps -eo pid,args | grep -F 'vllm' | "
        f"grep -F {sh_quote(profile.served_model_name)} | grep -v grep || true"
    )
    port = executor.run("preflight-port", port_command, target.timeout_seconds)
    process = executor.run("preflight-process", process_command, target.timeout_seconds)
    port_occupied = bool(port.stdout.strip())
    process_present = bool(process.stdout.strip())
    return {
        "safe": not port_occupied and not process_present,
        "port": {
            "command": port_command,
            "exit_code": port.exit_code,
            "occupied": port_occupied,
            "stdout": port.stdout,
            "stderr": port.stderr,
        },
        "process": {
            "command": process_command,
            "exit_code": process.exit_code,
            "present": process_present,
            "stdout": process.stdout,
            "stderr": process.stderr,
        },
    }


def build_remote_smoke_script(profile: ServeProfile, timeout_seconds: int) -> str:
    serve_command = shell_join(render_vllm_serve_command(profile))
    request = {
        "model": profile.served_model_name,
        "messages": [{"role": "user", "content": "Say OK."}],
        "max_tokens": 4,
        "temperature": 0,
    }
    request_json = json.dumps(request)
    return f"""
set -u
LOG=$(mktemp /tmp/vllm-smoke-{profile.profile_id}.XXXXXX.log)
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
  if curl -fsS http://127.0.0.1:{profile.port}/v1/models >/tmp/vllm-smoke-models.json 2>/tmp/vllm-smoke-curl.err; then
    READY=1
    break
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    break
  fi
  sleep 2
done
if [ "$READY" -eq 1 ]; then
  curl -sS -w '\\nHTTP_STATUS:%{{http_code}}\\n' \\
    -H 'Content-Type: application/json' \\
    -d {sh_quote(request_json)} \\
    http://127.0.0.1:{profile.port}/v1/chat/completions > /tmp/vllm-smoke-response.json 2>/tmp/vllm-smoke-request.err || true
fi
cleanup
if kill -0 "$PID" 2>/dev/null; then CLEANED=false; else CLEANED=true; fi
echo __VLLM_SMOKE_SUMMARY_START__
printf '{{"pid":"%s","ready":%s,"cleaned":%s}}\\n' "$PID" "$READY" "$CLEANED"
echo __VLLM_SMOKE_RESPONSE_START__
cat /tmp/vllm-smoke-response.json 2>/dev/null || true
echo __VLLM_SMOKE_CLEANUP_START__
printf '{{"cleaned":%s}}\\n' "$CLEANED"
echo __VLLM_SMOKE_LOG_START__
cat "$LOG" 2>/dev/null || true
test "$READY" -eq 1
"""


def parse_remote_smoke_output(stdout: str) -> dict[str, Any]:
    summary_text = section(stdout, "__VLLM_SMOKE_SUMMARY_START__", "__VLLM_SMOKE_RESPONSE_START__")
    response_text = section(stdout, "__VLLM_SMOKE_RESPONSE_START__", "__VLLM_SMOKE_CLEANUP_START__")
    cleanup_text = section(stdout, "__VLLM_SMOKE_CLEANUP_START__", "__VLLM_SMOKE_LOG_START__")
    server_log = stdout.split("__VLLM_SMOKE_LOG_START__", 1)[1] if "__VLLM_SMOKE_LOG_START__" in stdout else ""
    return {
        "summary": parse_json_section(summary_text),
        "response": {"raw": response_text.strip()},
        "cleanup": parse_json_section(cleanup_text),
        "server_log": server_log.strip(),
    }


def save_smoke_artifacts(
    *,
    out_dir: Path,
    target: DiscoveryTarget,
    plan: dict[str, Any],
    summary: dict[str, Any],
    server_log: str,
    response: dict[str, Any],
    cleanup: dict[str, Any],
) -> dict[str, Any]:
    secrets = list(target.redact_values)
    redacted_plan, plan_count = redact_data(plan, secrets)
    redacted_summary, summary_count = redact_data(summary, secrets)
    redacted_log, log_count = redact_data({"log": server_log}, secrets)
    redacted_response, response_count = redact_data(response, secrets)
    redacted_cleanup, cleanup_count = redact_data(cleanup, secrets)
    report = {
        "replacement": REDACTION,
        "redacted_value_count": plan_count + summary_count + log_count + response_count + cleanup_count,
        "artifact_paths": {
            "plan": str(out_dir / "plan.json"),
            "summary": str(out_dir / "summary.json"),
            "server_log": str(out_dir / "server-log.json"),
            "response": str(out_dir / "smoke-response.json"),
            "cleanup": str(out_dir / "cleanup.json"),
            "redaction": str(out_dir / "redaction-report.json"),
        },
    }
    write_json(out_dir / "plan.json", redacted_plan)
    write_json(out_dir / "summary.json", redacted_summary)
    write_json(out_dir / "server-log.json", redacted_log)
    write_json(out_dir / "smoke-response.json", redacted_response)
    write_json(out_dir / "cleanup.json", redacted_cleanup)
    write_json(out_dir / "redaction-report.json", report)
    return {"status": summary["status"], "artifact_paths": report["artifact_paths"]}


def section(text: str, start: str, end: str) -> str:
    if start not in text:
        return ""
    after = text.split(start, 1)[1]
    if end not in after:
        return after
    return after.split(end, 1)[0]


def parse_json_section(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        return {}
    first_line = stripped.splitlines()[0]
    try:
        value = json.loads(first_line)
    except json.JSONDecodeError:
        return {"raw": stripped}
    return value if isinstance(value, dict) else {"value": value}


def sh_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"
