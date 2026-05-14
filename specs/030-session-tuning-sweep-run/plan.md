# Implementation Plan: Session Tuning Sweep Run

**Branch**: `030-session-tuning-sweep-run` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

## Summary

Add live execution and ranking for session tuning sweeps. The runner reuses benchmark execution with session tuning profiles, writes JSONL rows, and ranks candidates with existing objective scoring.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing benchmark, session tuning, discovery, artifact, and sweep ranking modules

**Storage**: JSONL result rows and JSON ranking reports

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows host orchestrating Linux GX10 over SSH

**Project Type**: Python CLI

**Constraints**: Requires explicit `--allow-session-tuning`; no promotion.

## Constitution Check

- **Deterministic Experiments**: Pass. Plan and result paths are retained.
- **Complete Traceability**: Pass. Every trial row links to artifact paths.
- **Remote Safety and Reversibility**: Pass. Session-scoped tuning only.
- **Objective-Driven Optimization**: Pass. Throughput, latency, balanced ranking.
- **Testable, Modular Automation**: Pass. Fake benchmark runner unit tests cover execution.

## Project Structure

```text
specs/030-session-tuning-sweep-run/
|-- spec.md
|-- plan.md
|-- contracts/
|   `-- session-tuning-sweep-run.md
`-- tasks.md

src/vllm_optimizer/
|-- cli.py
`-- session_tuning_sweep.py

tests/
|-- integration/test_cli_session_tuning_sweep_run.py
`-- unit/test_session_tuning_sweep_run.py
```

## Experiment and Safety Design

**Objective Family**: Runtime/session tuning performance.

**Benchmark Inputs**: Session tuning sweep plan and target config.

**Remote Actions**: Live benchmark sessions with shell-scoped tuning.

**Artifacts**: Trial benchmark dirs, `results.jsonl`, `ranking.json`.

**Rollback/Cleanup**: Existing benchmark cleanup stops vLLM; shell tuning exits with session.

## Complexity Tracking

No constitution violations.
