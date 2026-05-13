# Implementation Plan: Run Comparison Report

**Branch**: `007-run-comparison-report` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/007-run-comparison-report/spec.md`

## Summary

Add a local-only report command that reads existing baseline, sweep, and
repeated sweep ranking artifacts, normalizes candidate summaries, picks the
headline recommendation, and writes concise JSON plus optional Markdown.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library, pytest, existing artifact helpers

**Storage**: Local JSON and Markdown files under ignored `artifacts/`

**Testing**: pytest unit and integration tests

**Target Platform**: Local controller; no remote target

**Project Type**: Python CLI

**Performance Goals**: Generate reports from small artifact files in under one
second

**Constraints**: Local-only, no SSH, no benchmark execution, preserve source
artifact references

**Scale/Scope**: Baseline summary plus one one-shot sweep ranking and one
repeated sweep ranking

## Constitution Check

- **Deterministic Experiments**: PASS. Report records all input artifact paths
  and derives deterministic recommendations from existing data.
- **Complete Traceability**: PASS. Candidate rows link back to source artifact
  paths.
- **Remote Safety and Reversibility**: PASS. Feature has no remote actions.
- **Objective-Driven Optimization**: PASS. Recommendations name the objective
  and metrics used.
- **Testable, Modular Automation**: PASS. Parsing, recommendation, Markdown,
  and CLI paths are unit/integration testable.

## Project Structure

```text
src/vllm_optimizer/
|-- report.py
|-- cli.py
tests/
|-- unit/test_report.py
`-- integration/test_cli_report.py
specs/007-run-comparison-report/
```

**Structure Decision**: Add a focused `report.py` module and small CLI wrapper.

## Experiment and Safety Design

**Objective Family**: Reporting and decision support for existing optimizer
artifacts

**Benchmark Inputs**: Existing artifact paths only

**Remote Actions**: None

**Artifacts**: JSON report, optional Markdown report

**Rollback/Cleanup**: Not applicable; report generation only writes requested
local outputs

## Complexity Tracking

No constitution violations.
