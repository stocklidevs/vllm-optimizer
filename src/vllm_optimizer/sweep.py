from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from itertools import product
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .artifacts import read_json, read_jsonl, write_json, write_jsonl
from .benchmark import PromptSet, build_benchmark_plan, load_prompt_set, run_baseline_benchmark
from .discovery import DiscoveryTarget
from .serve_profiles import OPTIONAL_FLAG_RULES, ServeProfile, build_serve_plan, load_serve_profile


class SweepError(ValueError):
    """Raised when a sweep definition, plan, or result set is invalid."""


SAFE_PARAMETERS: dict[str, dict[str, Any]] = {
    "max_model_len": {"type": int, "min": 1024, "max": 65536, "risk_tier": "safe-session"},
    "gpu_memory_utilization": {"type": float, "min": 0.5, "max": 0.95, "risk_tier": "safe-session"},
    "performance_mode": {"type": str, "allowed": {"interactivity", "throughput"}, "risk_tier": "safe-session"},
    **{name: rule for name, rule in OPTIONAL_FLAG_RULES.items()},
}
BLOCKED_PARAMETERS = {"download_dir", "model_loader_extra_config", "tokenizer_mode"}

OBJECTIVES = {"throughput", "latency", "balanced", "single_user"}


@dataclass(frozen=True)
class SweepDefinition:
    sweep_id: str
    profile_path: Path
    prompts_path: Path
    parameters: dict[str, tuple[Any, ...]]
    candidates: tuple[dict[str, Any], ...]
    objectives: tuple[str, ...]
    seed: int
    max_trials: int | None
    baseline_summary_path: Path | None
    repetitions: int
    allow_risky_session_flags: bool


def load_sweep_definition(path: Path) -> SweepDefinition:
    data = read_json(path)
    errors: list[str] = []

    sweep_id = data.get("sweep_id")
    if not isinstance(sweep_id, str) or not sweep_id:
        errors.append("sweep_id is required")
        sweep_id = ""

    profile = _required_path(data, "profile", errors)
    prompts = _required_path(data, "prompts", errors)
    baseline_summary = data.get("baseline_summary")
    baseline_summary_path = Path(baseline_summary) if isinstance(baseline_summary, str) and baseline_summary else None

    seed = data.get("seed", 0)
    if not isinstance(seed, int):
        errors.append("seed must be an integer")
        seed = 0

    max_trials = data.get("max_trials")
    if max_trials is not None and (not isinstance(max_trials, int) or max_trials < 1):
        errors.append("max_trials must be a positive integer when provided")
        max_trials = None

    repetitions = data.get("repetitions", 1)
    if not isinstance(repetitions, int) or repetitions < 1:
        errors.append("repetitions must be a positive integer")
        repetitions = 1
    allow_risky_session_flags = data.get("allow_risky_session_flags", False)
    if not isinstance(allow_risky_session_flags, bool):
        errors.append("allow_risky_session_flags must be a boolean")
        allow_risky_session_flags = False

    objectives_raw = data.get("objectives", ["throughput", "latency", "balanced"])
    if not isinstance(objectives_raw, list) or not objectives_raw:
        errors.append("objectives must be a non-empty array")
        objectives_raw = []
    objectives: list[str] = []
    for objective in objectives_raw:
        if not isinstance(objective, str) or objective not in OBJECTIVES:
            errors.append(f"unsupported objective {objective!r}")
            continue
        objectives.append(objective)

    candidate_overrides = _load_candidate_overrides(data.get("candidates"), errors)
    parameters_raw = data.get("parameters")
    if parameters_raw is None:
        parameters_raw = {}
    if not isinstance(parameters_raw, dict):
        errors.append("parameters must be an object when provided")
        parameters_raw = {}
    parameters: dict[str, tuple[Any, ...]] = {}
    for name in sorted(parameters_raw):
        values = parameters_raw[name]
        if name not in SAFE_PARAMETERS:
            if name in BLOCKED_PARAMETERS:
                errors.append(f"parameter {name!r} is blocked for persistent/system safety")
            else:
                errors.append(f"parameter {name!r} is not allowed for session-level sweeps")
            continue
        if not isinstance(values, list) or not values:
            errors.append(f"parameters.{name} must be a non-empty array")
            continue
        parsed_values = []
        for value in values:
            parsed = _validate_parameter_value(name, value, errors)
            if parsed is not None:
                parsed_values.append(parsed)
        if parsed_values:
            parameters[name] = tuple(parsed_values)

    if not objectives:
        errors.append("at least one supported objective is required")
    if not parameters and not candidate_overrides:
        errors.append("at least one safe parameter or explicit candidate is required")
    if errors:
        raise SweepError("; ".join(errors))

    return SweepDefinition(
        sweep_id=sweep_id,
        profile_path=profile,
        prompts_path=prompts,
        parameters=parameters,
        candidates=tuple(candidate_overrides),
        objectives=tuple(objectives),
        seed=seed,
        max_trials=max_trials,
        baseline_summary_path=baseline_summary_path,
        repetitions=repetitions,
        allow_risky_session_flags=allow_risky_session_flags,
    )


def build_sweep_plan(
    definition: SweepDefinition, artifact_root: str = "artifacts/sweeps", allow_risky_session_flags: bool = False
) -> dict[str, Any]:
    profile = load_serve_profile(definition.profile_path)
    prompts = load_prompt_set(definition.prompts_path)
    explicit_candidates = list(definition.candidates)
    parameter_names = sorted({name for candidate in explicit_candidates for name in candidate} or definition.parameters)
    if explicit_candidates:
        candidate_overrides = explicit_candidates
    else:
        candidate_overrides = [
            dict(zip(parameter_names, values, strict=True))
            for values in product(*(definition.parameters[name] for name in parameter_names))
        ]
    if definition.max_trials is not None:
        candidate_overrides = candidate_overrides[: definition.max_trials]
    if not candidate_overrides:
        raise SweepError("sweep produced no trials")
    allow_risky = definition.allow_risky_session_flags or allow_risky_session_flags
    risk_tiers = {name: parameter_risk_tier(name) for name in parameter_names}
    has_risky = any(tier == "risky-session" for tier in risk_tiers.values())

    trials = []
    candidates = []
    for order, overrides in enumerate(candidate_overrides):
        candidate_id = build_candidate_id(definition.sweep_id, order, overrides)
        candidates.append(
            {
                "candidate_id": candidate_id,
                "order": order,
                "overrides": overrides,
                "repetitions": definition.repetitions,
            }
        )
        for repetition_index in range(definition.repetitions):
            trial_profile = apply_profile_overrides(profile, overrides, order, repetition_index)
            trial_id = build_trial_id(definition.sweep_id, order, repetition_index, overrides)
            artifact_dir = f"{artifact_root}/{definition.sweep_id}/{trial_id}"
            classification = "risky-session" if any(parameter_risk_tier(name) == "risky-session" for name in overrides) else "session-mutating"
            trials.append(
                {
                    "trial_id": trial_id,
                    "candidate_id": candidate_id,
                    "candidate_order": order,
                    "repetition_index": repetition_index,
                    "profile": serve_profile_to_dict(trial_profile),
                    "overrides": overrides,
                    "classification": classification,
                    "risk_tiers": {name: parameter_risk_tier(name) for name in overrides},
                    "artifact_dir": artifact_dir,
                    "serve_plan": build_serve_plan(trial_profile),
                    "benchmark_plan": build_benchmark_plan(trial_profile, prompts),
                }
            )

    return {
        "sweep_id": definition.sweep_id,
        "mode": "dry-run",
        "will_execute": False,
        "seed": definition.seed,
        "objectives": list(definition.objectives),
        "profile_path": str(definition.profile_path),
        "prompts_path": str(definition.prompts_path),
        "prompt_set_id": prompts.prompt_set_id,
        "baseline_summary_path": str(definition.baseline_summary_path) if definition.baseline_summary_path else None,
        "candidate_source": "explicit" if explicit_candidates else "cartesian",
        "safe_parameters": sorted(SAFE_PARAMETERS),
        "risk_tiers": risk_tiers,
        "allow_risky_session_flags": allow_risky,
        "has_risky_session_flags": has_risky,
        "repetitions": definition.repetitions,
        "candidate_count": len(candidates),
        "trial_count": len(trials),
        "candidates": candidates,
        "trials": trials,
    }


def build_sweep_preview(plan: dict[str, Any]) -> dict[str, Any]:
    trials = plan.get("trials")
    if not isinstance(trials, list) or not trials:
        raise SweepError("plan.trials must be a non-empty array")

    preview_trials: list[dict[str, Any]] = []
    blocked_reasons: list[dict[str, str]] = []
    for trial in trials:
        trial_id = str(trial.get("trial_id", "unknown"))
        overrides = trial.get("overrides", {})
        classification = trial.get("classification")
        if classification not in {"session-mutating", "risky-session"}:
            blocked_reasons.append(
                {"trial_id": trial_id, "reason": f"unsupported classification {classification!r}"}
            )
        if classification == "risky-session" and not plan.get("allow_risky_session_flags"):
            blocked_reasons.append({"trial_id": trial_id, "reason": "risky-session flags require explicit allowance"})
        if not isinstance(overrides, dict):
            blocked_reasons.append({"trial_id": trial_id, "reason": "overrides must be an object"})
            overrides = {}
        for name, value in overrides.items():
            if name not in SAFE_PARAMETERS:
                blocked_reasons.append({"trial_id": trial_id, "reason": f"unsafe parameter {name!r}"})
                continue
            value_errors: list[str] = []
            _validate_parameter_value(name, value, value_errors)
            for error in value_errors:
                blocked_reasons.append({"trial_id": trial_id, "reason": error})
        preview_trials.append(
            {
                "trial_id": trial_id,
                "candidate_id": trial.get("candidate_id"),
                "repetition_index": trial.get("repetition_index", 0),
                "order": trial.get("candidate_order", trial.get("order")),
                "changed_parameters": overrides,
                "classification": classification,
                "risk_tiers": trial.get("risk_tiers", {}),
                "will_execute": False,
                "artifact_dir": trial.get("artifact_dir"),
                "command_line": trial.get("serve_plan", {}).get("command_line"),
                "metrics": trial.get("benchmark_plan", {}).get("metrics", []),
                "cleanup": "stop vLLM process and verify process exit before next trial",
            }
        )

    return {
        "sweep_id": plan.get("sweep_id"),
        "mode": "dry-run",
        "will_execute": False,
        "trial_count": len(preview_trials),
        "blocked": bool(blocked_reasons),
        "blocked_reasons": blocked_reasons,
        "allow_risky_session_flags": bool(plan.get("allow_risky_session_flags")),
        "trials": preview_trials,
    }


def rank_sweep_results(plan: dict[str, Any], result_rows: list[dict[str, Any]]) -> dict[str, Any]:
    trials = plan.get("trials", [])
    if not isinstance(trials, list) or not trials:
        raise SweepError("plan.trials must be a non-empty array")
    rows_by_trial = {row.get("trial_id"): normalize_trial_result(row) for row in result_rows if row.get("trial_id")}
    trials_by_id = {trial.get("trial_id"): trial for trial in trials if trial.get("trial_id")}
    plan_trial_ids = [trial["trial_id"] for trial in trials if isinstance(trial.get("trial_id"), str)]
    excluded = []
    normalized_rows = []
    for trial_id in plan_trial_ids:
        row = rows_by_trial.get(trial_id)
        if row is None:
            excluded.append({"trial_id": trial_id, "reason": "missing result row"})
            continue
        trial = trials_by_id.get(trial_id, {})
        candidate_id = row.get("candidate_id")
        if candidate_id in (None, trial_id):
            candidate_id = trial.get("candidate_id") or trial_id
        row["candidate_id"] = candidate_id
        row["repetition_index"] = row.get("repetition_index", trial.get("repetition_index", 0))
        normalized_rows.append(row)

    aggregates = aggregate_candidates(plan, normalized_rows)
    rankable = [item for item in aggregates if item["success_count"] > 0]
    for item in aggregates:
        if item["success_count"] == 0:
            excluded.append({"candidate_id": item["candidate_id"], "reason": "no successful repetitions"})

    if not rankable:
        raise SweepError("no rankable sweep trials")

    baseline = load_optional_baseline(plan.get("baseline_summary_path"))
    rankings = {
        objective: rank_for_objective(objective, rankable, baseline)
        for objective in plan.get("objectives", ["throughput", "latency", "balanced"])
        if objective in OBJECTIVES
    }
    return {
        "sweep_id": plan.get("sweep_id"),
        "objectives": rankings,
        "excluded_trials": excluded,
        "candidate_aggregates": aggregates,
        "baseline_summary_path": plan.get("baseline_summary_path"),
        "source_trial_count": len(plan_trial_ids),
        "ranked_trial_count": len(rankable),
        "ranked_candidate_count": len(rankable),
    }


def run_sweep(
    target: DiscoveryTarget,
    plan: dict[str, Any],
    prompt_set: PromptSet,
    out_dir: Path,
    timeout_seconds: int,
    continue_on_failure: bool,
) -> dict[str, Any]:
    results = []
    failures = 0
    for trial in plan.get("trials", []):
        if trial.get("classification") == "risky-session" and not plan.get("allow_risky_session_flags"):
            raise SweepError("risky-session sweep plan requires explicit allowance before execution")
        trial_id = trial["trial_id"]
        profile = parse_profile_from_plan(trial["profile"])
        trial_out = out_dir / trial_id
        try:
            result = run_baseline_benchmark(target, profile, prompt_set, trial_out, timeout_seconds)
            summary = result["summary"]
            status = "completed" if summary.get("failure_count", 1) == 0 else "failed"
            if status != "completed":
                failures += 1
            results.append(
                {
                    "trial_id": trial_id,
                    "candidate_id": trial.get("candidate_id", trial_id),
                    "repetition_index": trial.get("repetition_index", 0),
                    "status": status,
                    "summary": summary,
                    "artifact_paths": result.get("artifact_paths", {}),
                    "failure_reason": None if status == "completed" else "benchmark failure",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive live-run guard
            failures += 1
            results.append(
                {
                    "trial_id": trial_id,
                    "candidate_id": trial.get("candidate_id", trial_id),
                    "repetition_index": trial.get("repetition_index", 0),
                    "status": "failed",
                    "summary": {},
                    "artifact_paths": {},
                    "failure_reason": str(exc),
                }
            )
        if failures and not continue_on_failure:
            break
    write_jsonl(out_dir / "results.jsonl", results)
    ranking = rank_sweep_results(plan, results)
    write_json(out_dir / "ranking.json", ranking)
    return {"results": results, "ranking": ranking, "failure_count": failures}


def load_sweep_results(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return read_jsonl(path)
    data = read_json(path)
    rows = data.get("results", data.get("trials"))
    if not isinstance(rows, list):
        raise SweepError("results file must contain a results or trials array")
    return [row for row in rows if isinstance(row, dict)]


def apply_profile_overrides(
    profile: ServeProfile, overrides: dict[str, Any], order: int, repetition_index: int = 0
) -> ServeProfile:
    values = {
        name: _coerce_profile_value(name, value)
        for name, value in overrides.items()
        if name not in OPTIONAL_FLAG_RULES
    }
    optional_flags = dict(profile.optional_flags)
    for name, value in overrides.items():
        if name in OPTIONAL_FLAG_RULES:
            optional_flags[name] = _coerce_profile_value(name, value)
    return replace(
        profile,
        profile_id=f"{profile.profile_id}-sweep-{order + 1:03d}-r{repetition_index + 1:02d}",
        optional_flags=optional_flags,
        **values,
    )


def build_candidate_id(sweep_id: str, order: int, overrides: dict[str, Any]) -> str:
    material = f"{sweep_id}|candidate|{order}|{sorted(overrides.items())}"
    digest = sha256(material.encode("utf-8")).hexdigest()[:8]
    return f"{sweep_id}-c{order + 1:03d}-{digest}"


def build_trial_id(sweep_id: str, order: int, repetition_index: int, overrides: dict[str, Any]) -> str:
    material = f"{sweep_id}|trial|{order}|{repetition_index}|{sorted(overrides.items())}"
    digest = sha256(material.encode("utf-8")).hexdigest()[:8]
    return f"{sweep_id}-c{order + 1:03d}-r{repetition_index + 1:02d}-{digest}"


def serve_profile_to_dict(profile: ServeProfile) -> dict[str, Any]:
    return asdict(profile)


def parse_profile_from_plan(data: dict[str, Any]) -> ServeProfile:
    return ServeProfile(**{**data, "optional_flags": data.get("optional_flags", {})})


def parameter_risk_tier(name: str) -> str:
    rule = SAFE_PARAMETERS.get(name, {})
    return str(rule.get("risk_tier", "safe-session"))


def normalize_trial_result(row: dict[str, Any]) -> dict[str, Any]:
    summary = row.get("summary")
    if not isinstance(summary, dict):
        summary = {
            "mean_latency_ms": row.get("mean_latency_ms"),
            "aggregate_tokens_per_second": row.get("aggregate_tokens_per_second"),
            "success_count": row.get("success_count"),
            "failure_count": row.get("failure_count", 0),
        }
    status = row.get("status")
    if not isinstance(status, str):
        status = "completed" if summary.get("failure_count", 0) == 0 else "failed"
    return {
        "trial_id": row.get("trial_id"),
        "candidate_id": row.get("candidate_id", row.get("trial_id")),
        "repetition_index": row.get("repetition_index", 0),
        "status": status,
        "summary": summary,
        "artifact_paths": row.get("artifact_paths", row.get("artifact_refs", {})),
        "failure_reason": row.get("failure_reason"),
    }


def aggregate_candidates(plan: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        candidate_id = str(row.get("candidate_id") or row.get("trial_id"))
        rows_by_candidate.setdefault(candidate_id, []).append(row)

    candidates = plan.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        candidates = [
            {
                "candidate_id": trial.get("candidate_id", trial.get("trial_id")),
                "order": trial.get("candidate_order", trial.get("order", 0)),
                "overrides": trial.get("overrides", {}),
            }
            for trial in plan.get("trials", [])
        ]

    aggregates = []
    seen = set()
    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id"))
        if candidate_id in seen:
            continue
        seen.add(candidate_id)
        candidate_rows = rows_by_candidate.get(candidate_id, [])
        successful = [
            row
            for row in candidate_rows
            if row.get("status") == "completed"
            and isinstance(row.get("summary", {}).get("mean_latency_ms"), int | float)
            and isinstance(row.get("summary", {}).get("aggregate_tokens_per_second"), int | float)
        ]
        latencies = [float(row["summary"]["mean_latency_ms"]) for row in successful]
        throughputs = [float(row["summary"]["aggregate_tokens_per_second"]) for row in successful]
        failure_count = len(candidate_rows) - len(successful)
        total_count = len(candidate_rows)
        aggregates.append(
            {
                "candidate_id": candidate_id,
                "order": candidate.get("order"),
                "overrides": candidate.get("overrides", {}),
                "success_count": len(successful),
                "failure_count": failure_count,
                "failure_rate": failure_count / total_count if total_count else 1.0,
                "mean_latency_ms": mean(latencies) if latencies else None,
                "latency_spread_ms": pstdev(latencies) if len(latencies) > 1 else 0.0 if latencies else None,
                "mean_tokens_per_second": mean(throughputs) if throughputs else None,
                "tokens_per_second_spread": pstdev(throughputs) if len(throughputs) > 1 else 0.0 if throughputs else None,
                "source_trials": [
                    {
                        "trial_id": row.get("trial_id"),
                        "repetition_index": row.get("repetition_index", 0),
                        "status": row.get("status"),
                        "artifact_paths": row.get("artifact_paths", {}),
                        "failure_reason": row.get("failure_reason"),
                    }
                    for row in sorted(candidate_rows, key=lambda item: item.get("repetition_index", 0))
                ],
                "artifact_paths": {
                    str(row.get("trial_id")): row.get("artifact_paths", {})
                    for row in candidate_rows
                    if row.get("trial_id")
                },
            }
        )
    return aggregates


def rank_for_objective(
    objective: str, rows: list[dict[str, Any]], baseline: dict[str, Any] | None
) -> list[dict[str, Any]]:
    scored = []
    latencies = [float(_row_latency(row)) for row in rows]
    throughputs = [float(_row_throughput(row)) for row in rows]
    max_latency = max(latencies)
    min_latency = min(latencies)
    max_throughput = max(throughputs)
    min_throughput = min(throughputs)
    for row in rows:
        throughput = float(_row_throughput(row))
        latency = float(_row_latency(row))
        failure_rate = float(row.get("failure_rate", 0.0))
        latency_spread = float(row.get("latency_spread_ms", 0.0) or 0.0)
        throughput_spread = float(row.get("tokens_per_second_spread", 0.0) or 0.0)
        if objective == "throughput":
            score = throughput
            key = (-throughput, failure_rate, throughput_spread, latency, _row_id(row))
        elif objective == "single_user":
            score = latency
            key = (latency, failure_rate, latency_spread, -throughput, throughput_spread, _row_id(row))
        elif objective == "latency":
            score = latency
            key = (latency, failure_rate, latency_spread, -throughput, _row_id(row))
        else:
            throughput_score = _normalize(throughput, min_throughput, max_throughput)
            latency_score = 1 - _normalize(latency, min_latency, max_latency)
            stability_penalty = min(0.2, failure_rate + (latency_spread / max(latency, 1)) * 0.1)
            score = mean([throughput_score, latency_score]) - stability_penalty
            key = (-score, failure_rate, latency_spread, -throughput, _row_id(row))
        scored.append(
            {
                "trial_id": row.get("trial_id"),
                "candidate_id": row.get("candidate_id", row.get("trial_id")),
                "score": score,
                "metrics": ranking_metrics(row),
                "baseline_delta": baseline_delta(ranking_metrics(row), baseline),
                "artifact_paths": row["artifact_paths"],
                "source_trials": row.get("source_trials", []),
                "_key": key,
            }
        )
    ranked = sorted(scored, key=lambda item: item["_key"])
    for index, item in enumerate(ranked, start=1):
        item["rank"] = index
        del item["_key"]
    return ranked


def baseline_delta(summary: dict[str, Any], baseline: dict[str, Any] | None) -> dict[str, Any]:
    if not baseline:
        return {}
    deltas = {}
    for key in ("mean_latency_ms", "aggregate_tokens_per_second"):
        current = summary.get(key)
        base = baseline.get(key)
        if isinstance(current, int | float) and isinstance(base, int | float) and base != 0:
            deltas[key] = {"absolute": current - base, "percent": ((current - base) / base) * 100}
    return deltas


def ranking_metrics(row: dict[str, Any]) -> dict[str, Any]:
    if "summary" in row:
        return row["summary"]
    return {
        "mean_latency_ms": row.get("mean_latency_ms"),
        "aggregate_tokens_per_second": row.get("mean_tokens_per_second"),
        "latency_spread_ms": row.get("latency_spread_ms"),
        "tokens_per_second_spread": row.get("tokens_per_second_spread"),
        "success_count": row.get("success_count"),
        "failure_count": row.get("failure_count"),
        "failure_rate": row.get("failure_rate"),
        "overrides": row.get("overrides"),
    }


def _row_id(row: dict[str, Any]) -> str:
    return str(row.get("candidate_id", row.get("trial_id", "")))


def _row_latency(row: dict[str, Any]) -> float:
    if "summary" in row:
        return float(row["summary"]["mean_latency_ms"])
    return float(row["mean_latency_ms"])


def _row_throughput(row: dict[str, Any]) -> float:
    if "summary" in row:
        return float(row["summary"]["aggregate_tokens_per_second"])
    return float(row["mean_tokens_per_second"])


def load_optional_baseline(path_value: Any) -> dict[str, Any] | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if not path.exists():
        return None
    return read_json(path)


def _normalize(value: float, low: float, high: float) -> float:
    if high == low:
        return 1.0
    return (value - low) / (high - low)


def _required_path(data: dict[str, Any], field: str, errors: list[str]) -> Path:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        errors.append(f"{field} is required")
        return Path(".")
    return Path(value)


def _load_candidate_overrides(value: Any, errors: list[str]) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list) or not value:
        errors.append("candidates must be a non-empty array when provided")
        return []
    candidates: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not item:
            errors.append(f"candidates[{index}] must be a non-empty object")
            continue
        candidate: dict[str, Any] = {}
        for name in sorted(item):
            if name not in SAFE_PARAMETERS:
                if name in BLOCKED_PARAMETERS:
                    errors.append(f"candidate parameter {name!r} is blocked for persistent/system safety")
                else:
                    errors.append(f"candidate parameter {name!r} is not allowed for session-level sweeps")
                continue
            parsed = _validate_parameter_value(name, item[name], errors)
            if parsed is not None:
                candidate[name] = parsed
        if candidate:
            candidates.append(candidate)
    return candidates


def _validate_parameter_value(name: str, value: Any, errors: list[str]) -> Any:
    rule = SAFE_PARAMETERS[name]
    expected = rule["type"]
    if expected is bool:
        if not isinstance(value, bool):
            errors.append(f"parameters.{name} contains value with invalid type")
            return None
        parsed = value
    elif expected is int:
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"parameters.{name} contains value with invalid type")
            return None
        parsed = value
    elif expected is float and isinstance(value, int | float) and not isinstance(value, bool):
        parsed = float(value)
    elif isinstance(value, expected):
        parsed = value
    else:
        errors.append(f"parameters.{name} contains value with invalid type")
        return None
    if "allowed" in rule and parsed not in rule["allowed"]:
        errors.append(f"parameters.{name} contains unsupported value {parsed!r}")
        return None
    if "min" in rule and parsed < rule["min"]:
        errors.append(f"parameters.{name} contains value below safe minimum {rule['min']}")
        return None
    if "max" in rule and parsed > rule["max"]:
        errors.append(f"parameters.{name} contains value above safe maximum {rule['max']}")
        return None
    return parsed


def _coerce_profile_value(name: str, value: Any) -> Any:
    if name == "max_model_len":
        return int(value)
    if name == "gpu_memory_utilization":
        return float(value)
    return value


def objective_exit_code(report: dict[str, Any]) -> int:
    return 0 if report.get("ranked_trial_count", 0) else 2
