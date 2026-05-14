# Implementation Plan: A/B Benchmark Confirmation

**Branch**: `013-ab-benchmark-confirmation` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/013-ab-benchmark-confirmation/spec.md`

## Summary

Add a local A/B confirmation report that aggregates repeated benchmark summary
artifacts for the original and recommended Qwen profiles. Live repetitions
reuse the existing `benchmark-run` lifecycle; the new implementation only
parses local summaries, computes aggregate means/spreads/failure rates, and
emits a conservative keep/switch/inconclusive decision.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Standard library only; existing artifact and CLI helpers.

**Storage**: Local benchmark artifact directories plus JSON/Markdown aggregate reports.

**Testing**: pytest unit and CLI integration tests.

**Target Platform**: Local controller repository; optional GX10 live runs through existing benchmark command.

**Project Type**: Python CLI/library.

**Performance Goals**: Aggregate six summaries in under 10 seconds.

**Constraints**: No new remote execution path; no persistent system mutation; fail before writing output when inputs are invalid.

**Scale/Scope**: Two profile groups with three repetitions each by default.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic Experiments**: PASS. Inputs list exact profile labels, summary paths, prompt set, repetition count, and thresholds.
- **Complete Traceability**: PASS. Reports include all source summary paths and aggregate metrics.
- **Remote Safety and Reversibility**: PASS. New code is local-only; live work uses existing benchmark lifecycle and cleanup.
- **Objective-Driven Optimization**: PASS. Decision is based on latency, throughput, failure rate, and stability spread.
- **Testable, Modular Automation**: PASS. Aggregation and decision logic will have unit tests; CLI path has integration tests.

## Project Structure

### Documentation (this feature)

```text
specs/013-ab-benchmark-confirmation/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- cli.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/vllm_optimizer/
|-- ab_confirmation.py
`-- cli.py

tests/
|-- unit/
|   `-- test_ab_confirmation.py
`-- integration/
    `-- test_cli_ab_confirmation.py
```

**Structure Decision**: Keep A/B aggregation separate from one-shot default reporting.

## Experiment and Safety Design

**Objective Family**: Stability-aware default choice based on latency,
throughput, failure rate, and spread.

**Benchmark Inputs**: Original profile summaries, recommended profile summaries,
shared prompt set label, repetition count, and noise threshold.

**Remote Actions**: Aggregation/reporting are local-only. Live repetitions use
existing `benchmark-run` with managed serve cleanup.

**Artifacts**: Per-repetition benchmark directories, aggregate report JSON, and
Markdown decision report.

**Rollback/Cleanup**: Existing benchmark cleanup handles vLLM lifecycle. Report
generation writes local files only.

## Complexity Tracking

No constitution violations.
