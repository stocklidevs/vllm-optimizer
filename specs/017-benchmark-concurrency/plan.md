# Implementation Plan: Benchmark Concurrency

**Branch**: `017-benchmark-concurrency` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/017-benchmark-concurrency/spec.md`

## Summary

Add prompt-set concurrency to the benchmark runner, use batch duration for concurrent throughput, add a concurrent interactive sweep, run it live, confirm the winner with repeated A/B, and preserve it as a workload-specific concurrent recommended profile.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing CLI modules

**Storage**: JSON prompt sets, sweep definitions, profiles, ignored live artifacts

**Testing**: pytest unit and integration coverage through existing CLI paths

**Target Platform**: Local CLI with session-mutating GX10 benchmark runs

**Project Type**: CLI tool

**Performance Goals**: Concurrent benchmark summaries use wall-clock batch duration for throughput.

**Constraints**: No persistent remote tuning. Workload-specific profile is separate from the default profile.

**Scale/Scope**: One concurrent prompt set, one concurrent sweep, one confirmed concurrent profile.

## Constitution Check

- **Deterministic Experiments**: PASS. Concurrency is recorded in prompt artifacts and benchmark plans.
- **Complete Traceability**: PASS. Promotion stores sweep and A/B confirmation provenance.
- **Remote Safety and Reversibility**: PASS. Live actions are session-mutating only.
- **Objective-Driven Optimization**: PASS. A/B confirmation requires latency and throughput improvements over the noise band.
- **Testable, Modular Automation**: PASS. Prompt loading, summary math, and sweep planning are tested.

## Project Structure

```text
config/prompts/qwen-coding-interactive-concurrent.json
config/sweeps/qwen-high-impact-interactive-concurrent.json
config/profiles/qwen3-coder-next-awq-concurrent-recommended.json
src/vllm_optimizer/benchmark.py
tests/unit/test_benchmark.py
tests/unit/test_sweep.py
```

**Structure Decision**: Concurrency belongs to prompt sets because it describes benchmark workload shape rather than vLLM serve configuration.

## Experiment and Safety Design

**Objective Family**: Concurrent latency, throughput, and balanced ranking.

**Benchmark Inputs**: Concurrent interactive prompt set with concurrency `3`; confirmed default profile; four explicit candidates.

**Remote Actions**: One live concurrent sweep plus two extra benchmark repetitions for repeated A/B confirmation.

**Artifacts**: Plans, previews, live rankings, A/B report, and promotion summary under ignored `artifacts/`.

**Rollback/Cleanup**: Existing benchmark cleanup stops vLLM between trials; workload-specific profile changes are git-reversible.

## Complexity Tracking

No constitution violations.
