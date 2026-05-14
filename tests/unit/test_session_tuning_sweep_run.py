from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json, read_jsonl, write_json
from vllm_optimizer.discovery import DiscoveryTarget
from vllm_optimizer.session_tuning_sweep import (
    SessionTuningSweepError,
    rank_session_tuning_sweep_results,
    run_session_tuning_sweep,
    write_session_tuning_sweep_plan,
)


def test_session_tuning_sweep_run_writes_result_rows(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    write_session_tuning_sweep_plan(Path("config/session-tuning-sweeps/qwen-runtime-env-sweep.json"), plan_path)
    calls = []

    def runner(_target, _profile, _prompt_set, out_dir, _timeout_seconds, session_tuning=None):
        calls.append(session_tuning.profile_id if session_tuning else "none")
        throughput = 50 + len(calls)
        summary = {
            "mean_latency_ms": 1000 - len(calls),
            "aggregate_tokens_per_second": throughput,
            "success_count": 1,
            "failure_count": 0,
        }
        write_json(out_dir / "summary.json", summary)
        return {"summary": summary, "artifact_paths": {"summary": (out_dir / "summary.json").as_posix()}}

    result = run_session_tuning_sweep(
        DiscoveryTarget("mock", "mock@example", ()),
        read_json(plan_path),
        tmp_path / "live",
        timeout_seconds=1200,
        continue_on_failure=False,
        allow_session_tuning=True,
        benchmark_runner=runner,
    )

    rows = read_jsonl(tmp_path / "live" / "results.jsonl")
    assert result["success_count"] == 8
    assert len(rows) == 8
    assert rows[0]["session_tuning_profile_id"] == "qwen-no-env-v1"
    assert rows[-1]["status"] == "completed"


def test_session_tuning_sweep_run_requires_allowance(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    write_session_tuning_sweep_plan(Path("config/session-tuning-sweeps/qwen-runtime-env-sweep.json"), plan_path)

    with pytest.raises(SessionTuningSweepError, match="--allow-session-tuning"):
        run_session_tuning_sweep(
            DiscoveryTarget("mock", "mock@example", ()),
            read_json(plan_path),
            tmp_path / "live",
            allow_session_tuning=False,
        )


def test_session_tuning_sweep_rank_uses_existing_objectives(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    write_session_tuning_sweep_plan(Path("config/session-tuning-sweeps/qwen-runtime-env-sweep.json"), plan_path)
    plan = read_json(plan_path)
    rows = []
    for index, trial in enumerate(plan["trials"]):
        rows.append(
            {
                "trial_id": trial["trial_id"],
                "candidate_id": trial["candidate_id"],
                "repetition_index": trial["repetition_index"],
                "status": "completed",
                "summary": {
                    "mean_latency_ms": 1000 - index,
                    "aggregate_tokens_per_second": 50 + index,
                    "success_count": 1,
                    "failure_count": 0,
                },
                "artifact_paths": {"summary": "summary.json"},
            }
        )

    ranking = rank_session_tuning_sweep_results(plan, rows)

    assert ranking["objectives"]["throughput"][0]["candidate_id"] == plan["trials"][-1]["candidate_id"]
    assert ranking["ranked_trial_count"] == 4
