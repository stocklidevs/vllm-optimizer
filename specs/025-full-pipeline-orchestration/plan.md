# Implementation Plan: Full Pipeline Orchestration

**Branch**: `025-full-pipeline-orchestration` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/025-full-pipeline-orchestration/spec.md`

## Summary

Add `optimize-workload --mode full` as the first real end-to-end optimizer pipeline. It reuses existing sweep execution, report generation, profile promotion preview, benchmark runner, and A/B confirmation modules. Full mode remains safety-gated: it requires a remote config and confirmation inputs, and it never writes a confirmed profile unless `--allow-promotion` is supplied and the A/B decision approves the candidate.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Standard library, pytest, uv-managed package

**Storage**: Local JSON, JSONL, Markdown artifacts under `artifacts/`

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows development host orchestrating Linux GX10 over SSH

**Project Type**: Python CLI

**Performance Goals**: Full mode should not add benchmark overhead beyond the requested sweep and confirmation repetitions.

**Constraints**: Deterministic artifact paths; no persistent system tuning; explicit remote config for live work; explicit promotion opt-in.

**Scale/Scope**: One workload sweep and one prompt set per full mode invocation.

## Constitution Check

- **Deterministic Experiments**: Pass. Full mode records inputs and fixed artifact paths for all stages.
- **Complete Traceability**: Pass. Full mode retains sweep, benchmark, report, A/B, and profile artifacts.
- **Remote Safety and Reversibility**: Pass. Only vLLM session lifecycle commands run remotely through existing cleanup paths; promotion is gated.
- **Objective-Driven Optimization**: Pass. The balanced objective selects the candidate and confirmation compares latency and throughput.
- **Testable, Modular Automation**: Pass. Unit tests use injectable benchmark execution; CLI tests cover validation.

## Project Structure

### Documentation

```text
specs/025-full-pipeline-orchestration/
|-- spec.md
|-- plan.md
|-- contracts/
|   `-- optimize-workload-full.md
`-- tasks.md
```

### Source Code

```text
src/vllm_optimizer/
|-- cli.py
`-- optimizer_pipeline.py

tests/
|-- integration/test_cli_optimizer_pipeline.py
`-- unit/test_optimizer_pipeline.py
```

**Structure Decision**: Extend the existing optimizer pipeline module instead of introducing a new orchestrator module so full mode can share artifacts, validation, summary, and confirmation logic with modes 023 and 024.

## Experiment and Safety Design

**Objective Family**: Balanced throughput and latency, followed by repeated A/B confirmation.

**Benchmark Inputs**: Sweep definition, current profile, generated candidate profile, prompt set, repetition count, remote config.

**Remote Actions**: Live sweep execution plus repeated vLLM benchmark lifecycle runs for current and candidate profiles. Existing preflight and cleanup behavior applies.

**Artifacts**: `pipeline-plan.json`, `sweep-plan.json`, `sweep-preview.json`, `live/results.jsonl`, `live/ranking.json`, `report.json`, `report.md`, `confirmation/current-rN/*`, `confirmation/candidate-rN/*`, `confirmation/confirmation-report.json`, candidate profile, optional confirmed profile.

**Rollback/Cleanup**: vLLM sessions are stopped by existing benchmark and sweep cleanup paths. Confirmed profile output is only written after explicit promotion approval.

## Complexity Tracking

No constitution violations.
