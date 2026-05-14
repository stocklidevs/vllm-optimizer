from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .artifacts import read_json, write_json
from .serve_profiles import OPTIONAL_FLAG_RULES, parse_serve_profile


class PromotionError(ValueError):
    """Raised when a ranked candidate cannot be promoted safely."""


DEFAULT_OBJECTIVE = "balanced"
DEFAULT_PROFILE_ID = "qwen3-coder-next-awq-recommended"


def build_promotion_preview(
    ranking_path: Path,
    objective: str = DEFAULT_OBJECTIVE,
    profile_id: str = DEFAULT_PROFILE_ID,
) -> dict[str, Any]:
    ranking = read_json(ranking_path)
    selected = select_ranked_candidate(ranking, objective)
    aggregate = find_candidate_aggregate(ranking, selected["candidate_id"])
    source_trials = aggregate.get("source_trials")
    if not isinstance(source_trials, list) or not source_trials:
        raise PromotionError(f"candidate {selected['candidate_id']!r} has no source trials")
    success_count = aggregate.get("success_count")
    if not isinstance(success_count, int) or success_count < 1:
        raise PromotionError(f"candidate {selected['candidate_id']!r} has no successful repetitions")

    source_profile = load_source_profile(source_trials)
    promoted_profile = build_recommended_profile(
        source_profile=source_profile,
        profile_id=profile_id,
        ranking_path=ranking_path,
        objective=objective,
        ranking=ranking,
        selected=selected,
        aggregate=aggregate,
        generated_at=None,
    )
    return {
        "eligible": True,
        "mode": "preview",
        "ranking_path": display_path(ranking_path),
        "objective": objective,
        "sweep_id": ranking.get("sweep_id"),
        "rank": selected.get("rank"),
        "candidate_id": selected["candidate_id"],
        "metrics": selected.get("metrics", {}),
        "baseline_delta": selected.get("baseline_delta", {}),
        "overrides": aggregate.get("overrides", {}),
        "source_trials": compact_source_trials(source_trials),
        "proposed_profile": promoted_profile,
        "provenance": promoted_profile["promotion"],
    }


def write_promoted_profile(
    ranking_path: Path,
    profile_out: Path,
    summary_out: Path,
    objective: str = DEFAULT_OBJECTIVE,
    profile_id: str = DEFAULT_PROFILE_ID,
    force: bool = False,
) -> dict[str, Any]:
    existing = [path for path in (profile_out, summary_out) if path.exists()]
    if existing and not force:
        names = ", ".join(str(path) for path in existing)
        raise PromotionError(f"output path already exists: {names}")

    preview = build_promotion_preview(ranking_path, objective, profile_id)
    profile = {
        **preview["proposed_profile"],
        "promotion": {
            **preview["proposed_profile"]["promotion"],
            "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
    }
    parse_serve_profile(profile)
    summary = render_promotion_summary(preview, profile_out)

    write_json(profile_out, profile)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(summary, encoding="utf-8")
    return {
        "profile_path": str(profile_out),
        "summary_path": str(summary_out),
        "preview": preview,
    }


def select_ranked_candidate(ranking: dict[str, Any], objective: str) -> dict[str, Any]:
    objectives = ranking.get("objectives")
    if not isinstance(objectives, dict) or objective not in objectives:
        raise PromotionError(f"objective {objective!r} is not present in ranking")
    ranked = objectives[objective]
    if not isinstance(ranked, list) or not ranked:
        raise PromotionError(f"objective {objective!r} has no ranked candidates")
    selected = ranked[0]
    if not isinstance(selected, dict) or not isinstance(selected.get("candidate_id"), str):
        raise PromotionError(f"objective {objective!r} top candidate is invalid")
    return selected


def find_candidate_aggregate(ranking: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    aggregates = ranking.get("candidate_aggregates")
    if not isinstance(aggregates, list):
        raise PromotionError("ranking has no candidate aggregates")
    for aggregate in aggregates:
        if isinstance(aggregate, dict) and aggregate.get("candidate_id") == candidate_id:
            return aggregate
    raise PromotionError(f"candidate aggregate {candidate_id!r} is missing")


def load_source_profile(source_trials: list[Any]) -> dict[str, Any]:
    for trial in source_trials:
        if not isinstance(trial, dict) or trial.get("status") != "completed":
            continue
        artifact_paths = trial.get("artifact_paths")
        if not isinstance(artifact_paths, dict):
            continue
        plan_path = artifact_paths.get("plan")
        if not isinstance(plan_path, str):
            continue
        path = Path(plan_path)
        if not path.exists():
            continue
        return profile_from_trial_plan(read_json(path))
    raise PromotionError("no completed source trial plan could be loaded")


def profile_from_trial_plan(plan: dict[str, Any]) -> dict[str, Any]:
    serve_plan = plan.get("serve_plan")
    if not isinstance(serve_plan, dict):
        raise PromotionError("source trial plan has no serve plan")
    command = serve_plan.get("serve_command")
    if not isinstance(command, list) or len(command) < 3:
        raise PromotionError("source trial plan has no serve command")
    return profile_from_serve_command([str(item) for item in command])


def profile_from_serve_command(command: list[str]) -> dict[str, Any]:
    if len(command) < 3 or command[1] != "serve":
        raise PromotionError("serve command is not a vLLM serve command")
    values: dict[str, Any] = {
        "profile_id": "promoted-profile",
        "vllm_executable": command[0],
        "model": command[2],
        "enable_auto_tool_choice": False,
        "optional_flags": {},
    }
    optional_by_cli = {rule["cli"]: name for name, rule in OPTIONAL_FLAG_RULES.items()}
    index = 3
    while index < len(command):
        token = command[index]
        if not token.startswith("--"):
            raise PromotionError(f"unexpected serve command token {token!r}")
        name = token[2:]
        if name == "enable-auto-tool-choice":
            values["enable_auto_tool_choice"] = True
            index += 1
            continue
        if name in optional_by_cli:
            option_name = optional_by_cli[name]
            rule = OPTIONAL_FLAG_RULES[option_name]
            if rule["type"] is bool:
                values["optional_flags"][option_name] = True
                index += 1
            else:
                if index + 1 >= len(command):
                    raise PromotionError(f"missing value for {token}")
                values["optional_flags"][option_name] = int(command[index + 1])
                index += 2
            continue
        if index + 1 >= len(command):
            raise PromotionError(f"missing value for {token}")
        value = command[index + 1]
        key = name.replace("-", "_")
        if key == "port":
            values[key] = int(value)
        elif key == "max_model_len":
            values[key] = int(value)
        elif key == "gpu_memory_utilization":
            values[key] = float(value)
        else:
            values[key] = value
        index += 2
    parse_serve_profile(values)
    return values


def build_recommended_profile(
    source_profile: dict[str, Any],
    profile_id: str,
    ranking_path: Path,
    objective: str,
    ranking: dict[str, Any],
    selected: dict[str, Any],
    aggregate: dict[str, Any],
    generated_at: str | None,
) -> dict[str, Any]:
    profile = dict(source_profile)
    profile["profile_id"] = profile_id
    optional_flags = dict(profile.get("optional_flags", {}))
    overrides = aggregate.get("overrides", {})
    if isinstance(overrides, dict):
        for name, value in overrides.items():
            if name in OPTIONAL_FLAG_RULES:
                optional_flags[name] = value
            elif name in profile:
                profile[name] = value
    profile["optional_flags"] = optional_flags
    profile["promotion"] = {
        "ranking_path": display_path(ranking_path),
        "objective": objective,
        "candidate_id": selected["candidate_id"],
        "rank": selected.get("rank"),
        "sweep_id": ranking.get("sweep_id"),
        "source_trial_ids": [
            trial["trial_id"]
            for trial in compact_source_trials(aggregate.get("source_trials", []))
            if isinstance(trial.get("trial_id"), str)
        ],
        "metrics": selected.get("metrics", {}),
        "baseline_delta": selected.get("baseline_delta", {}),
        "overrides": aggregate.get("overrides", {}),
        "generated_at": generated_at,
    }
    parse_serve_profile(profile)
    return profile


def compact_source_trials(source_trials: Any) -> list[dict[str, Any]]:
    if not isinstance(source_trials, list):
        return []
    compacted = []
    for trial in source_trials:
        if not isinstance(trial, dict):
            continue
        compacted.append(
            {
                "trial_id": trial.get("trial_id"),
                "repetition_index": trial.get("repetition_index", 0),
                "status": trial.get("status"),
                "failure_reason": trial.get("failure_reason"),
            }
        )
    return compacted


def render_promotion_summary(preview: dict[str, Any], profile_out: Path) -> str:
    metrics = preview.get("metrics", {})
    lines = [
        "# Promoted vLLM Profile",
        "",
        f"- Ranking artifact: `{preview['ranking_path']}`",
        f"- Objective: `{preview['objective']}`",
        f"- Candidate: `{preview['candidate_id']}`",
        f"- Rank: `{preview['rank']}`",
        f"- Profile output: `{display_path(profile_out)}`",
        "",
        "## Metrics",
        "",
    ]
    for key in sorted(metrics):
        value = metrics[key]
        if isinstance(value, dict):
            value = json.dumps(value, sort_keys=True)
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Source Trials", ""])
    for trial in preview.get("source_trials", []):
        lines.append(f"- {trial.get('trial_id')} ({trial.get('status')})")
    lines.extend(["", "## Overrides", ""])
    for key, value in sorted(preview.get("overrides", {}).items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def display_path(path: Path) -> str:
    return path.as_posix()
