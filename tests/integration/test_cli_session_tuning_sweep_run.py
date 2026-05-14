from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_jsonl
from vllm_optimizer.cli import main


def test_session_tuning_sweep_run_cli_requires_allowance(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    assert main(["session-tuning-sweep-plan", "--sweep", "config/session-tuning-sweeps/qwen-runtime-env-sweep.json", "--out", str(plan_path)]) == 0

    exit_code = main(
        [
            "session-tuning-sweep-run",
            "--config",
            "tests/fixtures/discovery/local.gx10.mock.json",
            "--plan",
            str(plan_path),
            "--out",
            str(tmp_path / "live"),
        ]
    )

    assert exit_code == 2


def test_session_tuning_sweep_rank_cli_writes_ranking(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    results_path = tmp_path / "results.jsonl"
    ranking_path = tmp_path / "ranking.json"
    assert main(["session-tuning-sweep-plan", "--sweep", "config/session-tuning-sweeps/qwen-runtime-env-sweep.json", "--out", str(plan_path)]) == 0
    plan = read_json(plan_path)
    write_jsonl(
        results_path,
        [
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
            for index, trial in enumerate(plan["trials"])
        ],
    )

    exit_code = main(
        [
            "session-tuning-sweep-rank",
            "--plan",
            str(plan_path),
            "--results",
            str(results_path),
            "--out",
            str(ranking_path),
        ]
    )

    assert exit_code == 0
    ranking = read_json(ranking_path)
    assert "balanced" in ranking["objectives"]
