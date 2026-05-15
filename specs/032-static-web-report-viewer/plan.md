# Implementation Plan: Static Web Report Viewer

**Branch**: `032-static-web-report-viewer` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)

## Summary

Add a local static HTML viewer generator for canonical report JSON. The first web UI phase renders recommendation, ranking, metrics, chart-like comparisons, next actions, and provenance without adding a server or recomputing report decisions.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing artifact and CLI modules; no web framework dependency

**Storage**: Standalone HTML file generated from canonical JSON

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows host opening local HTML files

**Project Type**: Python CLI generating static web artifacts

**Performance Goals**: Generate current report viewer files in under one second.

**Constraints**: No live GX10 calls; no network assets; deterministic HTML from unchanged canonical report input.

**Scale/Scope**: One report per generated HTML file.

## Constitution Check

- **Deterministic Experiments**: Pass. Viewer is generated from canonical report artifacts only.
- **Complete Traceability**: Pass. Viewer displays canonical provenance.
- **Remote Safety and Reversibility**: Pass. No remote actions.
- **Objective-Driven Optimization**: Pass. Viewer displays objective and recommendation from canonical report.
- **Testable, Modular Automation**: Pass. Unit and CLI tests cover rendering.

## Project Structure

```text
specs/032-static-web-report-viewer/
|-- spec.md
|-- plan.md
`-- tasks.md

src/vllm_optimizer/
|-- web_report.py
`-- cli.py

tests/
|-- unit/test_web_report.py
`-- integration/test_cli_web_report.py
```

## Experiment and Safety Design

**Objective Family**: Web presentation of canonical objective data.

**Benchmark Inputs**: Canonical report JSON.

**Remote Actions**: None.

**Artifacts**: Generated standalone HTML report viewer.

**Rollback/Cleanup**: Generated viewer can be regenerated or deleted locally.

## Complexity Tracking

No constitution violations.
