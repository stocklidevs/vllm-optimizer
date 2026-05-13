from pathlib import Path

from vllm_optimizer.artifacts import read_jsonl
from vllm_optimizer.experiments import load_experiment
from vllm_optimizer.planner import build_trial_plan
from vllm_optimizer.ranking import rank_results


def test_rank_results_orders_by_primary_and_tie_breaker() -> None:
    plan = build_trial_plan(load_experiment(Path("tests/fixtures/experiments/throughput.json")))
    rows = read_jsonl(Path("tests/fixtures/results/throughput.jsonl"))

    report = rank_results(plan, rows)

    assert report["ranked_trials"][0]["trial_id"] == "demo-throughput-t004"
    assert report["ranked_trials"][1]["trial_id"] == "demo-throughput-t003"
    assert {"trial_id": "not-in-plan", "reason": "trial not found in plan"} in report[
        "excluded_trials"
    ]


def test_rank_results_excludes_missing_results() -> None:
    plan = build_trial_plan(load_experiment(Path("tests/fixtures/experiments/throughput.json")))

    report = rank_results(plan, [])

    assert len(report["ranked_trials"]) == 0
    assert len(report["excluded_trials"]) == len(plan["trials"])
