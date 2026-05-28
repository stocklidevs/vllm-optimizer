# Implementation Plan: Qwen Parameter Sweep

**Branch**: `005-qwen-parameter-sweep` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-qwen-parameter-sweep/spec.md`

## Summary

Add a deterministic, bounded sweep layer over the existing Qwen baseline
benchmark workflow. The implementation will load a sweep definition, generate
safe profile variants in stable order, render dry-run previews without SSH,
optionally execute each trial sequentially through the existing benchmark
lifecycle, and produce objective-specific rankings with baseline deltas and
artifact traceability.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library, pytest, existing project modules
for artifacts, serve profiles, benchmark execution, safety, and ranking

**Storage**: Local JSON/JSONL artifacts under ignored `artifacts/` directories

**Testing**: pytest unit and integration tests

**Target Platform**: Local controller on Windows; remote Asus GX10 over
configured SSH for approved live runs

**Project Type**: Python CLI

**Performance Goals**: Generate local sweep plans for small bounded parameter
spaces in under one second; live sweeps remain sequential and small

**Constraints**: No persistent Linux/NVIDIA mutation, no package installs, no
unbounded shell input, no concurrent load testing, no live GX10 contact from
dry-run paths

**Scale/Scope**: Initial sweep supports a small Cartesian set of safe
session-level vLLM profile overrides and three ranking objectives

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic Experiments**: PASS. Sweep definitions include seed,
  baseline profile, prompt set, parameter space, trial ordering, and artifact
  paths.
- **Complete Traceability**: PASS. Each trial writes raw benchmark artifacts,
  result metadata, cleanup evidence, and ranking links back to sources.
- **Remote Safety and Reversibility**: PASS. Dry-run preview is local only;
  live execution is session-mutating and uses existing cleanup behavior.
- **Objective-Driven Optimization**: PASS. Throughput, latency, and balanced
  objectives are named explicitly with tie-breakers.
- **Testable, Modular Automation**: PASS. Planning, validation, preview,
  result aggregation, ranking, and CLI behavior are independently testable.

## Project Structure

### Documentation (this feature)

```text
specs/005-qwen-parameter-sweep/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- cli.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md
```

### Source Code (repository root)

```text
config/
|-- sweeps/
|   `-- qwen-small-sweep.json
src/vllm_optimizer/
|-- sweep.py
|-- cli.py
tests/
|-- integration/
|   `-- test_cli_sweep.py
`-- unit/
    `-- test_sweep.py
```

**Structure Decision**: Add one focused `sweep.py` module that composes the
existing serve-profile and benchmark modules. CLI changes remain in `cli.py`;
tests mirror the existing unit/integration layout.

## Experiment and Safety Design

**Objective Family**: Session-level Qwen vLLM parameter optimization for
throughput, latency, and balanced objective rankings

**Benchmark Inputs**: Existing Qwen prompt set, sequential request mix, bounded
parameter candidates, seed, maximum trial count, baseline profile, and optional
baseline summary

**Remote Actions**: Dry-run paths perform no SSH. Live execution starts vLLM,
runs the fixed benchmark, captures artifacts, and performs cleanup once per
trial. All actions are session-mutating only.

**Artifacts**: Sweep definition, sweep plan, dry-run preview, per-trial
benchmark artifacts, result manifest, failure records, ranking report, command
logs, and cleanup evidence

**Rollback/Cleanup**: Each started trial uses the existing benchmark cleanup
verification. Persistent host changes are blocked rather than rolled back.

## Complexity Tracking

No constitution violations.
