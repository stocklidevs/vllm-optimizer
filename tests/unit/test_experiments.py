from pathlib import Path

import pytest

from vllm_optimizer.experiments import ExperimentValidationError, load_experiment, parse_experiment


FIXTURE = Path("tests/fixtures/experiments/throughput.json")


def test_load_experiment_validates_fixture() -> None:
    experiment = load_experiment(FIXTURE)

    assert experiment.experiment_id == "demo-throughput"
    assert experiment.objective.family == "throughput"
    assert sorted(experiment.parameter_space) == [
        "gpu_memory_utilization",
        "max_num_batched_tokens",
    ]


def test_parse_experiment_rejects_missing_objective() -> None:
    with pytest.raises(ExperimentValidationError, match="objective is required"):
        parse_experiment(
            {
                "experiment_id": "bad",
                "model": {"id": "m", "vllm_version": "fixture"},
                "workload": {
                    "prompt_corpus_id": "p",
                    "request_mix": "r",
                    "concurrency": [1],
                    "seeds": [1],
                },
                "parameter_space": {"x": [1]},
                "target": {"host_label": "gx10", "execution_mode": "dry-run"},
            }
        )
