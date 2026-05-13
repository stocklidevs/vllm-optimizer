from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .artifacts import read_json


class ReportError(ValueError):
    """Raised when a comparison report cannot be produced."""


@dataclass(frozen=True)
class ReportInputs:
    baseline: Path | None = None
    sweep_ranking: Path | None = None
    repeated_ranking: Path | None = None


def build_comparison_report(inputs: ReportInputs) -> dict[str, Any]:
    baseline = _read_optional(inputs.baseline, "baseline")
    sweep = _read_optional(inputs.sweep_ranking, "sweep_ranking")
    repeated = _read_optional(inputs.repeated_ranking, "repeated_ranking")
    if sweep is None and repeated is None:
        raise ReportError("at least one ranking input is required")

    missing = [
        name
        for name, path in (
            ("baseline", inputs.baseline),
            ("sweep_ranking", inputs.sweep_ranking),
            ("repeated_ranking", inputs.repeated_ranking),
        )
        if path is None
    ]
    present = {
        name: str(path)
        for name, path in (
            ("baseline", inputs.baseline),
            ("sweep_ranking", inputs.sweep_ranking),
            ("repeated_ranking", inputs.repeated_ranking),
        )
        if path is not None
    }

    candidates: list[dict[str, Any]] = []
    if sweep is not None:
        candidates.extend(extract_candidates(sweep, "sweep"))
    if repeated is not None:
        candidates.extend(extract_candidates(repeated, "repeated"))
    if not candidates:
        raise ReportError("ranking inputs did not contain any ranked candidates")

    recommendation = choose_recommendation(candidates)
    notes = build_notes(baseline, sweep, repeated, candidates, missing)
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "inputs": {
            "present": present,
            "missing": missing,
        },
        "baseline": baseline or {},
        "recommendation": recommendation,
        "candidates": candidates,
        "notes": notes,
    }
    report["markdown"] = render_markdown(report)
    return report


def extract_candidates(ranking: dict[str, Any], source: str) -> list[dict[str, Any]]:
    objectives = ranking.get("objectives", {})
    if not isinstance(objectives, dict):
        return []
    preferred_objectives = ["balanced", "throughput", "latency"]
    snapshots: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for objective in preferred_objectives:
        rows = objectives.get(objective)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            candidate_id = row.get("candidate_id") or row.get("trial_id")
            if not isinstance(candidate_id, str) or not candidate_id:
                continue
            key = (source, candidate_id)
            if key in seen:
                continue
            seen.add(key)
            metrics = row.get("metrics", {})
            if not isinstance(metrics, dict):
                metrics = {}
            snapshots.append(
                {
                    "candidate_id": candidate_id,
                    "source": source,
                    "objective": objective,
                    "rank": row.get("rank"),
                    "score": row.get("score"),
                    "overrides": metrics.get("overrides", {}),
                    "metrics": metrics,
                    "baseline_delta": row.get("baseline_delta", {}),
                    "artifact_paths": row.get("artifact_paths", {}),
                    "stability_note": stability_note(metrics),
                }
            )
    return snapshots


def choose_recommendation(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    preferred = [
        item
        for item in candidates
        if item["source"] == "repeated" and item["objective"] == "balanced" and item.get("rank") == 1
    ]
    if not preferred:
        preferred = [
            item
            for item in candidates
            if item["source"] == "repeated" and item["objective"] == "throughput" and item.get("rank") == 1
        ]
    if not preferred:
        preferred = [item for item in candidates if item.get("rank") == 1]
    if not preferred:
        preferred = candidates
    winner = preferred[0]
    return {
        "candidate_id": winner["candidate_id"],
        "source": winner["source"],
        "objective": winner["objective"],
        "reason": recommendation_reason(winner),
        "tradeoffs": recommendation_tradeoffs(winner),
        "metrics": winner["metrics"],
        "baseline_delta": winner["baseline_delta"],
        "artifact_paths": winner["artifact_paths"],
    }


def recommendation_reason(candidate: dict[str, Any]) -> str:
    metrics = candidate["metrics"]
    tps = _number(metrics.get("aggregate_tokens_per_second"))
    latency = _number(metrics.get("mean_latency_ms"))
    parts = [f"Ranked #1 for {candidate['objective']} from {candidate['source']} artifacts."]
    if tps is not None:
        parts.append(f"Mean throughput is {tps:.3f} tokens/sec.")
    if latency is not None:
        parts.append(f"Mean latency is {latency:.3f} ms.")
    return " ".join(parts)


def recommendation_tradeoffs(candidate: dict[str, Any]) -> str:
    note = candidate.get("stability_note")
    if isinstance(note, str) and note:
        return note
    return "No repeated stability metrics were available for this candidate."


def stability_note(metrics: dict[str, Any]) -> str:
    failure_rate = _number(metrics.get("failure_rate"))
    latency_spread = _number(metrics.get("latency_spread_ms"))
    tps_spread = _number(metrics.get("tokens_per_second_spread"))
    notes = []
    if failure_rate is not None:
        notes.append(f"failure rate {failure_rate:.1%}")
    if latency_spread is not None:
        notes.append(f"latency spread {latency_spread:.3f} ms")
    if tps_spread is not None:
        notes.append(f"throughput spread {tps_spread:.3f} tokens/sec")
    if not notes:
        return ""
    if failure_rate == 0:
        return "Stable repetitions with " + ", ".join(notes) + "."
    return "Repetitions include failures with " + ", ".join(notes) + "."


def build_notes(
    baseline: dict[str, Any] | None,
    sweep: dict[str, Any] | None,
    repeated: dict[str, Any] | None,
    candidates: list[dict[str, Any]],
    missing: list[str],
) -> list[str]:
    notes = []
    if baseline is None:
        notes.append("Baseline summary was not provided.")
    if sweep is None:
        notes.append("One-shot sweep ranking was not provided.")
    if repeated is None:
        notes.append("Repeated sweep ranking was not provided; stability notes may be limited.")
    if missing:
        notes.append("Missing optional inputs: " + ", ".join(missing) + ".")
    repeated_candidates = [item for item in candidates if item["source"] == "repeated"]
    if repeated_candidates:
        notes.append(f"Repeated ranking contributed {len(repeated_candidates)} candidate snapshots.")
    return notes


def render_markdown(report: dict[str, Any]) -> str:
    recommendation = report["recommendation"]
    metrics = recommendation.get("metrics", {})
    deltas = recommendation.get("baseline_delta", {})
    lines = [
        "# vLLM Optimization Report",
        "",
        "## Recommendation",
        "",
        f"- Candidate: `{recommendation['candidate_id']}`",
        f"- Source: `{recommendation['source']}`",
        f"- Objective: `{recommendation['objective']}`",
        f"- Reason: {recommendation['reason']}",
        f"- Trade-offs: {recommendation['tradeoffs']}",
        "",
        "## Metrics",
        "",
    ]
    for label, key in (
        ("Mean latency", "mean_latency_ms"),
        ("Aggregate tokens/sec", "aggregate_tokens_per_second"),
        ("Failure rate", "failure_rate"),
        ("Latency spread", "latency_spread_ms"),
        ("Throughput spread", "tokens_per_second_spread"),
    ):
        value = metrics.get(key)
        if value is not None:
            lines.append(f"- {label}: `{_format_value(value)}`")
    if deltas:
        lines.extend(["", "## Baseline Delta", ""])
        for key, value in deltas.items():
            if isinstance(value, dict):
                absolute = _format_value(value.get("absolute"))
                percent = _format_value(value.get("percent"))
                lines.append(f"- {key}: `{absolute}` ({percent}%)")
    lines.extend(["", "## Candidates", ""])
    for candidate in report["candidates"]:
        candidate_metrics = candidate.get("metrics", {})
        lines.append(
            f"- `{candidate['candidate_id']}` [{candidate['source']}/{candidate['objective']} rank {candidate.get('rank')}]: "
            f"{_format_value(candidate_metrics.get('aggregate_tokens_per_second'))} tok/s, "
            f"{_format_value(candidate_metrics.get('mean_latency_ms'))} ms"
        )
    if report.get("notes"):
        lines.extend(["", "## Notes", ""])
        for note in report["notes"]:
            lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def _read_optional(path: Path | None, label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.exists():
        raise ReportError(f"{label} path does not exist: {path}")
    return read_json(path)


def _number(value: Any) -> float | None:
    return float(value) if isinstance(value, int | float) else None


def _format_value(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.3f}"
    if value is None:
        return "n/a"
    return str(value)
