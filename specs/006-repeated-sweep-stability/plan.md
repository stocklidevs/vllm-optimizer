# Implementation Plan: Repeated Sweep Stability

**Branch**: `006-repeated-sweep-stability` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-repeated-sweep-stability/spec.md`

## Summary

Extend the existing Qwen sweep workflow with a `repetitions` field, stable
candidate ids, repeated trial ids, per-candidate aggregate metrics, and
stability-aware rankings. Add a narrowed top-two sweep config for 0.86/32768
and 0.90/32768, then run it live sequentially on the GX10.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library, pytest, existing sweep and
benchmark modules

**Storage**: Local JSON/JSONL artifacts under ignored `artifacts/`

**Testing**: pytest unit and integration tests

**Target Platform**: Local Windows controller; remote GX10 through Tailscale SSH
for approved live runs

**Project Type**: Python CLI

**Performance Goals**: Local repeated plan and aggregate ranking in under one
second for small sweeps

**Constraints**: Sequential live execution, no persistent system tuning, no
package installs, no concurrent load testing

**Scale/Scope**: Two to four candidates with a small fixed repetition count for
the first stability pass

## Constitution Check

- **Deterministic Experiments**: PASS. Candidate ids and repeated trial ids are
  deterministic from sweep inputs.
- **Complete Traceability**: PASS. Aggregate rows link to every source
  repetition artifact.
- **Remote Safety and Reversibility**: PASS. Live runs reuse session-mutating
  benchmark lifecycle and cleanup.
- **Objective-Driven Optimization**: PASS. Rankings name throughput, latency,
  and balanced objectives with stability tie-breakers.
- **Testable, Modular Automation**: PASS. Planning, aggregation, ranking, and
  CLI paths are testable locally.

## Project Structure

```text
config/sweeps/qwen-top2-repeated.json
src/vllm_optimizer/sweep.py
src/vllm_optimizer/cli.py
tests/unit/test_sweep.py
tests/integration/test_cli_sweep.py
specs/006-repeated-sweep-stability/
```

**Structure Decision**: Extend the existing sweep module rather than adding a
second repeated-sweep module, because repeated trials are a direct refinement
of the current sweep model.

## Experiment and Safety Design

**Objective Family**: Repeated-run stability for session-level Qwen vLLM
optimization

**Benchmark Inputs**: Qwen baseline prompt set, top-two parameter candidates,
three repetitions, existing baseline summary reference

**Remote Actions**: Dry-run paths remain local. Live execution runs each
repetition sequentially through the existing benchmark lifecycle.

**Artifacts**: Repeated sweep plan, preview, results JSONL, per-repetition
benchmark artifacts, aggregate ranking, cleanup evidence

**Rollback/Cleanup**: Existing benchmark cleanup after every started
repetition; persistent changes are blocked.

## Complexity Tracking

No constitution violations.
