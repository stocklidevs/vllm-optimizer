from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from .artifacts import read_json, write_json
from .benchmark import build_benchmark_plan, load_prompt_set
from .serve_profiles import load_serve_profile
from .session_tuning import build_session_tuning_preview, load_session_tuning_profile


class SessionTuningSweepError(ValueError):
    """Raised when a session tuning sweep cannot be planned safely."""


@dataclass(frozen=True)
class SessionTuningSweepDefinition:
    sweep_id: str
    profile_path: Path
    prompts_path: Path
    candidate_paths: tuple[Path, ...]
    seed: int
    repetitions: int


def load_session_tuning_sweep_definition(path: Path) -> SessionTuningSweepDefinition:
    data = read_json(path)
    errors: list[str] = []
    sweep_id = data.get("sweep_id")
    if not isinstance(sweep_id, str) or not sweep_id:
        errors.append("sweep_id is required")
        sweep_id = ""
    profile_path = required_path(data, "profile", errors)
    prompts_path = required_path(data, "prompts", errors)
    seed = data.get("seed", 0)
    if not isinstance(seed, int):
        errors.append("seed must be an integer")
        seed = 0
    repetitions = data.get("repetitions", 1)
    if not isinstance(repetitions, int) or repetitions < 1:
        errors.append("repetitions must be a positive integer")
        repetitions = 1
    candidates = data.get("candidates")
    candidate_paths: list[Path] = []
    if not isinstance(candidates, list) or not candidates:
        errors.append("candidates must be a non-empty array")
    else:
        for index, item in enumerate(candidates):
            if not isinstance(item, str) or not item:
                errors.append(f"candidates[{index}] must be a path string")
                continue
            candidate_paths.append(Path(item))
    if errors:
        raise SessionTuningSweepError("; ".join(errors))
    return SessionTuningSweepDefinition(
        sweep_id=sweep_id,
        profile_path=profile_path,
        prompts_path=prompts_path,
        candidate_paths=tuple(candidate_paths),
        seed=seed,
        repetitions=repetitions,
    )


def required_path(data: dict[str, Any], key: str, errors: list[str]) -> Path:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        errors.append(f"{key} is required")
        return Path()
    return Path(value)


def build_session_tuning_sweep_plan(definition: SessionTuningSweepDefinition) -> dict[str, Any]:
    profile = load_serve_profile(definition.profile_path)
    prompts = load_prompt_set(definition.prompts_path)
    candidates = []
    trials = []
    for order, path in enumerate(definition.candidate_paths):
        tuning = load_session_tuning_profile(path)
        preview = build_session_tuning_preview(tuning)
        candidate_id = build_candidate_id(definition.sweep_id, order, tuning.profile_id)
        candidates.append(
            {
                "candidate_id": candidate_id,
                "order": order,
                "session_tuning_profile_id": tuning.profile_id,
                "session_tuning_path": path.as_posix(),
                "repetitions": definition.repetitions,
                "actions": preview["actions"],
            }
        )
        for repetition_index in range(definition.repetitions):
            trial_id = build_trial_id(definition.sweep_id, order, repetition_index, tuning.profile_id)
            trials.append(
                {
                    "trial_id": trial_id,
                    "candidate_id": candidate_id,
                    "candidate_order": order,
                    "repetition_index": repetition_index,
                    "classification": "session-mutating",
                    "session_tuning_path": path.as_posix(),
                    "session_tuning": preview,
                    "benchmark_plan": build_benchmark_plan(profile, prompts, tuning),
                    "artifact_dir": f"artifacts/session-tuning-sweeps/{definition.sweep_id}/{trial_id}",
                }
            )
    return {
        "sweep_id": definition.sweep_id,
        "mode": "dry-run",
        "will_execute": False,
        "seed": definition.seed,
        "profile_path": definition.profile_path.as_posix(),
        "prompts_path": definition.prompts_path.as_posix(),
        "prompt_set_id": prompts.prompt_set_id,
        "repetitions": definition.repetitions,
        "candidate_count": len(candidates),
        "trial_count": len(trials),
        "candidates": candidates,
        "trials": trials,
    }


def build_session_tuning_sweep_preview(plan: dict[str, Any]) -> dict[str, Any]:
    trials = plan.get("trials")
    if not isinstance(trials, list) or not trials:
        raise SessionTuningSweepError("plan.trials must be a non-empty array")
    blocked_reasons = []
    preview_trials = []
    for trial in trials:
        trial_id = str(trial.get("trial_id", "unknown"))
        classification = trial.get("classification")
        if classification != "session-mutating":
            blocked_reasons.append({"trial_id": trial_id, "reason": f"unsupported classification {classification!r}"})
        session_tuning = trial.get("session_tuning", {})
        actions = session_tuning.get("actions", []) if isinstance(session_tuning, dict) else []
        preview_trials.append(
            {
                "trial_id": trial_id,
                "candidate_id": trial.get("candidate_id"),
                "repetition_index": trial.get("repetition_index", 0),
                "session_tuning_profile_id": session_tuning.get("profile_id") if isinstance(session_tuning, dict) else None,
                "action_count": len(actions) if isinstance(actions, list) else 0,
                "classification": classification,
                "will_execute": False,
                "artifact_dir": trial.get("artifact_dir"),
            }
        )
    return {
        "sweep_id": plan.get("sweep_id"),
        "mode": "dry-run",
        "blocked": bool(blocked_reasons),
        "blocked_reasons": blocked_reasons,
        "candidate_count": plan.get("candidate_count"),
        "trial_count": len(preview_trials),
        "trials": preview_trials,
    }


def write_session_tuning_sweep_plan(sweep_path: Path, out_path: Path) -> dict[str, Any]:
    plan = build_session_tuning_sweep_plan(load_session_tuning_sweep_definition(sweep_path))
    write_json(out_path, plan)
    return plan


def write_session_tuning_sweep_preview(plan_path: Path, out_path: Path) -> dict[str, Any]:
    preview = build_session_tuning_sweep_preview(read_json(plan_path))
    write_json(out_path, preview)
    return preview


def build_candidate_id(sweep_id: str, order: int, profile_id: str) -> str:
    digest = sha256(f"{sweep_id}|candidate|{order}|{profile_id}".encode("utf-8")).hexdigest()[:8]
    return f"{sweep_id}-c{order + 1:03d}-{digest}"


def build_trial_id(sweep_id: str, order: int, repetition_index: int, profile_id: str) -> str:
    digest = sha256(f"{sweep_id}|trial|{order}|{repetition_index}|{profile_id}".encode("utf-8")).hexdigest()[:8]
    return f"{sweep_id}-c{order + 1:03d}-r{repetition_index + 1:02d}-{digest}"
