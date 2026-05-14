from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from . import __version__
from .artifacts import write_json
from .discovery import DiscoveryTarget
from .redaction import REDACTION, redact_data
from .ssh import CommandResult, Executor


ProbeClass = Literal["read-only", "session-mutating", "persistent-mutating", "risky/unknown"]


class SystemTuningError(ValueError):
    """Raised when system tuning discovery cannot run safely."""


@dataclass(frozen=True)
class TuningProbe:
    probe_id: str
    family: str
    purpose: str
    command: str
    classification: ProbeClass
    parser: str
    timeout_seconds: int | None = None


PROBES: tuple[TuningProbe, ...] = (
    TuningProbe(
        "nvidia-driver",
        "nvidia",
        "Capture NVIDIA driver version",
        "nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n 1",
        "read-only",
        "line",
    ),
    TuningProbe(
        "gpu-power",
        "gpu",
        "Capture current and enforced GPU power limits",
        "nvidia-smi --query-gpu=power.limit,power.default_limit --format=csv,noheader,nounits | head -n 1",
        "read-only",
        "csv",
    ),
    TuningProbe(
        "gpu-clocks",
        "gpu",
        "Capture graphics/memory clocks and performance state",
        "nvidia-smi --query-gpu=clocks.mem,clocks.gr,pstate --format=csv,noheader,nounits | head -n 1",
        "read-only",
        "csv",
    ),
    TuningProbe(
        "gpu-persistence",
        "gpu",
        "Capture GPU persistence mode",
        "nvidia-smi --query-gpu=persistence_mode --format=csv,noheader | head -n 1",
        "read-only",
        "line",
    ),
    TuningProbe(
        "cpu-governor",
        "cpu",
        "Capture the first CPU frequency governor",
        "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor",
        "read-only",
        "line",
    ),
    TuningProbe(
        "cpu-topology",
        "cpu",
        "Capture CPU topology from lscpu",
        "lscpu",
        "read-only",
        "key_values",
    ),
    TuningProbe(
        "memory",
        "memory",
        "Capture memory and swap totals",
        "grep -E '^(MemTotal|SwapTotal):' /proc/meminfo",
        "read-only",
        "key_values",
    ),
    TuningProbe(
        "transparent-hugepages",
        "memory",
        "Capture transparent hugepage mode",
        "cat /sys/kernel/mm/transparent_hugepage/enabled",
        "read-only",
        "thp",
    ),
    TuningProbe(
        "kernel-limits",
        "kernel",
        "Capture open file limit",
        "ulimit -n",
        "read-only",
        "line",
    ),
    TuningProbe(
        "vllm-env",
        "runtime",
        "Capture relevant vLLM/CUDA environment variables",
        "env | grep -E '^(VLLM_|CUDA_|NCCL_|TORCH_)' | sort",
        "read-only",
        "env",
    ),
)


def validate_probe_catalog(probes: tuple[TuningProbe, ...] = PROBES) -> None:
    invalid = [probe.probe_id for probe in probes if probe.classification != "read-only"]
    if invalid:
        raise SystemTuningError(f"non-read-only probes are not allowed: {', '.join(invalid)}")


def run_system_tuning_discovery(
    target: DiscoveryTarget,
    executor: Executor,
    out_dir: Path,
    probes: tuple[TuningProbe, ...] = PROBES,
) -> dict[str, Any]:
    validate_probe_catalog(probes)
    started_at = _now()
    raw_results = [run_probe(target, executor, probe) for probe in probes]
    catalog = build_tuning_catalog(target, raw_results, started_at, _now())
    return save_system_tuning_artifacts(out_dir, raw_results, catalog, list(target.redact_values))


def run_probe(target: DiscoveryTarget, executor: Executor, probe: TuningProbe) -> dict[str, Any]:
    timeout = probe.timeout_seconds or target.timeout_seconds
    result = executor.run(probe.probe_id, probe.command, timeout)
    return probe_result_to_dict(probe, result)


def probe_result_to_dict(probe: TuningProbe, result: CommandResult) -> dict[str, Any]:
    status = "success" if result.exit_code == 0 and not result.timed_out else "unavailable"
    return {
        "probe_id": probe.probe_id,
        "family": probe.family,
        "purpose": probe.purpose,
        "command": probe.command,
        "classification": probe.classification,
        "parser": probe.parser,
        "status": status,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "timed_out": result.timed_out,
        "duration_ms": result.duration_ms,
    }


def build_tuning_catalog(
    target: DiscoveryTarget,
    raw_results: list[dict[str, Any]],
    started_at: str,
    completed_at: str,
) -> dict[str, Any]:
    by_id = {item["probe_id"]: item for item in raw_results}
    entries = {
        "nvidia.driver_version": entry(by_id["nvidia-driver"], "nvidia", "read-only", parse_line),
        "gpu.power_limit_watts": entry(by_id["gpu-power"], "gpu", "session-mutating", parse_csv),
        "gpu.clocks": entry(by_id["gpu-clocks"], "gpu", "session-mutating", parse_gpu_clocks),
        "gpu.persistence_mode": entry(by_id["gpu-persistence"], "gpu", "session-mutating", parse_line),
        "cpu.governor": entry(by_id["cpu-governor"], "cpu", "session-mutating", parse_line),
        "cpu.topology": entry(by_id["cpu-topology"], "cpu", "read-only", parse_key_values),
        "memory.totals": entry(by_id["memory"], "memory", "read-only", parse_key_values),
        "memory.transparent_hugepages": entry(by_id["transparent-hugepages"], "memory", "persistent-mutating", parse_thp),
        "kernel.open_file_limit": entry(by_id["kernel-limits"], "kernel", "session-mutating", parse_line),
        "vllm.env": entry(by_id["vllm-env"], "runtime", "session-mutating", parse_env),
    }
    unavailable = [key for key, value in entries.items() if value["status"] != "available"]
    return {
        "target_label": target.target_label,
        "tool_version": __version__,
        "started_at": started_at,
        "completed_at": completed_at,
        "status": "completed" if not unavailable else "completed-with-unavailable",
        "probe_count": len(raw_results),
        "entries": entries,
        "unavailable_entries": unavailable,
    }


def entry(
    raw: dict[str, Any],
    family: str,
    future_action_classification: ProbeClass,
    parser,
) -> dict[str, Any]:
    base = {
        "family": family,
        "source_probe": raw["probe_id"],
        "discovery_classification": raw["classification"],
        "future_action_classification": future_action_classification,
    }
    if raw["status"] != "success":
        return {
            **base,
            "status": "unavailable",
            "current_value": None,
            "reason": str(raw.get("stderr") or raw.get("stdout") or "probe failed"),
        }
    return {**base, "status": "available", "current_value": parser(str(raw["stdout"]))}


def parse_line(stdout: str) -> str:
    return stdout.strip().splitlines()[0] if stdout.strip() else ""


def parse_csv(stdout: str) -> list[str]:
    line = parse_line(stdout)
    return [part.strip() for part in line.split(",") if part.strip()]


def parse_gpu_clocks(stdout: str) -> dict[str, str | None]:
    parts = parse_csv(stdout)
    return {
        "memory_mhz": parts[0] if len(parts) > 0 else None,
        "graphics_mhz": parts[1] if len(parts) > 1 else None,
        "pstate": parts[2] if len(parts) > 2 else None,
    }


def parse_key_values(stdout: str) -> dict[str, str]:
    values = {}
    for line in stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def parse_thp(stdout: str) -> str:
    for token in stdout.strip().split():
        if token.startswith("[") and token.endswith("]"):
            return token.strip("[]")
    return parse_line(stdout)


def parse_env(stdout: str) -> dict[str, str]:
    values = {}
    for line in stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def save_system_tuning_artifacts(
    out_dir: Path,
    raw_results: list[dict[str, Any]],
    catalog: dict[str, Any],
    secrets: list[str],
) -> dict[str, Any]:
    raw_redacted, raw_count = redact_data(raw_results, secrets)
    catalog_redacted, catalog_count = redact_data(catalog, secrets)
    paths = {
        "raw": out_dir / "raw-probes.json",
        "catalog": out_dir / "catalog.json",
        "redaction": out_dir / "redaction-report.json",
    }
    write_json(paths["raw"], {"probes": raw_redacted})
    write_json(paths["catalog"], catalog_redacted)
    redaction = {
        "replacement": REDACTION,
        "redacted_value_count": raw_count + catalog_count,
        "artifact_paths": {key: str(path) for key, path in paths.items()},
        "commands": [
            {"probe_id": item["probe_id"], "classification": item["classification"]}
            for item in raw_results
        ],
    }
    write_json(paths["redaction"], redaction)
    return {
        "catalog": catalog_redacted,
        "artifact_paths": redaction["artifact_paths"],
        "redaction": redaction,
    }


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
