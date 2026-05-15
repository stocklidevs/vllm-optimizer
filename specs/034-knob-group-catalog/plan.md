# Implementation Plan: Knob Group Catalog

**Branch**: `034-knob-group-catalog` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)

## Summary

Add a local knob group catalog generator and optional static selector preview. The catalog classifies existing sweep and tuning configs by family and safety tier so a future web UI can offer clear, gated choices.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing artifact helpers and config directories

**Storage**: JSON catalog and optional standalone HTML selector

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows host reading repository config files

**Project Type**: Python CLI generating local UI artifacts

**Constraints**: No GX10 calls; deterministic ordering; conservative safety classification.

## Constitution Check

- **Deterministic Experiments**: Pass. Catalog is generated from config paths in sorted order.
- **Complete Traceability**: Pass. Every group links to config path.
- **Remote Safety and Reversibility**: Pass. Catalog generation is local-only and labels side effects.
- **Objective-Driven Optimization**: Pass. Groups record inferred objective/workload family.
- **Testable, Modular Automation**: Pass. Unit and CLI tests cover classification and rendering.

## Project Structure

```text
specs/034-knob-group-catalog/
|-- spec.md
|-- plan.md
`-- tasks.md

src/vllm_optimizer/
|-- knob_catalog.py
`-- cli.py

tests/
|-- unit/test_knob_catalog.py
`-- integration/test_cli_knob_catalog.py
```

## Experiment and Safety Design

**Objective Family**: Knob family selection and safety classification.

**Benchmark Inputs**: Local sweep, session tuning sweep, and discovery config paths.

**Remote Actions**: None during catalog generation.

**Artifacts**: `knob-groups.json` and optional `knob-groups.html`.

**Rollback/Cleanup**: Generated catalog files can be regenerated or deleted locally.

## Complexity Tracking

No constitution violations.
