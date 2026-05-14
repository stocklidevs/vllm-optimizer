from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .artifacts import read_json
from .serve_profiles import parse_serve_profile


class DefaultReportError(ValueError):
    """Raised when a recommended-profile default report cannot be produced."""


NOISE_PERCENT = 1.0


@dataclass(frozen=True)
class DefaultReportInputs:
    baseline: Path
    recommended: Path
    profile: Path
    source_ranking: Path | None = None


def build_default_decision_report(inputs: DefaultReportInputs) -> dict[str, Any]:
    baseline = _read_required(inputs.baseline, "baseline")
    recommended = _read_required(inputs.recommended, "recommended")
    profile = _read_required(inputs.profile, "profile")
    parse_serve_profile(profile)
    source_ranking = _read_optional(inputs.source_ranking, "source_ranking")

    deltas = {
        "mean_latency_ms": metric_delta(
            _required_number(baseline, "baseline.mean_latency_ms"),
            _required_number(recommended, "recommended.mean_latency_ms"),
            lower_is_better=True,
        ),
        "aggregate_tokens_per_second": metric_delta(
            _required_number(baseline, "baseline.aggregate_tokens_per_second"),
            _required_number(recommended, "recommended.aggregate_tokens_per_second"),
            lower_is_better=False,
        ),
    }
    decision = decide_default_status(recommended, deltas)
    provenance = build_provenance(profile, inputs.profile, inputs.source_ranking, source_ranking)
    report = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "decision": decision,
        "inputs": {
            "baseline": inputs.baseline.as_posix(),
            "recommended": inputs.recommended.as_posix(),
            "profile": inputs.profile.as_posix(),
            "source_ranking": inputs.source_ranking.as_posix() if inputs.source_ranking else None,
        },
        "baseline": baseline,
        "recommended": recommended,
        "deltas": deltas,
        "provenance": provenance,
    }
    report["markdown"] = render_default_markdown(report)
    return report


def metric_delta(baseline: float, recommended: float, lower_is_better: bool) -> dict[str, Any]:
    absolute = recommended - baseline
    percent = (absolute / baseline) * 100 if baseline else None
    improved = absolute <= 0 if lower_is_better else absolute >= 0
    return {
        "baseline": baseline,
        "recommended": recommended,
        "absolute": absolute,
        "percent": percent,
        "improved": improved,
        "materially_worse": is_materially_worse(percent, lower_is_better),
    }


def decide_default_status(recommended: dict[str, Any], deltas: dict[str, dict[str, Any]]) -> dict[str, str]:
    failures = recommended.get("failure_count")
    successes = recommended.get("success_count")
    if not isinstance(successes, int) or successes < 1:
        return {"status": "reject", "reason": "recommended benchmark has no successful prompts"}
    if isinstance(failures, int) and failures > 0:
        return {"status": "reject", "reason": "recommended benchmark has prompt failures"}
    latency_improved = bool(deltas["mean_latency_ms"]["improved"])
    throughput_improved = bool(deltas["aggregate_tokens_per_second"]["improved"])
    latency_worse = bool(deltas["mean_latency_ms"].get("materially_worse", False))
    throughput_worse = bool(deltas["aggregate_tokens_per_second"].get("materially_worse", False))
    if latency_improved and throughput_improved:
        return {"status": "keep", "reason": "recommended profile is not worse than baseline on latency or throughput"}
    if latency_worse and throughput_worse:
        return {"status": "reject", "reason": "recommended profile is worse than baseline on latency and throughput"}
    return {
        "status": "inconclusive",
        "reason": "recommended profile is mixed or within the 1% noise band",
    }


def is_materially_worse(percent: float | None, lower_is_better: bool) -> bool:
    if percent is None:
        return False
    return percent > NOISE_PERCENT if lower_is_better else percent < -NOISE_PERCENT


def build_provenance(
    profile: dict[str, Any],
    profile_path: Path,
    source_ranking_path: Path | None,
    source_ranking: dict[str, Any] | None,
) -> dict[str, Any]:
    promotion = profile.get("promotion", {})
    if not isinstance(promotion, dict):
        promotion = {}
    candidate_id = promotion.get("candidate_id")
    source_rank = None
    if source_ranking is not None and isinstance(candidate_id, str):
        source_rank = find_source_rank(source_ranking, candidate_id)
    return {
        "profile_path": profile_path.as_posix(),
        "profile_id": profile.get("profile_id"),
        "candidate_id": candidate_id,
        "source_sweep_id": promotion.get("sweep_id"),
        "source_trial_ids": promotion.get("source_trial_ids", []),
        "promotion_objective": promotion.get("objective"),
        "promotion_ranking_path": promotion.get("ranking_path"),
        "source_ranking_path": source_ranking_path.as_posix() if source_ranking_path else None,
        "source_rank": source_rank,
    }


def find_source_rank(source_ranking: dict[str, Any], candidate_id: str) -> dict[str, Any] | None:
    objectives = source_ranking.get("objectives", {})
    if not isinstance(objectives, dict):
        return None
    for objective, rows in objectives.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict) and row.get("candidate_id") == candidate_id:
                return {"objective": objective, "rank": row.get("rank"), "metrics": row.get("metrics", {})}
    return None


def render_default_markdown(report: dict[str, Any]) -> str:
    decision = report["decision"]
    provenance = report["provenance"]
    deltas = report["deltas"]
    lines = [
        "# Recommended Profile Default Decision",
        "",
        f"- Decision: `{decision['status']}`",
        f"- Reason: {decision['reason']}",
        f"- Profile: `{provenance.get('profile_id')}`",
        f"- Candidate: `{provenance.get('candidate_id')}`",
        f"- Source sweep: `{provenance.get('source_sweep_id')}`",
        "",
        "## Metric Deltas",
        "",
    ]
    for key, label in (
        ("mean_latency_ms", "Mean latency"),
        ("aggregate_tokens_per_second", "Aggregate tokens/sec"),
    ):
        delta = deltas[key]
        percent = delta.get("percent")
        percent_text = "n/a" if percent is None else f"{percent:.3f}%"
        lines.append(
            f"- {label}: baseline `{delta['baseline']:.3f}`, recommended `{delta['recommended']:.3f}`, "
            f"delta `{delta['absolute']:.3f}` ({percent_text})"
        )
    lines.extend(["", "## Provenance", ""])
    for key in (
        "profile_path",
        "promotion_objective",
        "promotion_ranking_path",
        "source_ranking_path",
    ):
        value = provenance.get(key)
        if value:
            lines.append(f"- {key}: `{value}`")
    trial_ids = provenance.get("source_trial_ids", [])
    if trial_ids:
        lines.append("- source_trial_ids: " + ", ".join(f"`{trial_id}`" for trial_id in trial_ids))
    lines.append("")
    return "\n".join(lines)


def _read_required(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise DefaultReportError(f"{label} path does not exist: {path}")
    return read_json(path)


def _read_optional(path: Path | None, label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    return _read_required(path, label)


def _required_number(data: dict[str, Any], label: str) -> float:
    key = label.rsplit(".", 1)[1]
    value = data.get(key)
    if not isinstance(value, int | float):
        raise DefaultReportError(f"{label} must be numeric")
    return float(value)
