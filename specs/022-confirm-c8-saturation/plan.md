# Implementation Plan: Confirm C8 Saturation

**Branch**: `022-confirm-c8-saturation` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

## Summary

Promote the c8 saturation winner into a candidate profile, run five repeated live benchmarks for the current concurrent profile and the c8 candidate at concurrency 8, generate an A/B confirmation report, and update the concurrent recommended profile only if the report approves switching.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: Candidate profile under `config/profiles/`, ignored live benchmark artifacts, A/B report artifacts, promotion summary artifacts

**Testing**: Existing A/B, benchmark, promotion, and full pytest suite

**Target Platform**: Local CLI controlling remote GX10 over SSH

## Constitution Check

- **Deterministic Experiments**: PASS. Prompt set, profile paths, ranking path, and report paths are explicit.
- **Complete Traceability**: PASS. Confirmation and promotion retain source artifacts and candidate provenance.
- **Remote Safety and Reversibility**: PASS. Live benchmark runs are session-scoped and cleanup after each serve.
- **Objective-Driven Optimization**: PASS. The decision gate uses latency, throughput, failure rate, and noise band.
- **Testable, Modular Automation**: PASS. Reuses existing tested benchmark, A/B, and promotion modules.

## Experiment and Safety Design

**Remote Actions**: Ten session-scoped live benchmark runs: five current concurrent profile, five c8 candidate.

**Artifacts**:

- `config/profiles/qwen3-coder-next-awq-concurrent-c8-candidate.json`
- `artifacts/benchmarks/qwen-c8-confirmation/current-r*`
- `artifacts/benchmarks/qwen-c8-confirmation/c8-r*`
- `artifacts/reports/qwen-c8-concurrency-confirmation.json`
- `artifacts/reports/qwen-c8-concurrency-confirmation.md`

**Rollback/Cleanup**: If promotion is approved, the previous concurrent recommended profile remains recoverable from git history and the confirmation report records the decision.
