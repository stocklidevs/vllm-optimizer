# Implementation Plan: Live Concurrency Saturation

**Branch**: `021-live-concurrency-saturation` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

## Summary

Run the planned concurrency saturation sweeps on the GX10 for c1, c2, c4, c6, and c8, combine them with the existing c3 ranking, regenerate the saturation report, update documentation/versioning, verify, and commit.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: Ignored live artifacts under `artifacts/sweeps/` and report outputs under `artifacts/reports/`

**Testing**: pytest full suite after report/docs update

**Target Platform**: Local CLI controlling remote GX10 over SSH

## Constitution Check

- **Deterministic Experiments**: PASS. Existing plans define the live trials.
- **Complete Traceability**: PASS. Live artifacts and report paths are retained.
- **Remote Safety and Reversibility**: PASS. Existing sweep harness performs session-scoped serve cleanup.
- **Objective-Driven Optimization**: PASS. Saturation report names throughput, latency, failure rate, and recommendation.
- **Testable, Modular Automation**: PASS. The CLI/report code is already covered; full suite will run after execution.

## Experiment and Safety Design

**Remote Actions**: Sequential session-scoped vLLM serve trials for c1, c2, c4, c6, and c8.

**Artifacts**: `artifacts/sweeps/qwen-concurrency-saturation-c*/live` and `artifacts/reports/qwen-concurrency-saturation.*`.

**Rollback/Cleanup**: vLLM process cleanup is built into each benchmark trial; local artifacts are ignored by git.
