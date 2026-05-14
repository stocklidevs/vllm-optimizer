# Implementation Plan: Risky Winner Confirmation

**Branch**: `015-risky-winner-confirmation` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/015-risky-winner-confirmation/spec.md`

## Summary

Add a guarded promotion path that refuses to write the default recommended profile unless a repeated A/B confirmation report chooses the risky winner. Generate a reusable risky winner profile from the risky-session sweep ranking, run live repetitions against the current recommended profile, and promote only when the report materially favors the candidate.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: JSON profiles, JSON/Markdown reports, ignored benchmark artifacts

**Testing**: pytest unit and integration tests

**Target Platform**: Windows local workspace with SSH-managed Linux GX10 benchmark target

**Project Type**: CLI tool

**Performance Goals**: Promotion command completes locally in under one second for normal artifacts; live confirmation uses existing benchmark runtime limits.

**Constraints**: Do not mutate GX10 persistently; do not overwrite default profile unless confirmation explicitly approves promotion and `--force` is supplied for existing outputs.

**Scale/Scope**: One risky winner profile, one current recommended control profile, three live repetitions per profile.

## Constitution Check

- **Deterministic Experiments**: PASS. Ranking, profile, prompt set, A/B report paths, noise band, and source summaries are recorded.
- **Complete Traceability**: PASS. Promotion provenance includes ranking and confirmation details.
- **Remote Safety and Reversibility**: PASS. Live benchmark runs are session-mutating only; promotion is local and git-reviewed.
- **Objective-Driven Optimization**: PASS. Objective is balanced latency and throughput with failures as a blocker.
- **Testable, Modular Automation**: PASS. Guarded promotion is unit and CLI tested.

## Project Structure

### Documentation (this feature)

```text
specs/015-risky-winner-confirmation/
|-- spec.md
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
|-- cli.py
`-- promotion.py

config/profiles/
`-- qwen3-coder-next-awq-risky-winner.json

tests/
|-- unit/test_promotion.py
`-- integration/test_cli_promotion.py
```

**Structure Decision**: Extend the existing promotion module and CLI because Spec 011 already owns profile promotion and Spec 013 already owns A/B confirmation artifacts.

## Experiment and Safety Design

**Objective Family**: Balanced latency and throughput, with any increased failure rate blocking promotion.

**Benchmark Inputs**: `config/prompts/qwen-baseline.json`, current recommended profile, risky winner profile, three repetitions each, 1% noise band.

**Remote Actions**: Six `benchmark-run` invocations over SSH against the GX10; each starts and cleans up a vLLM session.

**Artifacts**: Benchmark plans, metrics, summaries under `artifacts/benchmarks/qwen-risky-ab/`; A/B report under `artifacts/reports/`; promotion summary under `artifacts/promotions/`.

**Rollback/Cleanup**: Benchmark runner cleanup stops vLLM sessions. Local profile promotion is reversible through git.

## Complexity Tracking

No constitution violations.
