from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

SUPPORTED_FAMILIES = {"throughput", "latency"}


def rank_results(plan: dict[str, Any], result_rows: list[dict[str, Any]]) -> dict[str, Any]:
    objective = plan["objective"]
    family = objective["family"]
    if family not in SUPPORTED_FAMILIES:
        raise ValueError(f"ranking for objective family {family!r} is not implemented")

    metric = objective["primary_metric"]
    direction = objective["direction"]
    tie_breakers = objective.get("tie_breakers", [])
    plan_trial_ids = {trial["trial_id"] for trial in plan.get("trials", [])}
    rows_by_trial = {row.get("trial_id"): row for row in result_rows if row.get("trial_id")}

    ranked_candidates: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []

    for trial_id in sorted(plan_trial_ids):
        row = rows_by_trial.get(trial_id)
        if row is None:
            excluded.append({"trial_id": trial_id, "reason": "missing result row"})
            continue
        if not isinstance(row.get(metric), int | float):
            excluded.append({"trial_id": trial_id, "reason": f"missing metric {metric}"})
            continue
        ranked_candidates.append(
            {
                "trial_id": trial_id,
                "primary_metric": metric,
                "primary_value": row[metric],
                "metrics": {key: value for key, value in row.items() if key != "trial_id"},
                "artifact_refs": row.get("artifact_refs", []),
            }
        )

    unknown_ids = sorted(set(rows_by_trial) - plan_trial_ids)
    for trial_id in unknown_ids:
        excluded.append({"trial_id": str(trial_id), "reason": "trial not found in plan"})

    ranked = sorted(
        ranked_candidates,
        key=lambda item: ranking_key(item, direction, tie_breakers),
    )
    for index, item in enumerate(ranked, start=1):
        item["rank"] = index

    return {
        "experiment_id": plan["experiment_id"],
        "generated_at": datetime.now(UTC).isoformat(),
        "objective": objective,
        "ranked_trials": ranked,
        "excluded_trials": excluded,
        "artifact_refs": sorted(
            {
                ref
                for item in ranked
                for ref in item.get("artifact_refs", [])
                if isinstance(ref, str)
            }
        ),
    }


def ranking_key(
    item: dict[str, Any], direction: str, tie_breakers: list[dict[str, str]]
) -> tuple[Any, ...]:
    primary = item["primary_value"]
    values: list[Any] = [_sort_value(primary, direction)]
    for tie_breaker in tie_breakers:
        metric = tie_breaker["metric"]
        tie_value = item["metrics"].get(metric)
        values.append(_sort_value(tie_value, tie_breaker["direction"]))
    values.append(item["trial_id"])
    return tuple(values)


def _sort_value(value: Any, direction: str) -> Any:
    if not isinstance(value, int | float):
        return float("inf")
    return -value if direction == "maximize" else value
