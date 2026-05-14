# Implementation Plan: Workload-Aware Sweeps

**Branch**: `016-workload-aware-sweeps` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/016-workload-aware-sweeps/spec.md`

## Summary

Add workload-specific prompt sets and high-impact sweep configs around the confirmed Qwen recommended profile. Extend sweep definitions with explicit candidate lists so high-impact interactions can be tested deliberately without generating a large cartesian search.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: JSON prompt sets, JSON sweep definitions, ignored dry-run/live artifacts

**Testing**: pytest unit tests for prompt loading and sweep planning

**Target Platform**: Local CLI with optional session-mutating GX10 live runs

**Project Type**: CLI tool

**Performance Goals**: Local plan/preview generation should remain fast for bounded explicit candidates; live runs are constrained by existing timeout controls.

**Constraints**: No persistent system tuning. Risky-session candidates require explicit allowance and are documented as such.

**Scale/Scope**: Three workload prompt sets and three high-impact sweep configs.

## Constitution Check

- **Deterministic Experiments**: PASS. Prompt set ids, candidates, seed, repetitions, and profile paths are recorded.
- **Complete Traceability**: PASS. Plans and previews link to prompt sets, profile paths, and candidate overrides.
- **Remote Safety and Reversibility**: PASS. Live runs are session-mutating only and use existing cleanup.
- **Objective-Driven Optimization**: PASS. Each workload ranks throughput, latency, and balanced objectives.
- **Testable, Modular Automation**: PASS. Explicit candidates and prompt sets are covered by unit tests.

## Project Structure

```text
config/prompts/
|-- qwen-coding-interactive.json
|-- qwen-coding-long.json
`-- qwen-tool-json.json

config/sweeps/
|-- qwen-high-impact-interactive.json
|-- qwen-high-impact-long.json
`-- qwen-high-impact-tool-json.json

src/vllm_optimizer/
`-- sweep.py

tests/unit/
|-- test_benchmark.py
`-- test_sweep.py
```

**Structure Decision**: Extend existing sweep definitions because live sweep execution, previewing, and ranking already work for one prompt set at a time.

## Experiment and Safety Design

**Objective Family**: Throughput, latency, and balanced ranking per workload.

**Benchmark Inputs**: Three prompt sets with deterministic temperature zero cases; confirmed recommended profile; explicit high-impact candidate lists.

**Remote Actions**: Optional future `sweep-run` invocations over SSH; no remote action is required for this spec.

**Artifacts**: Local plans and previews under `artifacts/sweeps/qwen-high-impact-*`; future live results and rankings under the same roots.

**Rollback/Cleanup**: Existing sweep runner stops vLLM between trials; local config changes are reversible through git.

## Complexity Tracking

No constitution violations.
