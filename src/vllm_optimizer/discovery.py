from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from . import __version__
from .artifacts import read_json, write_json
from .redaction import REDACTION, redact_data
from .ssh import CommandResult, Executor


class DiscoveryError(ValueError):
    """Raised for invalid discovery inputs."""


@dataclass(frozen=True)
class DiscoveryTarget:
    target_label: str
    ssh_destination: str
    redact_values: tuple[str, ...]
    timeout_seconds: int = 10


@dataclass(frozen=True)
class ProbeDefinition:
    probe_id: str
    purpose: str
    command: str
    classification: Literal["read-only"]
    parser: str
    timeout_seconds: int | None = None


PROBES: tuple[ProbeDefinition, ...] = (
    ProbeDefinition("connectivity", "Verify SSH command execution", "hostname", "read-only", "hostname"),
    ProbeDefinition("os-release", "Collect OS release facts", "cat /etc/os-release", "read-only", "os_release"),
    ProbeDefinition("kernel", "Collect kernel identity", "uname -a", "read-only", "kernel"),
    ProbeDefinition(
        "gpu",
        "Collect GPU and NVIDIA driver facts",
        "nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader",
        "read-only",
        "gpu",
    ),
    ProbeDefinition(
        "cuda-visible",
        "Check CUDA visibility from Python",
        "python3 -c \"import torch; print(torch.cuda.is_available())\"",
        "read-only",
        "cuda_visible",
    ),
    ProbeDefinition("python", "Collect Python version", "python3 --version", "read-only", "python"),
    ProbeDefinition(
        "vllm",
        "Collect vLLM import/version availability",
        "python3 -c \"import importlib.metadata as m; print(m.version('vllm'))\"",
        "read-only",
        "vllm",
    ),
)


def load_target(path: Path) -> DiscoveryTarget:
    data = read_json(path)
    target_label = data.get("target_label")
    ssh_destination = data.get("ssh_destination")
    timeout_seconds = data.get("timeout_seconds", 10)
    redact_values = data.get("redact_values", [])

    errors: list[str] = []
    if not isinstance(target_label, str) or not target_label:
        errors.append("target_label is required")
    if not isinstance(ssh_destination, str) or not ssh_destination:
        errors.append("ssh_destination is required")
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
        errors.append("timeout_seconds must be an integer >= 1")
    if not isinstance(redact_values, list) or not all(
        isinstance(item, str) for item in redact_values
    ):
        errors.append("redact_values must be an array of strings")
    if errors:
        raise DiscoveryError("; ".join(errors))

    return DiscoveryTarget(
        target_label=target_label,
        ssh_destination=ssh_destination,
        timeout_seconds=timeout_seconds,
        redact_values=tuple(redact_values),
    )


def validate_probe_catalog(probes: tuple[ProbeDefinition, ...] = PROBES) -> None:
    invalid = [probe.probe_id for probe in probes if probe.classification != "read-only"]
    if invalid:
        raise DiscoveryError(f"non-read-only probes are not allowed: {', '.join(invalid)}")


def run_discovery(
    target: DiscoveryTarget,
    executor: Executor,
    out_dir: Path,
    probes: tuple[ProbeDefinition, ...] = PROBES,
) -> dict[str, Any]:
    validate_probe_catalog(probes)
    started_at = datetime.now(UTC).isoformat()
    raw_results: list[dict[str, Any]] = []

    connectivity = probes[0]
    first = run_probe(connectivity, target, executor)
    raw_results.append(first)

    if first["status"] != "success":
        for probe in probes[1:]:
            raw_results.append(skipped_probe(probe, "connectivity failed"))
        status = "connectivity-failed"
    else:
        for probe in probes[1:]:
            raw_results.append(run_probe(probe, target, executor))
        status = "completed"

    facts = parse_facts(raw_results)
    completed_at = datetime.now(UTC).isoformat()
    summary = {
        "run_id": f"{target.target_label}-{started_at.replace(':', '').replace('+', 'z')}",
        "target_label": target.target_label,
        "started_at": started_at,
        "completed_at": completed_at,
        "tool_version": __version__,
        "status": status,
        "facts": facts,
        "probes": [
            {
                "probe_id": item["probe_id"],
                "classification": item["classification"],
                "status": item["status"],
                "exit_code": item["exit_code"],
                "timed_out": item["timed_out"],
            }
            for item in raw_results
        ],
    }
    return save_discovery_artifacts(out_dir, raw_results, summary, list(target.redact_values))


def run_probe(
    probe: ProbeDefinition, target: DiscoveryTarget, executor: Executor
) -> dict[str, Any]:
    timeout = probe.timeout_seconds or target.timeout_seconds
    result = executor.run(probe.probe_id, probe.command, timeout)
    return probe_result_to_dict(probe, result)


def probe_result_to_dict(probe: ProbeDefinition, result: CommandResult) -> dict[str, Any]:
    status = "success" if result.exit_code == 0 and not result.timed_out else "failed"
    return {
        "probe_id": probe.probe_id,
        "purpose": probe.purpose,
        "command": probe.command,
        "classification": probe.classification,
        "status": status,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "timed_out": result.timed_out,
        "duration_ms": result.duration_ms,
    }


def skipped_probe(probe: ProbeDefinition, reason: str) -> dict[str, Any]:
    return {
        "probe_id": probe.probe_id,
        "purpose": probe.purpose,
        "command": probe.command,
        "classification": probe.classification,
        "status": "skipped",
        "exit_code": None,
        "stdout": "",
        "stderr": reason,
        "timed_out": False,
        "duration_ms": 0,
    }


def parse_facts(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {item["probe_id"]: item for item in results}
    facts: dict[str, Any] = {
        "connectivity": by_id.get("connectivity", {}).get("status") == "success",
        "unavailable": {},
    }
    _parse_hostname(facts, by_id.get("connectivity"))
    _parse_os(facts, by_id.get("os-release"))
    _parse_kernel(facts, by_id.get("kernel"))
    _parse_gpu(facts, by_id.get("gpu"))
    _parse_cuda(facts, by_id.get("cuda-visible"))
    _parse_python(facts, by_id.get("python"))
    _parse_vllm(facts, by_id.get("vllm"))
    return facts


def save_discovery_artifacts(
    out_dir: Path,
    raw_results: list[dict[str, Any]],
    summary: dict[str, Any],
    secrets: list[str],
) -> dict[str, Any]:
    raw_redacted, raw_count = redact_data(raw_results, secrets)
    summary_redacted, summary_count = redact_data(summary, secrets)
    report = {
        "replacement": REDACTION,
        "redacted_value_count": raw_count + summary_count,
        "artifact_paths": {
            "raw": str(out_dir / "raw-probes.json"),
            "summary": str(out_dir / "summary.json"),
            "redaction": str(out_dir / "redaction-report.json"),
        },
    }
    write_json(out_dir / "raw-probes.json", {"probes": raw_redacted})
    write_json(out_dir / "summary.json", summary_redacted)
    write_json(out_dir / "redaction-report.json", report)
    return {
        "status": summary["status"],
        "artifact_paths": report["artifact_paths"],
        "summary": summary_redacted,
        "redaction": report,
    }


def _require_success(facts: dict[str, Any], result: dict[str, Any] | None, key: str) -> str | None:
    if not result or result["status"] != "success":
        facts["unavailable"][key] = result["stderr"] if result else "missing probe"
        return None
    return str(result["stdout"]).strip()


def _parse_hostname(facts: dict[str, Any], result: dict[str, Any] | None) -> None:
    stdout = _require_success(facts, result, "hostname")
    if stdout:
        facts["hostname"] = stdout.splitlines()[0]


def _parse_os(facts: dict[str, Any], result: dict[str, Any] | None) -> None:
    stdout = _require_success(facts, result, "os")
    if not stdout:
        return
    values = {}
    for line in stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
    facts["os"] = {
        "name": values.get("NAME"),
        "version_id": values.get("VERSION_ID"),
        "pretty_name": values.get("PRETTY_NAME"),
    }


def _parse_kernel(facts: dict[str, Any], result: dict[str, Any] | None) -> None:
    stdout = _require_success(facts, result, "kernel")
    if stdout:
        facts["kernel"] = stdout


def _parse_gpu(facts: dict[str, Any], result: dict[str, Any] | None) -> None:
    stdout = _require_success(facts, result, "gpu")
    if not stdout:
        return
    first = stdout.splitlines()[0]
    parts = [part.strip() for part in first.split(",")]
    facts["gpu"] = {"name": parts[0] if parts else None}
    if len(parts) > 1:
        facts["nvidia_driver"] = parts[1]
    if len(parts) > 2:
        facts["gpu"]["memory_total"] = parts[2]


def _parse_cuda(facts: dict[str, Any], result: dict[str, Any] | None) -> None:
    stdout = _require_success(facts, result, "cuda_visible")
    if stdout:
        facts["cuda_visible"] = stdout.lower() == "true"


def _parse_python(facts: dict[str, Any], result: dict[str, Any] | None) -> None:
    stdout = _require_success(facts, result, "python")
    if stdout:
        facts["python"] = {"version": stdout}


def _parse_vllm(facts: dict[str, Any], result: dict[str, Any] | None) -> None:
    stdout = _require_success(facts, result, "vllm")
    if stdout:
        facts["vllm"] = {"available": True, "version": stdout.splitlines()[0]}
