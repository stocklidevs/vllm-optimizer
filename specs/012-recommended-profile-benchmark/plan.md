# Implementation Plan: Recommended Profile Benchmark

**Branch**: `012-recommended-profile-benchmark` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/012-recommended-profile-benchmark/spec.md`

## Summary

Add a local default-decision report for validating the promoted recommended
profile against a standalone benchmark summary. The benchmark plan/live run will
reuse existing `benchmark-plan` and `benchmark-run` commands with the promoted
profile. New code will compare original baseline summary, recommended benchmark
summary, promoted profile provenance, and optional source ranking into JSON and
Markdown that states whether the recommended profile should remain the default.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Standard library only; existing artifact,
benchmark, serve-profile, and CLI modules.

**Storage**: Local JSON benchmark artifacts and Markdown/JSON decision reports.

**Testing**: pytest unit and CLI integration tests.

**Target Platform**: Local controller repository; optional GX10 live benchmark
through existing managed benchmark lifecycle.

**Project Type**: Python CLI/library.

**Performance Goals**: Local plan/report generation under 10 seconds for
current artifact sizes.

**Constraints**: No new remote execution path; no new dependencies; no
persistent Linux/NVIDIA mutation; fail before writing reports when required
inputs are invalid.

**Scale/Scope**: One promoted profile and one benchmark summary at a time.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic Experiments**: PASS. Report inputs are explicit artifact
  paths; benchmark plan uses existing prompt corpus and promoted profile.
- **Complete Traceability**: PASS. Decision report records baseline summary,
  recommended summary, promoted profile, candidate id, source sweep id, and
  optional source ranking path.
- **Remote Safety and Reversibility**: PASS. New code is local-only reporting;
  live benchmarking reuses existing session-mutating lifecycle and cleanup.
- **Objective-Driven Optimization**: PASS. Decision is based on latency,
  throughput, failure count, and balanced default suitability.
- **Testable, Modular Automation**: PASS. Report logic is isolated in a module
  with unit tests and CLI integration tests.

## Project Structure

### Documentation (this feature)

```text
specs/012-recommended-profile-benchmark/
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
|-- default_report.py
|-- cli.py
|-- benchmark.py
`-- serve_profiles.py

tests/
|-- unit/
|   `-- test_default_report.py
`-- integration/
    `-- test_cli_default_report.py
```

**Structure Decision**: Keep default decision logic separate from the broader
comparison report so this spec can focus on promoted-profile validation.

## Experiment and Safety Design

**Objective Family**: Balanced default suitability, with latency and throughput
deltas reported explicitly.

**Benchmark Inputs**: Existing Qwen baseline prompt set, promoted recommended
profile, original baseline summary, recommended benchmark summary, and
promotion provenance.

**Remote Actions**: Planning/reporting are local-only. Live benchmarking uses
the existing `benchmark-run` managed vLLM lifecycle.

**Artifacts**: Recommended benchmark plan, live benchmark artifacts, default
decision report JSON, and default decision Markdown.

**Rollback/Cleanup**: Existing benchmark runner terminates managed vLLM process
and writes cleanup artifacts. Report generation writes local files only.

## Complexity Tracking

No constitution violations.
