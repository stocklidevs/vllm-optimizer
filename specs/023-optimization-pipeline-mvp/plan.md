# Implementation Plan: Optimization Pipeline MVP

**Branch**: `023-optimization-pipeline-mvp` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

## Summary

Add an `optimize-workload` command that orchestrates the existing sweep plan, preview, run, rank, and report primitives for one sweep at a time. The MVP writes deterministic pipeline artifacts and keeps live execution and promotion explicit.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: JSON pipeline plan/summary, sweep plan/preview/ranking, comparison report JSON/Markdown

**Testing**: Unit tests for orchestrator behavior plus CLI integration tests

**Target Platform**: Local CLI; optional remote GX10 live run via existing SSH benchmark harness

## Constitution Check

- **Deterministic Experiments**: PASS. Pipeline inputs and artifact paths are recorded.
- **Complete Traceability**: PASS. Summary links every generated artifact.
- **Remote Safety and Reversibility**: PASS. Plan/preview are local; run mode requires explicit remote config and existing sweep safety gates.
- **Objective-Driven Optimization**: PASS. Ranking/report stages use existing named objectives.
- **Testable, Modular Automation**: PASS. Orchestrator delegates to tested modules and adds tests for stage sequencing.

## Project Structure

```text
src/vllm_optimizer/
|-- optimizer_pipeline.py
`-- cli.py

tests/
|-- unit/test_optimizer_pipeline.py
`-- integration/test_cli_optimizer_pipeline.py
```

## Experiment and Safety Design

**Remote Actions**: Only run mode contacts the GX10, using the existing sequential sweep runner.

**Artifacts**:

- `pipeline-plan.json`
- `pipeline-summary.json`
- `sweep-plan.json`
- `sweep-preview.json`
- `live/results.jsonl`
- `live/ranking.json`
- `report.json`
- `report.md`

**Rollback/Cleanup**: Pipeline writes local artifacts only outside live sweep outputs; remote cleanup stays in the existing benchmark harness.
