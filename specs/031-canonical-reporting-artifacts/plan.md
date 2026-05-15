# Implementation Plan: Canonical Reporting Artifacts

**Branch**: `031-canonical-reporting-artifacts` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)

## Summary

Add a canonical report layer that turns existing completed optimizer artifacts into deterministic machine-readable JSON and human-readable Markdown. The report must summarize recommendation status, objective winners, candidate metrics, failure/exclusion state, chart-ready datasets, and provenance links for future web dashboards.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing artifact, sweep ranking, session tuning sweep ranking, and CLI modules

**Storage**: JSON canonical report and Markdown readable report files

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows host consuming local artifact files produced by GX10 workflows

**Project Type**: Python CLI

**Performance Goals**: Report generation from existing artifacts should complete in less than one second for current sweep sizes.

**Constraints**: No live GX10 calls; deterministic output from unchanged inputs; web UI consumes report data without recomputing decisions.

**Scale/Scope**: Cover sweep and session tuning sweep rankings first, with extensible source metadata for pipeline and confirmation reports.

## Constitution Check

- **Deterministic Experiments**: Pass. Reports are generated from retained artifact inputs and sort candidate/chart data deterministically.
- **Complete Traceability**: Pass. Reports retain source artifact paths and candidate trial provenance.
- **Remote Safety and Reversibility**: Pass. Report generation is local-only and performs no GX10 actions.
- **Objective-Driven Optimization**: Pass. Reports preserve objective-specific rankings and recommendation status.
- **Testable, Modular Automation**: Pass. Unit tests cover report building and CLI tests cover file output.

## Project Structure

```text
specs/031-canonical-reporting-artifacts/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- canonical-report.md
`-- tasks.md

src/vllm_optimizer/
|-- canonical_report.py
`-- cli.py

tests/
|-- unit/test_canonical_report.py
`-- integration/test_cli_canonical_report.py
```

**Structure Decision**: Add a focused `canonical_report.py` module and a single CLI command that writes JSON plus optional Markdown. Existing specialized reports remain intact.

## Experiment and Safety Design

**Objective Family**: Reporting and decision traceability for throughput, latency, balanced, and stability-related objectives.

**Benchmark Inputs**: Existing plan, ranking, result, and summary artifacts from completed runs.

**Remote Actions**: None.

**Artifacts**: `canonical-report.json`, optional Markdown report, and links to source plan/ranking/results/summary artifacts.

**Rollback/Cleanup**: No remote cleanup required; generated report files can be regenerated or deleted locally.

## Complexity Tracking

No constitution violations.
