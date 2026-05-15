# Implementation Plan: Artifact Contract Catalog

**Branch**: `037-artifact-contract-catalog` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)

## Summary

Add a deterministic local artifact contract catalog command for release polish. The catalog records stable artifact schema versions and the fields future web/UI consumers can rely on.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing CLI and artifact writer helpers

**Storage**: JSON catalog plus optional Markdown reference

**Testing**: Unit coverage for catalog structure and integration coverage through CLI

**Target Platform**: Local CLI

**Project Type**: Python CLI/report metadata

**Constraints**: No GX10 access, no live artifacts required, no report payload changes.

## Constitution Check

- **Deterministic Experiments**: Pass. The catalog is deterministic except for generation timestamp.
- **Complete Traceability**: Pass. Contracts list producer commands and consumers.
- **Remote Safety and Reversibility**: Pass. The feature is local-only.
- **Objective-Driven Optimization**: Pass. Contracts support reliable reporting and downstream objective views.
- **Testable, Modular Automation**: Pass. Structure and CLI outputs are covered by tests.

## Project Structure

```text
src/vllm_optimizer/artifact_contracts.py
tests/unit/test_artifact_contracts.py
tests/integration/test_cli_artifact_contracts.py
```

## Release Design

**Contract Scope**: Stable release-facing artifacts that dashboards and users consume directly.

**Initial Contracts**: canonical report, execution status, knob group catalog, and pipeline control manifest.

**Markdown Output**: A compact reference with schema version, producer, stability, required fields, optional fields, and consumers.

## Complexity Tracking

No constitution violations.
