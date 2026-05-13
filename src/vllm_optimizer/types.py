from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


ObjectiveFamily = Literal[
    "throughput",
    "latency",
    "memory",
    "tool-calling",
    "structured-output",
    "long-context",
    "stability",
    "balanced",
]
Direction = Literal["maximize", "minimize"]
ActionClass = Literal["read-only", "session-mutating", "persistent-mutating"]


@dataclass(frozen=True)
class TieBreaker:
    metric: str
    direction: Direction


@dataclass(frozen=True)
class Objective:
    family: ObjectiveFamily
    primary_metric: str
    direction: Direction
    constraints: dict[str, Any] = field(default_factory=dict)
    tie_breakers: tuple[TieBreaker, ...] = ()


@dataclass(frozen=True)
class ModelConfig:
    id: str
    vllm_version: str
    path_label: str | None = None
    tokenizer: str | None = None


@dataclass(frozen=True)
class Workload:
    prompt_corpus_id: str
    request_mix: str
    concurrency: tuple[int, ...]
    seeds: tuple[int, ...]


@dataclass(frozen=True)
class Target:
    host_label: str
    execution_mode: Literal["dry-run"]


@dataclass(frozen=True)
class ExperimentDefinition:
    experiment_id: str
    objective: Objective
    model: ModelConfig
    workload: Workload
    parameter_space: dict[str, tuple[Any, ...]]
    target: Target
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Trial:
    trial_id: str
    ordinal: int
    seed: int
    concurrency: int
    parameters: dict[str, Any]


@dataclass(frozen=True)
class RemoteAction:
    action_id: str
    trial_id: str | None
    kind: str
    classification: ActionClass
    command: str
    allowed: bool
    expected_side_effects: str
    cleanup: str | None = None
