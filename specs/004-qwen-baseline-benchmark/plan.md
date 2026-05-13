# Implementation Plan: Qwen Baseline Benchmark

**Branch**: `004-qwen-baseline-benchmark` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-qwen-baseline-benchmark/spec.md`

## Summary

Add a small sequential baseline benchmark using the existing Qwen serve profile
and safe lifecycle wrapper. The benchmark renders a dry-run plan, starts Qwen
only after preflight checks pass, runs a fixed prompt set, captures per-request
metrics and raw responses, summarizes baseline metrics, and cleans up.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library only; pytest for tests

**Storage**: Local JSON artifacts under `artifacts/benchmarks/qwen-baseline/`

**Testing**: pytest unit/integration tests with local fixtures

**Target Platform**: Local Windows controller orchestrating remote Linux GX10

**Project Type**: Python CLI plus importable library

**Performance Goals**: Not optimization; record first baseline metrics

**Constraints**: Sequential fixed prompts only; no parameter changes; cleanup
required

**Scale/Scope**: One Qwen profile, small fixed prompt set, one request per
prompt

## Constitution Check

- **Deterministic Experiments**: PASS. Prompt set, profile, and run artifacts
  are recorded.
- **Complete Traceability**: PASS. Raw responses and summary link by prompt id.
- **Remote Safety and Reversibility**: PASS. Reuses smoke preflight/cleanup.
- **Objective-Driven Optimization**: PASS. Baseline measurement is named and
  not claimed as optimized.
- **Testable, Modular Automation**: PASS. Plan rendering and metric summarizing
  are unit-testable.

## Project Structure

```text
src/vllm_optimizer/benchmark.py
config/prompts/qwen-baseline.json
tests/unit/test_benchmark.py
tests/integration/test_cli_benchmark.py
```

## Experiment and Safety Design

**Objective Family**: Baseline measurement.

**Benchmark Inputs**: Qwen serve profile and fixed prompt set.

**Remote Actions**: Same lifecycle as smoke serve plus multiple sequential chat
requests.

**Artifacts**: `plan.json`, `prompts.json`, `responses.json`, `metrics.json`,
`summary.json`, `server-log.json`, `cleanup.json`, `redaction-report.json`.

**Rollback/Cleanup**: Always attempt cleanup after server start.

## Complexity Tracking

No constitution violations are required.
