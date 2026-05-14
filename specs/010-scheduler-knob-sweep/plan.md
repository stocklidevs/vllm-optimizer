# Implementation Plan: Scheduler Knob Sweep

**Branch**: `010-scheduler-knob-sweep` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/010-scheduler-knob-sweep/spec.md`

## Summary

Extend serve profiles with an explicit optional flag allowlist for scheduler
and prefill knobs, update sweep overrides to handle those options, and add a
bounded Qwen scheduler sweep config using three repetitions per candidate.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library, pytest, existing serve-profile and
sweep modules

**Storage**: Local JSON artifacts under ignored `artifacts/`

**Testing**: pytest unit/integration tests

**Target Platform**: Local controller; optional live GX10 run later

**Project Type**: Python CLI

**Performance Goals**: Local plan/preview in under one second

**Constraints**: Only approved optional flags, no arbitrary shell fragments, no
persistent host mutation, no concurrent load tests

**Scale/Scope**: Small scheduler sweep around current Qwen champion

## Constitution Check

- **Deterministic Experiments**: PASS. Optional flags and sweep values are
  recorded in profiles and plans.
- **Complete Traceability**: PASS. Rendered commands and artifacts include
  optional flag values.
- **Remote Safety and Reversibility**: PASS. New flags are session-level only
  and previewable before live execution.
- **Objective-Driven Optimization**: PASS. Scheduler sweep keeps throughput,
  latency, and balanced objectives.
- **Testable, Modular Automation**: PASS. Rendering, validation, sweep planning,
  and CLI preview are locally testable.

## Project Structure

```text
config/sweeps/qwen-scheduler-safe.json
src/vllm_optimizer/serve_profiles.py
src/vllm_optimizer/sweep.py
tests/unit/test_serve_profiles.py
tests/unit/test_sweep.py
tests/integration/test_cli_sweep.py
specs/010-scheduler-knob-sweep/
```

**Structure Decision**: Extend existing serve profile and sweep modules because
optional serve flags are part of command rendering and candidate generation.

## Experiment and Safety Design

**Objective Family**: Scheduler/prefill session-level Qwen optimization

**Benchmark Inputs**: Existing Qwen prompt set and baseline summary,
`max_num_batched_tokens`, `max_num_seqs`, `enable_chunked_prefill`, and
`enable_prefix_caching`

**Remote Actions**: None for plan/preview. Optional live execution uses existing
session-mutating sweep runner.

**Artifacts**: Plan, preview, results JSONL, per-trial benchmark artifacts,
ranking report, comparison report

**Rollback/Cleanup**: Existing benchmark cleanup after each started trial

## Complexity Tracking

No constitution violations.
