from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .artifacts import read_json


class AbConfirmationError(ValueError):
    """Raised when repeated A/B benchmark confirmation cannot be produced."""


DEFAULT_NOISE_PERCENT = 1.0


@dataclass(frozen=True)
class AbConfirmationInputs:
    original_label: str
    recommended_label: str
    original_summaries: tuple[Path, ...]
    recommended_summaries: tuple[Path, ...]
    prompt_set_id: str
    noise_percent: float = DEFAULT_NOISE_PERCENT


def build_ab_confirmation_report(inputs: AbConfirmationInputs) -> dict[str, Any]:
    if not inputs.original_summaries:
        raise AbConfirmationError("original summaries are required")
    if not inputs.recommended_summaries:
        raise AbConfirmationError("recommended summaries are required")
    original = aggregate_profile(inputs.original_label, inputs.original_summaries)
    recommended = aggregate_profile(inputs.recommended_label, inputs.recommended_summaries)
    deltas = build_deltas(original, recommended, inputs.noise_percent)
    decision = decide_ab_default(original, recommended, deltas)
    report = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "prompt_set_id": inputs.prompt_set_id,
        "noise_percent": inputs.noise_percent,
        "decision": decision,
        "aggregates": {
            "original": original,
            "recommended": recommended,
        },
        "deltas": deltas,
        "inputs": {
            "original_label": inputs.original_label,
            "recommended_label": inputs.recommended_label,
            "original_summaries": [path.as_posix() for path in inputs.original_summaries],
            "recommended_summaries": [path.as_posix() for path in inputs.recommended_summaries],
        },
    }
    report["markdown"] = render_ab_markdown(report)
    return report


def aggregate_profile(label: str, paths: tuple[Path, ...]) -> dict[str, Any]:
    summaries = [load_summary(path) for path in paths]
    latencies = [_number(summary, "mean_latency_ms") for summary in summaries]
    throughputs = [_number(summary, "aggregate_tokens_per_second") for summary in summaries]
    success_count = sum(int(summary.get("success_count", 0) or 0) for summary in summaries)
    failure_count = sum(int(summary.get("failure_count", 0) or 0) for summary in summaries)
    total_count = success_count + failure_count
    return {
        "label": label,
        "source_summary_paths": [path.as_posix() for path in paths],
        "repetition_count": len(summaries),
        "success_count": success_count,
        "failure_count": failure_count,
        "failure_rate": failure_count / total_count if total_count else 1.0,
        "mean_latency_ms": mean(latencies),
        "latency_spread_ms": pstdev(latencies) if len(latencies) > 1 else 0.0,
        "mean_tokens_per_second": mean(throughputs),
        "tokens_per_second_spread": pstdev(throughputs) if len(throughputs) > 1 else 0.0,
        "source_metrics": summaries,
    }


def load_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AbConfirmationError(f"summary path does not exist: {path}")
    summary = read_json(path)
    _number(summary, "mean_latency_ms")
    _number(summary, "aggregate_tokens_per_second")
    if not isinstance(summary.get("success_count"), int):
        raise AbConfirmationError(f"{path}: success_count must be an integer")
    if not isinstance(summary.get("failure_count"), int):
        raise AbConfirmationError(f"{path}: failure_count must be an integer")
    return summary


def build_deltas(original: dict[str, Any], recommended: dict[str, Any], noise_percent: float) -> dict[str, Any]:
    latency_delta = recommended["mean_latency_ms"] - original["mean_latency_ms"]
    throughput_delta = recommended["mean_tokens_per_second"] - original["mean_tokens_per_second"]
    latency_percent = (latency_delta / original["mean_latency_ms"]) * 100
    throughput_percent = (throughput_delta / original["mean_tokens_per_second"]) * 100
    return {
        "mean_latency_ms": {
            "absolute": latency_delta,
            "percent": latency_percent,
            "recommended_better": latency_delta < 0 and abs(latency_percent) > noise_percent,
            "original_better": latency_delta > 0 and abs(latency_percent) > noise_percent,
        },
        "mean_tokens_per_second": {
            "absolute": throughput_delta,
            "percent": throughput_percent,
            "recommended_better": throughput_delta > 0 and abs(throughput_percent) > noise_percent,
            "original_better": throughput_delta < 0 and abs(throughput_percent) > noise_percent,
        },
        "failure_rate": {
            "absolute": recommended["failure_rate"] - original["failure_rate"],
            "recommended_higher": recommended["failure_rate"] > original["failure_rate"],
        },
    }


def decide_ab_default(original: dict[str, Any], recommended: dict[str, Any], deltas: dict[str, Any]) -> dict[str, str]:
    if recommended["failure_rate"] > original["failure_rate"]:
        return {"status": "keep-original", "reason": "recommended profile has a higher failure rate"}
    latency = deltas["mean_latency_ms"]
    throughput = deltas["mean_tokens_per_second"]
    if latency["recommended_better"] and throughput["recommended_better"]:
        return {"status": "switch-to-recommended", "reason": "recommended profile is materially better on latency and throughput"}
    if latency["original_better"] and throughput["original_better"]:
        return {"status": "keep-original", "reason": "original profile is materially better on latency and throughput"}
    return {"status": "inconclusive", "reason": "profile differences are mixed or inside the noise band"}


def render_ab_markdown(report: dict[str, Any]) -> str:
    decision = report["decision"]
    original = report["aggregates"]["original"]
    recommended = report["aggregates"]["recommended"]
    deltas = report["deltas"]
    lines = [
        "# A/B Benchmark Confirmation",
        "",
        f"- Decision: `{decision['status']}`",
        f"- Reason: {decision['reason']}",
        f"- Prompt set: `{report['prompt_set_id']}`",
        f"- Noise band: `{report['noise_percent']:.3f}%`",
        "",
        "## Aggregates",
        "",
    ]
    for aggregate in (original, recommended):
        lines.extend(
            [
                f"### {aggregate['label']}",
                "",
                f"- Repetitions: `{aggregate['repetition_count']}`",
                f"- Failure rate: `{aggregate['failure_rate']:.3%}`",
                f"- Mean latency: `{aggregate['mean_latency_ms']:.3f} ms`",
                f"- Latency spread: `{aggregate['latency_spread_ms']:.3f} ms`",
                f"- Mean throughput: `{aggregate['mean_tokens_per_second']:.3f} tokens/sec`",
                f"- Throughput spread: `{aggregate['tokens_per_second_spread']:.3f} tokens/sec`",
                "",
            ]
        )
    lines.extend(
        [
            "## Deltas (recommended - original)",
            "",
            f"- Mean latency: `{deltas['mean_latency_ms']['absolute']:.3f} ms` ({deltas['mean_latency_ms']['percent']:.3f}%)",
            f"- Mean throughput: `{deltas['mean_tokens_per_second']['absolute']:.3f} tokens/sec` ({deltas['mean_tokens_per_second']['percent']:.3f}%)",
            f"- Failure rate: `{deltas['failure_rate']['absolute']:.3%}`",
            "",
            "## Source Summaries",
            "",
        ]
    )
    for label, paths in (
        (original["label"], original["source_summary_paths"]),
        (recommended["label"], recommended["source_summary_paths"]),
    ):
        lines.append(f"- {label}: " + ", ".join(f"`{path}`" for path in paths))
    lines.append("")
    return "\n".join(lines)


def _number(summary: dict[str, Any], key: str) -> float:
    value = summary.get(key)
    if not isinstance(value, int | float):
        raise AbConfirmationError(f"{key} must be numeric")
    return float(value)
