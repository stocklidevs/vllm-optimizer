# Implementation Plan: Expanded Qwen Sweep

**Branch**: `008-expanded-qwen-sweep` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/008-expanded-qwen-sweep/spec.md`

## Summary

Add a fixed expanded repeated sweep configuration around the current Qwen
winner. The implementation uses existing sweep planning, preview, live run,
ranking, and report commands, with tests proving the config produces six
candidates and eighteen sequential trials.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Existing sweep/report modules, pytest

**Storage**: Local JSON/Markdown artifacts under ignored `artifacts/`

**Testing**: pytest unit/integration tests

**Target Platform**: Local controller; optional remote GX10 live run

**Project Type**: Python CLI

**Performance Goals**: Local plan and preview in under one second; live run
remains sequential

**Constraints**: No persistent Linux/NVIDIA tuning, no installs, no concurrent
load testing

**Scale/Scope**: Six candidates, three repetitions each, eighteen trials total

## Constitution Check

- **Deterministic Experiments**: PASS. Config fixes candidate grid, repetitions,
  prompt set, baseline reference, and artifact paths.
- **Complete Traceability**: PASS. Existing sweep runner records per-repetition
  artifacts and ranking source links.
- **Remote Safety and Reversibility**: PASS. Live run is session-mutating only
  and uses cleanup after every started trial.
- **Objective-Driven Optimization**: PASS. Throughput, latency, and balanced
  rankings are produced.
- **Testable, Modular Automation**: PASS. Config, plan generation, preview,
  ranking compatibility, and report compatibility are testable locally.

## Project Structure

```text
config/sweeps/qwen-expanded-safe.json
tests/unit/test_sweep.py
tests/integration/test_cli_sweep.py
README.md
specs/008-expanded-qwen-sweep/
```

**Structure Decision**: No new code module is needed; this feature exercises
existing sweep and report capabilities with a larger fixed configuration.

## Experiment and Safety Design

**Objective Family**: Expanded repeated Qwen session-level optimization

**Benchmark Inputs**: Qwen baseline prompt set, baseline summary, GPU memory
utilization values 0.88/0.90/0.92, performance modes interactivity/throughput,
max model length 32768, three repetitions

**Remote Actions**: None for plan/preview/ranking/report. Optional live run
starts and cleans vLLM sequentially per trial.

**Artifacts**: Plan, preview, live result JSONL, per-trial benchmark artifacts,
ranking JSON, comparison report JSON/Markdown

**Rollback/Cleanup**: Existing benchmark cleanup after every started trial

## Complexity Tracking

No constitution violations.
