# Implementation Plan: Workload Leaderboard

**Branch**: `018-workload-leaderboard` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/018-workload-leaderboard/spec.md`

## Summary

Add a local workload-report command that consumes labeled sweep rankings and optional promoted profiles, then produces JSON/Markdown leaderboards with winners, deltas, failed candidate findings, and next actions.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: JSON/Markdown reports and existing artifact files

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Local CLI

**Project Type**: CLI tool

**Performance Goals**: Local report generation completes in under one second for normal artifact sizes.

**Constraints**: Report is read-only and local-only; no GX10 commands.

**Scale/Scope**: Four workload rankings and one promoted profile for the current Qwen sweep set.

## Constitution Check

- **Deterministic Experiments**: PASS. Inputs are explicit artifact paths.
- **Complete Traceability**: PASS. Report records source ranking and profile paths.
- **Remote Safety and Reversibility**: PASS. No remote actions.
- **Objective-Driven Optimization**: PASS. Report focuses on balanced workload winners and promotion status.
- **Testable, Modular Automation**: PASS. Unit and CLI tests cover report behavior.

## Project Structure

```text
src/vllm_optimizer/
|-- workload_report.py
`-- cli.py

tests/
|-- unit/test_workload_report.py
`-- integration/test_cli_workload_report.py
```

**Structure Decision**: Use a separate workload_report module to keep leaderboard logic distinct from the older single comparison report.

## Experiment and Safety Design

**Objective Family**: Workload-specific balanced ranking.

**Benchmark Inputs**: Existing live ranking artifacts and promoted profile artifacts.

**Remote Actions**: None.

**Artifacts**: `artifacts/reports/qwen-workload-leaderboard.json` and `.md`.

**Rollback/Cleanup**: Local report generation only; outputs are ignored by git.

## Complexity Tracking

No constitution violations.
