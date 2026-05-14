# Implementation Plan: Concurrency Saturation

**Branch**: `020-concurrency-saturation` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/020-concurrency-saturation/spec.md`

## Summary

Add a local saturation-report command that summarizes ranked concurrent interactive sweeps by concurrency level, create deterministic concurrency ladder prompt sets and sweep configs near the current winner, improve FP8 dtype failure classification, and refresh documentation/versioning.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: JSON prompt sets, JSON sweep configs, JSON/Markdown reports, ignored artifact outputs

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Local CLI coordinating optional remote GX10 live runs

**Project Type**: CLI tool

**Performance Goals**: Local report generation completes in under one second for normal artifact sizes.

**Constraints**: No persistent remote/system changes; live runs are session-scoped and require existing sweep preview gates.

**Scale/Scope**: Six concurrency levels and a compact candidate matrix around the known concurrent winner.

## Constitution Check

- **Deterministic Experiments**: PASS. Prompt sets, sweep configs, and ranking artifacts are explicit inputs.
- **Complete Traceability**: PASS. Reports retain source ranking paths and winner candidate ids.
- **Remote Safety and Reversibility**: PASS. New implementation is local; live commands reuse session-scoped sweep harness.
- **Objective-Driven Optimization**: PASS. Saturation recommendation names throughput, failure rate, latency, and tie breakers.
- **Testable, Modular Automation**: PASS. Report builder, CLI, configs, and classifier behavior are covered by tests.

## Project Structure

```text
src/vllm_optimizer/
|-- saturation_report.py
|-- workload_report.py
`-- cli.py

config/prompts/
`-- qwen-coding-interactive-concurrency-*.json

config/sweeps/
`-- qwen-concurrency-saturation-c*.json

tests/
|-- unit/test_saturation_report.py
|-- unit/test_workload_report.py
|-- unit/test_sweep.py
`-- integration/test_cli_saturation_report.py
```

**Structure Decision**: Use a dedicated saturation_report module rather than overloading workload_report because saturation compares several rankings for the same workload dimension.

## Experiment and Safety Design

**Objective Family**: Concurrent interactive throughput saturation with latency and failure-rate tie breakers.

**Benchmark Inputs**: Interactive coding prompt set replicated across concurrency levels 1, 2, 3, 4, 6, and 8.

**Remote Actions**: Optional live sweep execution over SSH using existing cleanup behavior.

**Artifacts**: Plans/previews/live rankings under `artifacts/sweeps/qwen-concurrency-saturation-*`; report under `artifacts/reports/qwen-concurrency-saturation.*`.

**Rollback/Cleanup**: Local generated artifacts are ignored by git; remote serve cleanup remains part of the benchmark harness.

## Complexity Tracking

No constitution violations.
