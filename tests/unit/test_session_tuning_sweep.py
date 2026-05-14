from pathlib import Path

from vllm_optimizer.session_tuning_sweep import (
    build_session_tuning_sweep_plan,
    build_session_tuning_sweep_preview,
    load_session_tuning_sweep_definition,
)


def test_session_tuning_sweep_plan_is_deterministic() -> None:
    definition = load_session_tuning_sweep_definition(
        Path("config/session-tuning-sweeps/qwen-runtime-env-sweep.json")
    )

    plan = build_session_tuning_sweep_plan(definition)
    again = build_session_tuning_sweep_plan(definition)

    assert [candidate["candidate_id"] for candidate in plan["candidates"]] == [
        candidate["candidate_id"] for candidate in again["candidates"]
    ]
    assert plan["candidate_count"] == 4
    assert plan["trial_count"] == 8
    assert plan["trials"][0]["session_tuning"]["profile_id"] == "qwen-no-env-v1"
    assert plan["trials"][0]["benchmark_plan"]["session_tuning"]["profile_id"] == "qwen-no-env-v1"


def test_session_tuning_sweep_preview_reports_unblocked_trials() -> None:
    definition = load_session_tuning_sweep_definition(
        Path("config/session-tuning-sweeps/qwen-runtime-env-sweep.json")
    )
    plan = build_session_tuning_sweep_plan(definition)

    preview = build_session_tuning_sweep_preview(plan)

    assert preview["blocked"] is False
    assert preview["trial_count"] == 8
    assert preview["trials"][0]["will_execute"] is False
    assert preview["trials"][0]["session_tuning_profile_id"] == "qwen-no-env-v1"
