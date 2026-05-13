from pathlib import Path

from vllm_optimizer.experiments import load_experiment
from vllm_optimizer.planner import build_trial_plan, expand_trials


FIXTURE = Path("tests/fixtures/experiments/throughput.json")


def test_expand_trials_is_deterministic() -> None:
    experiment = load_experiment(FIXTURE)

    first = expand_trials(experiment)
    second = expand_trials(experiment)

    assert [trial.trial_id for trial in first] == [trial.trial_id for trial in second]
    assert [trial.parameters for trial in first] == [trial.parameters for trial in second]
    assert len(first) == 8


def test_build_trial_plan_contains_reproducibility_metadata() -> None:
    experiment = load_experiment(FIXTURE)
    plan = build_trial_plan(experiment)

    assert plan["source_hash"]
    assert plan["objective"]["family"] == "throughput"
    assert plan["model"]["vllm_version"] == "0.0.fixture"
    assert plan["trials"][0]["trial_id"] == "demo-throughput-t001"
