from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .artifacts import read_json


class WorkloadReportError(ValueError):
    """Raised when a workload leaderboard report cannot be produced."""


@dataclass(frozen=True)
class WorkloadInput:
    label: str
    ranking_path: Path
    baseline_candidate_order: int | None = 0
    promoted_profile_path: Path | None = None


@dataclass(frozen=True)
class WorkloadReportInputs:
    workloads: tuple[WorkloadInput, ...]


def build_workload_leaderboard_report(inputs: WorkloadReportInputs) -> dict[str, Any]:
    if not inputs.workloads:
        raise WorkloadReportError("at least one workload ranking is required")

    workloads = [build_workload_summary(item) for item in inputs.workloads]
    report = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "workloads": workloads,
        "promoted_profiles": promoted_profiles(workloads),
        "failed_candidate_findings": failed_candidate_findings(workloads),
        "next_actions": next_actions(workloads),
    }
    report["markdown"] = render_workload_markdown(report)
    return report


def build_workload_summary(item: WorkloadInput) -> dict[str, Any]:
    ranking = _read_required(item.ranking_path, "ranking")
    winner = top_balanced(ranking)
    baseline = baseline_candidate(ranking, item.baseline_candidate_order)
    promoted_profile = _read_optional(item.promoted_profile_path)
    return {
        "label": item.label,
        "ranking_path": item.ranking_path.as_posix(),
        "sweep_id": ranking.get("sweep_id"),
        "winner": winner,
        "baseline": baseline,
        "baseline_delta": workload_delta(baseline, winner),
        "ranked_candidate_count": ranking.get("ranked_candidate_count"),
        "source_trial_count": ranking.get("source_trial_count"),
        "failed_candidates": failed_candidates(ranking),
        "promoted_profile": compact_profile(promoted_profile, item.promoted_profile_path),
        "recommendation": workload_recommendation(item.label, winner, baseline, promoted_profile),
    }


def top_balanced(ranking: dict[str, Any]) -> dict[str, Any]:
    objectives = ranking.get("objectives")
    if not isinstance(objectives, dict):
        raise WorkloadReportError("ranking has no objectives")
    rows = objectives.get("balanced")
    if not isinstance(rows, list) or not rows:
        raise WorkloadReportError("ranking has no balanced objective rows")
    row = rows[0]
    if not isinstance(row, dict):
        raise WorkloadReportError("top balanced row is invalid")
    return compact_ranked_candidate(row)


def baseline_candidate(ranking: dict[str, Any], order: int | None) -> dict[str, Any] | None:
    if order is None:
        return None
    aggregates = ranking.get("candidate_aggregates")
    if not isinstance(aggregates, list):
        return None
    for aggregate in aggregates:
        if isinstance(aggregate, dict) and aggregate.get("order") == order:
            return compact_aggregate_candidate(aggregate)
    return None


def failed_candidates(ranking: dict[str, Any]) -> list[dict[str, Any]]:
    aggregates = ranking.get("candidate_aggregates")
    if not isinstance(aggregates, list):
        return []
    failed = []
    for aggregate in aggregates:
        if not isinstance(aggregate, dict):
            continue
        failure_count = aggregate.get("failure_count")
        success_count = aggregate.get("success_count")
        if not isinstance(failure_count, int) or failure_count < 1:
            continue
        source_trials = aggregate.get("source_trials", [])
        failed.append(
            {
                **compact_aggregate_candidate(aggregate),
                "failure_summary": classify_failure(source_trials),
                "failed_trial_count": failure_count,
                "successful_trial_count": success_count,
            }
        )
    return failed


def compact_ranked_candidate(row: dict[str, Any]) -> dict[str, Any]:
    metrics = row.get("metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
    return {
        "candidate_id": row.get("candidate_id"),
        "rank": row.get("rank"),
        "score": row.get("score"),
        "metrics": compact_metrics(metrics),
        "overrides": metrics.get("overrides", {}),
        "source_trials": row.get("source_trials", []),
    }


def compact_aggregate_candidate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": row.get("candidate_id"),
        "order": row.get("order"),
        "metrics": compact_metrics(row),
        "overrides": row.get("overrides", {}),
    }


def compact_metrics(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "mean_latency_ms": row.get("mean_latency_ms"),
        "aggregate_tokens_per_second": row.get("aggregate_tokens_per_second", row.get("mean_tokens_per_second")),
        "failure_count": row.get("failure_count"),
        "failure_rate": row.get("failure_rate"),
        "success_count": row.get("success_count"),
        "latency_spread_ms": row.get("latency_spread_ms"),
        "tokens_per_second_spread": row.get("tokens_per_second_spread"),
    }


def workload_delta(baseline: dict[str, Any] | None, winner: dict[str, Any]) -> dict[str, Any]:
    if baseline is None:
        return {}
    base_metrics = baseline.get("metrics", {})
    winner_metrics = winner.get("metrics", {})
    return {
        "mean_latency_ms": metric_delta(
            base_metrics.get("mean_latency_ms"),
            winner_metrics.get("mean_latency_ms"),
            lower_is_better=True,
        ),
        "aggregate_tokens_per_second": metric_delta(
            base_metrics.get("aggregate_tokens_per_second"),
            winner_metrics.get("aggregate_tokens_per_second"),
            lower_is_better=False,
        ),
    }


def metric_delta(baseline: Any, winner: Any, lower_is_better: bool) -> dict[str, Any]:
    if not isinstance(baseline, int | float) or not isinstance(winner, int | float) or baseline == 0:
        return {"absolute": None, "percent": None, "material": False, "improved": False}
    absolute = winner - baseline
    percent = (absolute / baseline) * 100
    improved = absolute < 0 if lower_is_better else absolute > 0
    return {
        "absolute": absolute,
        "percent": percent,
        "material": abs(percent) > 1.0,
        "improved": improved,
    }


def compact_profile(profile: dict[str, Any] | None, path: Path | None) -> dict[str, Any] | None:
    if profile is None:
        return None
    promotion = profile.get("promotion", {})
    if not isinstance(promotion, dict):
        promotion = {}
    return {
        "path": path.as_posix() if path else None,
        "profile_id": profile.get("profile_id"),
        "gpu_memory_utilization": profile.get("gpu_memory_utilization"),
        "performance_mode": profile.get("performance_mode"),
        "optional_flags": profile.get("optional_flags", {}),
        "source_candidate_id": promotion.get("candidate_id"),
        "confirmation": promotion.get("confirmation", {}),
    }


def workload_recommendation(
    label: str,
    winner: dict[str, Any],
    baseline: dict[str, Any] | None,
    promoted_profile: dict[str, Any] | None,
) -> dict[str, str]:
    deltas = workload_delta(baseline, winner)
    latency = deltas.get("mean_latency_ms", {})
    throughput = deltas.get("aggregate_tokens_per_second", {})
    if promoted_profile is not None:
        return {"status": "promoted", "action": f"Use `{promoted_profile.get('profile_id')}` for {label}."}
    if latency.get("material") and latency.get("improved") and throughput.get("material") and throughput.get("improved"):
        return {"status": "confirm", "action": f"Run repeated A/B confirmation for `{winner.get('candidate_id')}`."}
    if latency.get("improved") or throughput.get("improved"):
        return {"status": "watch", "action": "Keep as workload-specific evidence; do not promote yet."}
    return {"status": "keep-default", "action": "Keep the existing profile for this workload."}


def promoted_profiles(workloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [workload["promoted_profile"] for workload in workloads if workload.get("promoted_profile")]


def failed_candidate_findings(workloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings = []
    for workload in workloads:
        for candidate in workload["failed_candidates"]:
            findings.append(
                {
                    "workload": workload["label"],
                    "candidate_id": candidate["candidate_id"],
                    "overrides": candidate["overrides"],
                    "failure_summary": candidate["failure_summary"],
                }
            )
    return findings


def next_actions(workloads: list[dict[str, Any]]) -> list[str]:
    actions = [workload["recommendation"]["action"] for workload in workloads]
    if any(is_ninja_failure(item["failure_summary"]) for item in failed_candidate_findings(workloads)):
        actions.append("Install or expose `ninja` on the GX10 before rerunning FP8 KV cache candidates.")
    actions.append("Use the leaderboard after each live sweep batch before promoting new defaults.")
    return dedupe(actions)


def classify_failure(source_trials: Any) -> str:
    texts = []
    if isinstance(source_trials, list):
        for trial in source_trials:
            if not isinstance(trial, dict):
                continue
            reason = trial.get("failure_reason")
            if isinstance(reason, str):
                texts.append(reason)
            artifact_paths = trial.get("artifact_paths", {})
            if isinstance(artifact_paths, dict):
                server_log = artifact_paths.get("server_log")
                if isinstance(server_log, str):
                    texts.append(_safe_read_text(Path(server_log)))
    joined = "\n".join(texts)
    if "fp8_e5m2 kv-cache is not supported with fp8 checkpoints" in joined:
        return "`fp8_e5m2` KV cache is unsupported for this FP8 checkpoint."
    if "No such file or directory: 'ninja'" in joined or "ninja" in joined:
        return "vLLM/FlashInfer JIT failed because `ninja` is missing on the GX10."
    if "benchmark failure" in joined:
        return "Benchmark failed before producing successful requests."
    return "Candidate had failed repetitions; inspect source trial logs."


def is_ninja_failure(text: str) -> bool:
    return "ninja" in text.lower()


def render_workload_markdown(report: dict[str, Any]) -> str:
    lines = ["# Workload Leaderboard", "", "## Winners", ""]
    for workload in report["workloads"]:
        winner = workload["winner"]
        metrics = winner["metrics"]
        deltas = workload.get("baseline_delta", {})
        latency_delta = deltas.get("mean_latency_ms", {})
        throughput_delta = deltas.get("aggregate_tokens_per_second", {})
        lines.extend(
            [
                f"### {workload['label']}",
                "",
                f"- Sweep: `{workload['sweep_id']}`",
                f"- Winner: `{winner['candidate_id']}`",
                f"- Mean latency: `{_fmt(metrics.get('mean_latency_ms'))} ms`",
                f"- Throughput: `{_fmt(metrics.get('aggregate_tokens_per_second'))} tokens/sec`",
                f"- Failure rate: `{_fmt_pct(metrics.get('failure_rate'))}`",
                f"- Baseline latency delta: `{_fmt(latency_delta.get('absolute'))} ms` ({_fmt_pct(latency_delta.get('percent'), already_percent=True)})",
                f"- Baseline throughput delta: `{_fmt(throughput_delta.get('absolute'))} tokens/sec` ({_fmt_pct(throughput_delta.get('percent'), already_percent=True)})",
                f"- Recommendation: {workload['recommendation']['action']}",
                "",
                "Overrides:",
                "",
            ]
        )
        for name, value in sorted((winner.get("overrides") or {}).items()):
            lines.append(f"- {name}: `{value}`")
        lines.append("")
    if report["promoted_profiles"]:
        lines.extend(["## Promoted Profiles", ""])
        for profile in report["promoted_profiles"]:
            lines.append(f"- `{profile['profile_id']}`: `{profile['path']}`")
        lines.append("")
    if report["failed_candidate_findings"]:
        lines.extend(["## Failed Candidate Findings", ""])
        for finding in report["failed_candidate_findings"]:
            lines.append(
                f"- `{finding['candidate_id']}` in {finding['workload']}: {finding['failure_summary']}"
            )
        lines.append("")
    lines.extend(["## Next Actions", ""])
    for action in report["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _read_required(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise WorkloadReportError(f"{label} path does not exist: {path}")
    return read_json(path)


def _read_optional(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return _read_required(path, "profile")


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _fmt(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.3f}"
    return "n/a"


def _fmt_pct(value: Any, already_percent: bool = False) -> str:
    if not isinstance(value, int | float):
        return "n/a"
    return f"{value:.3f}%" if already_percent else f"{value:.3%}"
