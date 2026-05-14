# Implementation Plan: Pipeline Confirmation Stage

**Branch**: `024-pipeline-confirmation-stage` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

## Summary

Extend `optimize-workload` with an explicit `confirm` mode that generates a candidate profile from the pipeline ranking, builds an A/B confirmation report from repeated summaries, and optionally promotes only when `--allow-promotion` is provided and the report approves switching.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, pytest, existing A/B and promotion modules

**Storage**: Candidate profile JSON, confirmation report JSON/Markdown, optional confirmed profile JSON and promotion summary

**Testing**: Unit tests for confirmation orchestration and CLI integration tests

**Target Platform**: Local CLI; confirmation summaries may come from prior live GX10 benchmark runs

## Constitution Check

- **Deterministic Experiments**: PASS. Confirmation inputs are explicit summary paths and ranking paths.
- **Complete Traceability**: PASS. Candidate, report, and promoted profile retain source provenance.
- **Remote Safety and Reversibility**: PASS. This MVP confirm mode is local-only and does not run live benchmarks.
- **Objective-Driven Optimization**: PASS. Existing A/B decision gate compares latency, throughput, and failure rate.
- **Testable, Modular Automation**: PASS. Uses existing tested A/B and promotion modules with orchestration tests.

## Project Structure

```text
src/vllm_optimizer/
|-- optimizer_pipeline.py
`-- cli.py

tests/
|-- unit/test_optimizer_pipeline.py
`-- integration/test_cli_optimizer_pipeline.py
```

## Experiment and Safety Design

**Remote Actions**: None in this MVP confirmation stage.

**Artifacts**:

- `candidate-profile.json`
- `confirmation-report.json`
- `confirmation-report.md`
- `confirmed-profile.json` when promotion is explicitly allowed and approved
- `promotion-summary.md` when promotion is explicitly allowed and approved

**Rollback/Cleanup**: Existing profile outputs are only overwritten when explicit force-like pipeline behavior is invoked through `--allow-promotion` and the A/B report approves switching.
