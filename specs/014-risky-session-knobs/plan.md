# Implementation Plan: Risky Session Knobs

**Branch**: `014-risky-session-knobs` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-risky-session-knobs/spec.md`

## Summary

Extend serve flag rendering and sweep planning with risk-tiered vLLM flags.
Safe flags retain existing behavior. Risky-session flags can be planned and
previewed but remain blocked unless explicitly allowed, and live sweep execution
requires a separate `--allow-risky-session-flags` opt-in. Add a small
recommended-profile sweep for `block_size` and `enforce_eager`, run it live,
rank it, then version and commit.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Standard library only; existing sweep, benchmark, and serve-profile modules.

**Storage**: JSON sweep configs, plans, previews, live results, and rankings.

**Testing**: pytest unit and CLI integration tests.

**Target Platform**: Local controller repository with optional GX10 live sweep.

**Project Type**: Python CLI/library.

**Performance Goals**: Plan/preview under 10 seconds; small live sweep of 4 candidates.

**Constraints**: No persistent/system flags; live risky sweeps require explicit CLI opt-in.

**Scale/Scope**: Initial risky-session sweep covers `block_size` and `enforce_eager` only.

## Constitution Check

- **Deterministic Experiments**: PASS. Sweep configs record profile, prompts, parameters, seed, and candidate order.
- **Complete Traceability**: PASS. Plans/previews/results/rankings are retained with risk metadata.
- **Remote Safety and Reversibility**: PASS. Risky-session flags are session-local and require opt-in; blocked flags remain refused.
- **Objective-Driven Optimization**: PASS. Existing throughput/latency/balanced ranking applies.
- **Testable, Modular Automation**: PASS. Unit and CLI tests cover risk gates and rendering.

## Project Structure

```text
src/vllm_optimizer/
|-- serve_profiles.py
|-- sweep.py
`-- cli.py

config/sweeps/
`-- qwen-risky-session-small.json

tests/
|-- unit/
|   |-- test_serve_profiles.py
|   `-- test_sweep.py
`-- integration/
    `-- test_cli_sweep.py
```

## Experiment and Safety Design

**Objective Family**: Throughput, latency, and balanced.

**Benchmark Inputs**: Confirmed recommended Qwen profile and baseline prompt set.

**Remote Actions**: Planning/preview local-only. Live sweep uses existing
managed benchmark lifecycle and cleanup.

**Artifacts**: Risky sweep plan, preview, live results, and ranking.

**Rollback/Cleanup**: Existing sweep/benchmark cleanup stops vLLM after each trial.

## Complexity Tracking

No constitution violations.
