# Implementation Plan: Impactful Sweep Bundles

**Branch**: `036-impactful-sweep-bundles` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)

## Summary

Add two curated sweep definitions for higher-impact tuning: KV/cache memory tradeoffs and tool/JSON prefix-prefill behavior. Validate them through existing planning and preview tests without live GX10 execution.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing sweep config loader, planner, and preview commands

**Storage**: JSON sweep definition files

**Testing**: pytest integration tests through CLI

**Target Platform**: Windows host generating local plans/previews

**Project Type**: Python CLI config expansion

**Constraints**: No live GX10 run; risky-session candidates gated by existing allow flag.

## Constitution Check

- **Deterministic Experiments**: Pass. New sweep definitions include fixed seeds and explicit candidates.
- **Complete Traceability**: Pass. Config files become reproducibility inputs.
- **Remote Safety and Reversibility**: Pass. Only dry-run planning is tested; risky flags remain gated.
- **Objective-Driven Optimization**: Pass. Throughput, latency, and balanced objectives are included.
- **Testable, Modular Automation**: Pass. CLI tests validate planning and preview behavior.

## Project Structure

```text
config/sweeps/
|-- qwen-kv-cache-memory-tradeoff.json
`-- qwen-prefix-prefill-tool-json.json

tests/integration/
`-- test_cli_impactful_sweeps.py
```

## Experiment and Safety Design

**Objective Family**: KV/cache memory behavior and tool/JSON structured-output performance.

**Benchmark Inputs**: Existing Qwen profile and prompt sets.

**Remote Actions**: None in this feature.

**Artifacts**: Future sweep plans, previews, results, and rankings from existing commands.

**Rollback/Cleanup**: Existing sweep cleanup applies during later live runs.

## Complexity Tracking

No constitution violations.
