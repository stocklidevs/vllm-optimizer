# Implementation Plan: FP8 Ninja Rerun

**Branch**: `019-fp8-ninja-rerun` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/019-fp8-ninja-rerun/spec.md`

## Summary

Expose the configured vLLM executable directory on the remote benchmark `PATH`, add FP8 rerun sweep configs, run live risky-session FP8 workload probes on the GX10, and refresh the workload leaderboard.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: JSON sweep configs, ignored plan/preview/live artifacts, Markdown/JSON reports

**Testing**: pytest unit and integration suite

**Target Platform**: Local CLI coordinating remote GX10 over SSH

**Project Type**: CLI tool

**Performance Goals**: No added benchmark overhead beyond a shell `PATH` export.

**Constraints**: FP8 remains risky-session only; persistent Linux/NVIDIA changes are out of scope.

**Scale/Scope**: Three FP8 workload reruns and one refreshed workload report.

## Constitution Check

- **Deterministic Experiments**: PASS. Sweep configs and plans fully define each rerun.
- **Complete Traceability**: PASS. Reports point to ranking and live artifact paths.
- **Remote Safety and Reversibility**: PASS. Only session-scoped serve commands run remotely.
- **Objective-Driven Optimization**: PASS. Results are ranked by existing workload objectives.
- **Testable, Modular Automation**: PASS. PATH rendering and sweep gating are covered by tests.

## Project Structure

```text
src/vllm_optimizer/
`-- benchmark.py

config/sweeps/
|-- qwen-fp8-rerun-interactive.json
|-- qwen-fp8-rerun-long.json
`-- qwen-fp8-rerun-tool-json.json

tests/unit/
|-- test_benchmark.py
`-- test_sweep.py
```

**Structure Decision**: Keep the PATH export in benchmark script rendering and model the rerun as sweep configuration, not as a new command.

## Experiment and Safety Design

**Objective Family**: Workload-specific balanced ranking, with throughput and latency rankings retained.

**Benchmark Inputs**: Existing Qwen workload prompt sets and recommended serve profile.

**Remote Actions**: Session-scoped vLLM serve launches over SSH with cleanup.

**Artifacts**: FP8 rerun plans/previews/live rankings under `artifacts/sweeps/`, refreshed workload report under `artifacts/reports/`.

**Rollback/Cleanup**: Remote serve cleanup is already part of the benchmark harness; local artifacts are ignored by git.

## Complexity Tracking

No constitution violations.
