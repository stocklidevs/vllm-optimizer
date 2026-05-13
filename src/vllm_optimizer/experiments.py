from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import read_json
from .types import (
    Direction,
    ExperimentDefinition,
    ModelConfig,
    Objective,
    ObjectiveFamily,
    Target,
    TieBreaker,
    Workload,
)

OBJECTIVE_FAMILIES: set[str] = {
    "throughput",
    "latency",
    "memory",
    "tool-calling",
    "structured-output",
    "long-context",
    "stability",
    "balanced",
}
DIRECTIONS: set[str] = {"maximize", "minimize"}


class ExperimentValidationError(ValueError):
    """Raised when an experiment definition cannot be planned."""


def load_experiment(path: Path) -> ExperimentDefinition:
    return parse_experiment(read_json(path))


def parse_experiment(data: dict[str, Any]) -> ExperimentDefinition:
    errors: list[str] = []

    experiment_id = _required_str(data, "experiment_id", errors)
    objective_data = _required_dict(data, "objective", errors)
    model_data = _required_dict(data, "model", errors)
    workload_data = _required_dict(data, "workload", errors)
    parameter_data = _required_dict(data, "parameter_space", errors)
    target_data = _required_dict(data, "target", errors)

    family = _required_str(objective_data, "family", errors)
    if family and family not in OBJECTIVE_FAMILIES:
        errors.append(f"objective.family must be one of {sorted(OBJECTIVE_FAMILIES)}")
    primary_metric = _required_str(objective_data, "primary_metric", errors)
    direction = _required_str(objective_data, "direction", errors)
    if direction and direction not in DIRECTIONS:
        errors.append("objective.direction must be maximize or minimize")

    tie_breakers = []
    for index, item in enumerate(objective_data.get("tie_breakers", [])):
        if not isinstance(item, dict):
            errors.append(f"objective.tie_breakers[{index}] must be an object")
            continue
        metric = _required_str(item, "metric", errors, f"objective.tie_breakers[{index}]")
        tie_direction = _required_str(
            item, "direction", errors, f"objective.tie_breakers[{index}]"
        )
        if tie_direction and tie_direction not in DIRECTIONS:
            errors.append(
                f"objective.tie_breakers[{index}].direction must be maximize or minimize"
            )
        if metric and tie_direction:
            tie_breakers.append(TieBreaker(metric=metric, direction=tie_direction))  # type: ignore[arg-type]

    model_id = _required_str(model_data, "id", errors)
    vllm_version = _required_str(model_data, "vllm_version", errors)

    prompt_corpus_id = _required_str(workload_data, "prompt_corpus_id", errors)
    request_mix = _required_str(workload_data, "request_mix", errors)
    concurrency = _required_int_list(workload_data, "concurrency", errors)
    seeds = _required_int_list(workload_data, "seeds", errors)

    if not parameter_data:
        errors.append("parameter_space must include at least one parameter")
    parameter_space: dict[str, tuple[Any, ...]] = {}
    for key, value in sorted(parameter_data.items()):
        if not isinstance(value, list) or not value:
            errors.append(f"parameter_space.{key} must be a non-empty array")
            continue
        parameter_space[str(key)] = tuple(value)

    host_label = _required_str(target_data, "host_label", errors)
    execution_mode = _required_str(target_data, "execution_mode", errors)
    if execution_mode != "dry-run":
        errors.append("target.execution_mode must be dry-run for this feature")

    if errors:
        raise ExperimentValidationError("; ".join(errors))

    return ExperimentDefinition(
        experiment_id=experiment_id,
        objective=Objective(
            family=family,  # type: ignore[arg-type]
            primary_metric=primary_metric,
            direction=direction,  # type: ignore[arg-type]
            constraints=objective_data.get("constraints", {}),
            tie_breakers=tuple(tie_breakers),
        ),
        model=ModelConfig(
            id=model_id,
            vllm_version=vllm_version,
            path_label=model_data.get("path_label"),
            tokenizer=model_data.get("tokenizer"),
        ),
        workload=Workload(
            prompt_corpus_id=prompt_corpus_id,
            request_mix=request_mix,
            concurrency=tuple(concurrency),
            seeds=tuple(seeds),
        ),
        parameter_space=parameter_space,
        target=Target(host_label=host_label, execution_mode="dry-run"),
        metadata=data.get("metadata", {}),
    )


def _required_str(
    data: dict[str, Any], field: str, errors: list[str], prefix: str | None = None
) -> str:
    label = f"{prefix}.{field}" if prefix else field
    value = data.get(field)
    if not isinstance(value, str) or not value:
        errors.append(f"{label} is required")
        return ""
    return value


def _required_dict(data: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = data.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field} is required")
        return {}
    return value


def _required_int_list(data: dict[str, Any], field: str, errors: list[str]) -> list[int]:
    value = data.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"workload.{field} must be a non-empty array")
        return []
    result: list[int] = []
    for index, item in enumerate(value):
        if not isinstance(item, int):
            errors.append(f"workload.{field}[{index}] must be an integer")
        elif item < 1 and field == "concurrency":
            errors.append(f"workload.{field}[{index}] must be >= 1")
        else:
            result.append(item)
    return result
