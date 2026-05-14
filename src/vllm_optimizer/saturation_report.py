from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .artifacts import read_json
from .workload_report import WorkloadReportError, compact_ranked_candidate, top_balanced


class SaturationReportError(ValueError):
    """Raised when a concurrency saturation report cannot be produced."""


@dataclass(frozen=True)
class SaturationInput:
    concurrency: int
    ranking_path: Path


@dataclass(frozen=True)
class SaturationReportInputs:
    rankings: tuple[SaturationInput, ...]


def build_saturation_report(inputs: SaturationReportInputs) -> dict[str, Any]:
    if not inputs.rankings:
        raise SaturationReportError("at least one concurrency ranking is required")
    levels = [build_level_summary(item) for item in sorted(inputs.rankings, key=lambda item: item.concurrency)]
    recommendation = recommend_level(levels)
    report = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "levels": levels,
        "recommendation": recommendation,
        "next_actions": next_actions(levels, recommendation),
    }
    report["markdown"] = render_saturation_markdown(report)
    return report


def build_level_summary(item: SaturationInput) -> dict[str, Any]:
    if item.concurrency < 1:
        raise SaturationReportError("concurrency must be a positive integer")
    ranking = _read_required(item.ranking_path)
    try:
        winner = top_balanced(ranking)
    except WorkloadReportError as exc:
        raise SaturationReportError(str(exc)) from exc
    metrics = winner.get("metrics", {})
    return {
        "concurrency": item.concurrency,
        "ranking_path": item.ranking_path.as_posix(),
        "sweep_id": ranking.get("sweep_id"),
        "winner": compact_ranked_candidate({"candidate_id": winner.get("candidate_id"), **winner}),
        "metrics": metrics,
        "overrides": winner.get("overrides", {}),
        "ranked_candidate_count": ranking.get("ranked_candidate_count"),
        "source_trial_count": ranking.get("source_trial_count"),
    }


def recommend_level(levels: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [level for level in levels if _numeric(level, "aggregate_tokens_per_second") is not None]
    if not eligible:
        raise SaturationReportError("no rankable concurrency levels")
    stable = [level for level in eligible if _failure_rate(level) == 0]
    candidates = stable or eligible
    winner = sorted(
        candidates,
        key=lambda level: (
            -float(_numeric(level, "aggregate_tokens_per_second") or 0.0),
            _failure_rate(level),
            float(_numeric(level, "mean_latency_ms") or 0.0),
            int(level["concurrency"]),
            str(level.get("winner", {}).get("candidate_id", "")),
        ),
    )[0]
    return {
        "concurrency": winner["concurrency"],
        "candidate_id": winner["winner"].get("candidate_id"),
        "metrics": winner["metrics"],
        "overrides": winner["overrides"],
        "reason": "Selected by highest throughput among stable levels, then failure rate, latency, and lower concurrency.",
    }


def next_actions(levels: list[dict[str, Any]], recommendation: dict[str, Any]) -> list[str]:
    actions = [
        f"Use concurrency {recommendation['concurrency']} as the current saturation candidate for repeated confirmation.",
        "Run repeated confirmation before promoting any saturation winner as a default.",
    ]
    if any(_failure_rate(level) > 0 for level in levels):
        actions.append("Inspect failed candidates before increasing concurrency further.")
    return actions


def render_saturation_markdown(report: dict[str, Any]) -> str:
    lines = ["# Concurrency Saturation", "", "## Levels", ""]
    for level in report["levels"]:
        metrics = level["metrics"]
        lines.extend(
            [
                f"### concurrency {level['concurrency']}",
                "",
                f"- Sweep: `{level['sweep_id']}`",
                f"- Winner: `{level['winner'].get('candidate_id')}`",
                f"- Mean latency: `{_fmt(metrics.get('mean_latency_ms'))} ms`",
                f"- Throughput: `{_fmt(metrics.get('aggregate_tokens_per_second'))} tokens/sec`",
                f"- Failure rate: `{_fmt_pct(metrics.get('failure_rate'))}`",
                "",
                "Overrides:",
                "",
            ]
        )
        for name, value in sorted((level.get("overrides") or {}).items()):
            lines.append(f"- {name}: `{value}`")
        lines.append("")
    recommendation = report["recommendation"]
    metrics = recommendation["metrics"]
    lines.extend(
        [
            "## Recommendation",
            "",
            f"- Concurrency: `{recommendation['concurrency']}`",
            f"- Candidate: `{recommendation['candidate_id']}`",
            f"- Throughput: `{_fmt(metrics.get('aggregate_tokens_per_second'))} tokens/sec`",
            f"- Mean latency: `{_fmt(metrics.get('mean_latency_ms'))} ms`",
            f"- Reason: {recommendation['reason']}",
            "",
            "## Next Actions",
            "",
        ]
    )
    for action in report["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def _read_required(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SaturationReportError(f"ranking path does not exist: {path}")
    return read_json(path)


def _numeric(level: dict[str, Any], key: str) -> float | None:
    value = level.get("metrics", {}).get(key)
    if isinstance(value, int | float):
        return float(value)
    return None


def _failure_rate(level: dict[str, Any]) -> float:
    value = level.get("metrics", {}).get("failure_rate")
    if isinstance(value, int | float):
        return float(value)
    return 1.0


def _fmt(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.3f}"
    return "n/a"


def _fmt_pct(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.3%}"
    return "n/a"
