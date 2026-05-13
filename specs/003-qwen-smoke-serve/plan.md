# Implementation Plan: Qwen Smoke Serve

**Branch**: `003-qwen-smoke-serve` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-qwen-smoke-serve/spec.md`

## Summary

Add dry-run and live smoke lifecycle support for the known Qwen3 Coder Next
profile. The implementation will render an auditable lifecycle plan, perform
read-only preflight checks, start vLLM only when checks pass, poll readiness,
send one tiny request, collect logs/artifacts, and clean up the managed process.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library only; pytest for tests

**Storage**: Local JSON artifacts under `artifacts/smoke/<profile-id>/`

**Testing**: pytest unit/integration tests with mock SSH/lifecycle outputs

**Target Platform**: Local Windows controller orchestrating remote Linux GX10

**Project Type**: Python CLI plus importable library

**Performance Goals**: Not a benchmark; readiness and one request are timed for
operational evidence only

**Constraints**: Must refuse occupied port or existing matching vLLM process;
must clean up after start; no package install or system tuning

**Scale/Scope**: One profile, one server process, one smoke request

## Constitution Check

- **Deterministic Experiments**: PASS. Plan and artifacts record profile,
  command, preflight checks, timings, and results.
- **Complete Traceability**: PASS. Plan, logs, response, cleanup, and summary
  artifacts are retained.
- **Remote Safety and Reversibility**: PASS. Session-mutating action has
  preflight gates and cleanup.
- **Objective-Driven Optimization**: PASS. This validates lifecycle readiness,
  not a performance objective.
- **Testable, Modular Automation**: PASS. Smoke plan rendering, preflight
  parsing, artifact writing, and CLI are testable independently.

## Project Structure

```text
src/vllm_optimizer/
|-- smoke.py
`-- existing modules

tests/unit/test_smoke.py
tests/integration/test_cli_smoke.py
```

## Experiment and Safety Design

**Objective Family**: Lifecycle readiness.

**Benchmark Inputs**: Qwen serve profile and local GX10 config.

**Remote Actions**: Port/process preflight checks, server start, readiness
poll, one smoke request, cleanup, final process check.

**Artifacts**: `plan.json`, `summary.json`, `server.log`,
`smoke-response.json`, `cleanup.json`, `redaction-report.json`.

**Rollback/Cleanup**: Always attempt cleanup for the managed process after
start.

## Complexity Tracking

No constitution violations are required.
