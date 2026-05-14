# Implementation Plan: Session Tuning Experiments

**Branch**: `027-session-tuning-experiments` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

## Summary

Introduce guarded session tuning profiles for benchmark runs. The first version supports shell-scoped environment exports and open-file limits, previews them deterministically, rejects persistent/risky actions, and allows `benchmark-plan` / `benchmark-run` to include them only when explicitly opted in.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Standard library, existing benchmark and artifact helpers

**Storage**: JSON profiles and JSON benchmark artifacts

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows development host orchestrating Linux GX10 benchmark shell over SSH

**Project Type**: Python CLI

**Performance Goals**: Tuning prelude should add negligible benchmark startup overhead.

**Constraints**: Session-only; no persistent writes; explicit apply gate for benchmark execution.

**Scale/Scope**: One tuning profile per benchmark run.

## Constitution Check

- **Deterministic Experiments**: Pass. Tuning profile path and rendered prelude are recorded.
- **Complete Traceability**: Pass. Benchmark plan includes tuning metadata.
- **Remote Safety and Reversibility**: Pass. Only shell-scoped env and ulimit are allowed.
- **Objective-Driven Optimization**: Pass. The feature enables runtime/session tuning experiments.
- **Testable, Modular Automation**: Pass. Profile validation, preview, and script rendering are testable locally.

## Project Structure

```text
specs/027-session-tuning-experiments/
|-- spec.md
|-- plan.md
|-- contracts/
|   `-- session-tuning.md
`-- tasks.md

src/vllm_optimizer/
|-- benchmark.py
|-- cli.py
`-- session_tuning.py

config/session-tuning/
`-- qwen-runtime-env.json

tests/
|-- integration/test_cli_session_tuning.py
`-- unit/test_session_tuning.py
```

## Experiment and Safety Design

**Objective Family**: Runtime/session tuning.

**Benchmark Inputs**: Serve profile, prompt set, session tuning profile, optional system tuning catalog.

**Remote Actions**: Shell-local `export` and `ulimit -n` before vLLM starts.

**Artifacts**: Session tuning preview, benchmark plan, benchmark summary and logs.

**Rollback/Cleanup**: Shell-scoped changes end when benchmark shell exits.

## Complexity Tracking

No constitution violations.
