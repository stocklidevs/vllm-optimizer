# Implementation Plan: Promote Winner Profile

**Branch**: `011-promote-winner-profile` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/011-promote-winner-profile/spec.md`

## Summary

Add a local-only promotion workflow that reads an existing sweep ranking
artifact, selects the top candidate for a requested objective, previews the
candidate and provenance, and can write a reusable recommended serve profile
plus a human-readable promotion summary. The implementation will add a small
promotion module, CLI commands for preview/write flows, tests for invalid
rankings and overwrite safety, and documentation for promoting the current GX10
scheduler winner.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Standard library only; existing project modules for
JSON artifacts, serve-profile validation, and CLI wiring.

**Storage**: Local JSON and Markdown files. Generated recommended profiles are
intended for version control; live sweep artifacts remain ignored.

**Testing**: pytest unit and integration tests.

**Target Platform**: Local controller machine running the repository CLI.

**Project Type**: Python CLI/library.

**Performance Goals**: Preview and promotion complete in under 10 seconds for
current ranking artifact sizes.

**Constraints**: No GX10 SSH, no vLLM launch, no remote mutation, no dependency
additions, deterministic candidate selection for identical ranking/objective
inputs.

**Scale/Scope**: Existing sweep ranking artifacts with tens to hundreds of
candidates; first target is the Qwen scheduler sweep winner.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic Experiments**: PASS. Promotion records ranking artifact,
  objective, selected candidate id, source trials, metrics, and source profile
  settings. Selection is deterministic for the same artifact and objective.
- **Complete Traceability**: PASS. Generated profile and summary link back to
  the ranking artifact, source sweep, selected candidate, and source trial ids.
- **Remote Safety and Reversibility**: PASS. All actions are local-only and
  read existing artifacts. Profile writes require explicit output paths and
  overwrite protection.
- **Objective-Driven Optimization**: PASS. Promotion requires a named objective
  and refuses artifacts without that objective.
- **Testable, Modular Automation**: PASS. Core selection/promotion logic will
  be in a module with unit tests; CLI paths will have integration coverage.

## Project Structure

### Documentation (this feature)

```text
specs/011-promote-winner-profile/
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
|-- promotion.py
|-- cli.py
|-- artifacts.py
`-- serve_profiles.py

tests/
|-- unit/
|   `-- test_promotion.py
`-- integration/
    `-- test_cli_promotion.py

config/profiles/
`-- qwen3-coder-next-awq-recommended.json

docs/
`-- generated promotion summaries under artifacts/ or checked-in docs when requested
```

**Structure Decision**: Keep promotion logic in a focused module, reuse existing
artifact/profile helpers, and expose two CLI commands for preview and generation.

## Experiment and Safety Design

**Objective Family**: Reuse of best-known configuration for a chosen objective,
primarily balanced with throughput/latency alternatives.

**Benchmark Inputs**: Existing ranking artifacts generated from sweep runs;
promotion does not execute prompts or benchmarks.

**Remote Actions**: None. No SSH, no vLLM process lifecycle, and no system
tuning.

**Artifacts**: Promotion preview JSON, recommended profile JSON, promotion
summary Markdown, and provenance embedded in the generated profile.

**Rollback/Cleanup**: Local-only file writes. Existing profile paths are not
overwritten unless explicitly allowed; failed validation writes no output.

## Complexity Tracking

No constitution violations.
