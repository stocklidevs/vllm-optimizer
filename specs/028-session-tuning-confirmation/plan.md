# Implementation Plan: Session Tuning Confirmation

**Branch**: `028-session-tuning-confirmation` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

## Summary

Add `session-tuning-confirm` to run repeated A/B benchmark confirmation for one session tuning profile. It reuses the existing benchmark runner, session tuning gate, and A/B confirmation report.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Standard library, existing benchmark/session tuning/A-B modules

**Storage**: Local JSON and Markdown artifacts

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows development host orchestrating Linux GX10 over SSH

**Project Type**: Python CLI

**Performance Goals**: Runtime is proportional to `2 * repetitions` benchmark runs.

**Constraints**: Requires explicit session tuning approval; only session-scoped tuning is applied.

**Scale/Scope**: One serve profile, one prompt set, one session tuning profile per invocation.

## Constitution Check

- **Deterministic Experiments**: Pass. Inputs and repetition artifact paths are recorded.
- **Complete Traceability**: Pass. All benchmark artifacts and reports are retained.
- **Remote Safety and Reversibility**: Pass. Tuning is shell-scoped and approval-gated.
- **Objective-Driven Optimization**: Pass. Decision compares latency and throughput.
- **Testable, Modular Automation**: Pass. Runner injection enables local tests.

## Project Structure

```text
specs/028-session-tuning-confirmation/
|-- spec.md
|-- plan.md
|-- contracts/
|   `-- session-tuning-confirm.md
`-- tasks.md

src/vllm_optimizer/
|-- cli.py
`-- session_tuning_confirmation.py

tests/
|-- integration/test_cli_session_tuning_confirmation.py
`-- unit/test_session_tuning_confirmation.py
```

## Experiment and Safety Design

**Objective Family**: Runtime/session tuning confirmation.

**Benchmark Inputs**: Target config, serve profile, prompt set, session tuning profile, repetitions.

**Remote Actions**: Live benchmark runs; tuned side uses shell-scoped session tuning prelude.

**Artifacts**: `current-rN/*`, `tuned-rN/*`, `confirmation-report.json`, `confirmation-report.md`, `summary.json`.

**Rollback/Cleanup**: Existing benchmark cleanup stops vLLM after each run; session tuning ends with shell exit.

## Complexity Tracking

No constitution violations.
