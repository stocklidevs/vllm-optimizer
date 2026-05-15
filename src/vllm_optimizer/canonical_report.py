from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .artifacts import read_json


SCHEMA_VERSION = "1.0"
SUPPORTED_FAMILIES = {"sweep", "session-tuning-sweep"}


class CanonicalReportError(ValueError):
    """Raised when a canonical report cannot be generated."""


@dataclass(frozen=True)
class CanonicalReportInputs:
    family: str
    label: str
    ranking_path: Path
    plan_path: Path | None = None
    results_path: Path | None = None
    summary_path: Path | None = None
    baseline_candidate_order: int | None = 0


def build_canonical_report(inputs: CanonicalReportInputs) -> dict[str, Any]:
    if inputs.family not in SUPPORTED_FAMILIES:
        raise CanonicalReportError(f"unsupported report family: {inputs.family}")
    ranking = _read_required(inputs.ranking_path, "ranking")
    summary = _read_optional(inputs.summary_path, "summary")
    candidates = build_candidates(ranking, inputs.baseline_candidate_order)
    if not any(candidate["objectives"] for candidate in candidates.values()):
        raise CanonicalReportError("no rankable candidates in ranking artifact")

    objectives = build_objectives(ranking, candidates)
    recommendation = build_recommendation(objectives, candidates)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": {
            "family": inputs.family,
            "label": inputs.label,
            "sweep_id": ranking.get("sweep_id"),
            "action_scope": "local-only",
            "summary": compact_summary(summary),
        },
        "recommendation": recommendation,
        "objectives": objectives,
        "candidates": candidates,
        "chart_datasets": build_chart_datasets(objectives, candidates),
        "provenance": {
            "plan_path": _path_string(inputs.plan_path),
            "ranking_path": inputs.ranking_path.as_posix(),
            "results_path": _path_string(inputs.results_path),
            "summary_path": _path_string(inputs.summary_path),
        },
    }
    report["markdown"] = render_markdown(report)
    return report


def build_candidates(ranking: dict[str, Any], baseline_order: int | None) -> dict[str, dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for aggregate in _list_of_dicts(ranking.get("candidate_aggregates")):
        candidate_id = aggregate.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            continue
        metrics = compact_metrics(aggregate)
        failure_count = _number(metrics.get("failure_count")) or 0
        order = aggregate.get("order")
        candidates[candidate_id] = {
            "candidate_id": candidate_id,
            "label": candidate_id,
            "order": order,
            "is_baseline": baseline_order is not None and order == baseline_order,
            "recommendable": failure_count == 0,
            "exclusion_reason": None if failure_count == 0 else "candidate has failed trials",
            "metrics": metrics,
            "objectives": {},
            "artifact_paths": aggregate.get("artifact_paths", {}),
            "source_trials": aggregate.get("source_trials", []),
        }

    objectives = ranking.get("objectives")
    if isinstance(objectives, dict):
        for objective_name, rows in objectives.items():
            if not isinstance(objective_name, str):
                continue
            for row in _list_of_dicts(rows):
                candidate_id = row.get("candidate_id") or row.get("trial_id")
                if not isinstance(candidate_id, str) or not candidate_id:
                    continue
                candidate = candidates.setdefault(
                    candidate_id,
                    {
                        "candidate_id": candidate_id,
                        "label": candidate_id,
                        "order": None,
                        "is_baseline": False,
                        "recommendable": True,
                        "exclusion_reason": None,
                        "metrics": compact_metrics(row.get("metrics", {})),
                        "objectives": {},
                        "artifact_paths": row.get("artifact_paths", {}),
                        "source_trials": row.get("source_trials", []),
                    },
                )
                candidate["objectives"][objective_name] = {
                    "rank": row.get("rank"),
                    "score": row.get("score"),
                }
                if not candidate.get("artifact_paths") and isinstance(row.get("artifact_paths"), dict):
                    candidate["artifact_paths"] = row["artifact_paths"]
                if not any(value is not None for value in candidate["metrics"].values()):
                    candidate["metrics"] = compact_metrics(row.get("metrics", {}))

    return dict(sorted(candidates.items(), key=lambda item: candidate_sort_key(item[1])))


def build_objectives(
    ranking: dict[str, Any],
    candidates: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    objectives: dict[str, dict[str, Any]] = {}
    raw_objectives = ranking.get("objectives", {})
    if not isinstance(raw_objectives, dict):
        return objectives
    for objective_name in sorted(raw_objectives):
        rows = []
        for row in _list_of_dicts(raw_objectives.get(objective_name)):
            candidate_id = row.get("candidate_id") or row.get("trial_id")
            if not isinstance(candidate_id, str) or candidate_id not in candidates:
                continue
            metrics = row.get("metrics", {})
            if not isinstance(metrics, dict):
                metrics = {}
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "rank": row.get("rank"),
                    "score": row.get("score"),
                    "recommendable": candidates[candidate_id]["recommendable"],
                    "is_baseline": candidates[candidate_id]["is_baseline"],
                    "metrics": compact_metrics(metrics),
                }
            )
        rows.sort(key=lambda item: (_rank_sort(item.get("rank")), str(item["candidate_id"])))
        objectives[objective_name] = {
            "winner_candidate_id": rows[0]["candidate_id"] if rows else None,
            "ranked_candidate_count": len(rows),
            "rows": rows,
        }
    return objectives


def build_recommendation(
    objectives: dict[str, dict[str, Any]],
    candidates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    winner = preferred_winner(objectives, candidates)
    if winner is None:
        return {
            "status": "no-recommendation",
            "candidate_id": None,
            "objective": None,
            "summary": "No recommendation is possible because the report has no rankable candidates.",
            "rationale": [],
            "next_actions": ["Inspect source ranking artifacts before rerunning report generation."],
        }

    objective, candidate = winner
    metrics = candidate["metrics"]
    if candidate["is_baseline"]:
        status = "keep-baseline"
        summary = f"Keep baseline `{candidate['candidate_id']}` for `{objective}`."
        next_actions = ["Do not promote a tuned profile from this report.", "Use this report as baseline evidence for future sweeps."]
    else:
        status = "requires-confirmation"
        summary = f"Candidate `{candidate['candidate_id']}` leads `{objective}` and requires repeated confirmation before promotion."
        next_actions = ["Run repeated A/B confirmation before promotion.", "Keep existing profile until confirmation succeeds."]
    return {
        "status": status,
        "candidate_id": candidate["candidate_id"],
        "objective": objective,
        "summary": summary,
        "rationale": recommendation_rationale(candidate, metrics),
        "next_actions": next_actions,
    }


def preferred_winner(
    objectives: dict[str, dict[str, Any]],
    candidates: dict[str, dict[str, Any]],
) -> tuple[str, dict[str, Any]] | None:
    objective_order = ["balanced", "throughput", "latency", *sorted(objectives)]
    seen: set[str] = set()
    for objective in objective_order:
        if objective in seen:
            continue
        seen.add(objective)
        rows = objectives.get(objective, {}).get("rows", [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            candidate = candidates.get(row.get("candidate_id"))
            if candidate and candidate["recommendable"]:
                return objective, candidate
    return None


def recommendation_rationale(candidate: dict[str, Any], metrics: dict[str, Any]) -> list[str]:
    rationale = []
    tps = metrics.get("aggregate_tokens_per_second")
    latency = metrics.get("mean_latency_ms")
    failure_rate = metrics.get("failure_rate")
    if isinstance(tps, int | float):
        rationale.append(f"Throughput: {tps:.3f} tokens/sec.")
    if isinstance(latency, int | float):
        rationale.append(f"Mean latency: {latency:.3f} ms.")
    if isinstance(failure_rate, int | float):
        rationale.append(f"Failure rate: {failure_rate:.3%}.")
    if candidate["is_baseline"]:
        rationale.append("Top ranked candidate is the configured baseline/current behavior.")
    return rationale


def build_chart_datasets(
    objectives: dict[str, dict[str, Any]],
    candidates: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    ranking_rows = []
    for objective_name in sorted(objectives):
        for row in objectives[objective_name]["rows"]:
            metrics = row.get("metrics", {})
            ranking_rows.append(
                {
                    "objective": objective_name,
                    "candidate_id": row["candidate_id"],
                    "rank": row.get("rank"),
                    "score": row.get("score"),
                    "tokens_per_second": metrics.get("aggregate_tokens_per_second"),
                    "mean_latency_ms": metrics.get("mean_latency_ms"),
                    "failure_rate": metrics.get("failure_rate"),
                    "is_baseline": row.get("is_baseline"),
                    "recommendable": row.get("recommendable"),
                }
            )
    metric_rows = []
    for candidate in candidates.values():
        metrics = candidate.get("metrics", {})
        metric_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "tokens_per_second": metrics.get("aggregate_tokens_per_second"),
                "mean_latency_ms": metrics.get("mean_latency_ms"),
                "tokens_per_second_spread": metrics.get("tokens_per_second_spread"),
                "latency_spread_ms": metrics.get("latency_spread_ms"),
                "failure_rate": metrics.get("failure_rate"),
                "is_baseline": candidate.get("is_baseline"),
                "recommendable": candidate.get("recommendable"),
            }
        )
    return {
        "candidate_ranking": {
            "kind": "ranking",
            "x": "rank",
            "y": "score",
            "rows": ranking_rows,
        },
        "metric_summary": {
            "kind": "scatter",
            "x": "mean_latency_ms",
            "y": "tokens_per_second",
            "rows": metric_rows,
        },
        "failure_summary": {
            "kind": "bar",
            "x": "candidate_id",
            "y": "failure_rate",
            "rows": metric_rows,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    recommendation = report["recommendation"]
    lines = [
        "# Canonical vLLM Optimization Report",
        "",
        "## Recommendation",
        "",
        f"- Status: `{recommendation['status']}`",
        f"- Candidate: `{recommendation.get('candidate_id') or 'n/a'}`",
        f"- Objective: `{recommendation.get('objective') or 'n/a'}`",
        f"- Summary: {recommendation['summary']}",
        "",
        "## Rationale",
        "",
    ]
    for item in recommendation.get("rationale", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Candidates", ""])
    for candidate in report["candidates"].values():
        metrics = candidate.get("metrics", {})
        lines.append(
            f"- `{candidate['candidate_id']}`: {_fmt(metrics.get('aggregate_tokens_per_second'))} tok/s, "
            f"{_fmt(metrics.get('mean_latency_ms'))} ms, failure rate {_fmt_pct(metrics.get('failure_rate'))}"
        )
    lines.extend(["", "## Next Actions", ""])
    for action in recommendation.get("next_actions", []):
        lines.append(f"- {action}")
    lines.extend(["", "## Provenance", ""])
    for key, value in report["provenance"].items():
        if value is not None:
            lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def compact_summary(summary: dict[str, Any] | None) -> dict[str, Any]:
    if summary is None:
        return {}
    return {
        key: summary.get(key)
        for key in ("trial_count", "success_count", "failure_count", "sweep_id")
        if key in summary
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


def candidate_sort_key(candidate: dict[str, Any]) -> tuple[int, int, str]:
    order = candidate.get("order")
    return (0 if isinstance(order, int) else 1, int(order) if isinstance(order, int) else 0, str(candidate["candidate_id"]))


def _read_required(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise CanonicalReportError(f"{label} path does not exist: {path}")
    try:
        return read_json(path)
    except ValueError as exc:
        raise CanonicalReportError(str(exc)) from exc


def _read_optional(path: Path | None, label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    return _read_required(path, label)


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _number(value: Any) -> float | None:
    return float(value) if isinstance(value, int | float) else None


def _rank_sort(value: Any) -> int:
    return int(value) if isinstance(value, int) else 999_999


def _path_string(path: Path | None) -> str | None:
    return path.as_posix() if path else None


def _fmt(value: Any) -> str:
    return f"{value:.3f}" if isinstance(value, int | float) else "n/a"


def _fmt_pct(value: Any) -> str:
    return f"{value:.3%}" if isinstance(value, int | float) else "n/a"
