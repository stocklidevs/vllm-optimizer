from __future__ import annotations

import hashlib
import itertools
import json
from datetime import UTC, datetime
from typing import Any

from .types import ExperimentDefinition, Trial


def build_trial_plan(experiment: ExperimentDefinition) -> dict[str, Any]:
    trials = expand_trials(experiment)
    return {
        "experiment_id": experiment.experiment_id,
        "created_at": datetime.now(UTC).isoformat(),
        "source_hash": experiment_hash(experiment),
        "objective": {
            "family": experiment.objective.family,
            "primary_metric": experiment.objective.primary_metric,
            "direction": experiment.objective.direction,
            "constraints": experiment.objective.constraints,
            "tie_breakers": [
                {"metric": item.metric, "direction": item.direction}
                for item in experiment.objective.tie_breakers
            ],
        },
        "model": {
            "id": experiment.model.id,
            "path_label": experiment.model.path_label,
            "vllm_version": experiment.model.vllm_version,
            "tokenizer": experiment.model.tokenizer,
        },
        "workload": {
            "prompt_corpus_id": experiment.workload.prompt_corpus_id,
            "request_mix": experiment.workload.request_mix,
        },
        "target": {
            "host_label": experiment.target.host_label,
            "execution_mode": experiment.target.execution_mode,
        },
        "trials": [trial_to_dict(trial) for trial in trials],
    }


def expand_trials(experiment: ExperimentDefinition) -> list[Trial]:
    parameter_keys = sorted(experiment.parameter_space)
    parameter_values = [experiment.parameter_space[key] for key in parameter_keys]
    trials: list[Trial] = []

    ordinal = 1
    for seed in sorted(experiment.workload.seeds):
        for concurrency in sorted(experiment.workload.concurrency):
            for values in itertools.product(*parameter_values):
                parameters = dict(zip(parameter_keys, values, strict=True))
                trials.append(
                    Trial(
                        trial_id=f"{experiment.experiment_id}-t{ordinal:03d}",
                        ordinal=ordinal,
                        seed=seed,
                        concurrency=concurrency,
                        parameters=parameters,
                    )
                )
                ordinal += 1

    return trials


def experiment_hash(experiment: ExperimentDefinition) -> str:
    payload = {
        "experiment_id": experiment.experiment_id,
        "objective": {
            "family": experiment.objective.family,
            "primary_metric": experiment.objective.primary_metric,
            "direction": experiment.objective.direction,
            "constraints": experiment.objective.constraints,
            "tie_breakers": [
                {"metric": item.metric, "direction": item.direction}
                for item in experiment.objective.tie_breakers
            ],
        },
        "model": {
            "id": experiment.model.id,
            "path_label": experiment.model.path_label,
            "vllm_version": experiment.model.vllm_version,
            "tokenizer": experiment.model.tokenizer,
        },
        "workload": {
            "prompt_corpus_id": experiment.workload.prompt_corpus_id,
            "request_mix": experiment.workload.request_mix,
            "concurrency": list(experiment.workload.concurrency),
            "seeds": list(experiment.workload.seeds),
        },
        "parameter_space": {
            key: list(value) for key, value in sorted(experiment.parameter_space.items())
        },
        "target": {
            "host_label": experiment.target.host_label,
            "execution_mode": experiment.target.execution_mode,
        },
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def trial_to_dict(trial: Trial) -> dict[str, Any]:
    return {
        "trial_id": trial.trial_id,
        "ordinal": trial.ordinal,
        "seed": trial.seed,
        "concurrency": trial.concurrency,
        "parameters": trial.parameters,
    }
