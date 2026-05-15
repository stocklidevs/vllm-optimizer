# Implementation Plan: Release Readiness Check

**Branch**: `038-release-readiness-check` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)

## Summary

Add a deterministic local `release-check` command that reports release readiness across version metadata, README badge, active SpecKit feature files, artifact contracts, and release-facing docs.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Python standard library, existing artifact writer helpers

**Storage**: JSON plus optional Markdown readiness report

**Testing**: Unit tests for check logic and CLI integration tests

**Target Platform**: Local CLI

**Project Type**: Python CLI release metadata

**Constraints**: No live GX10 commands, no package publishing, no external services.

## Constitution Check

- **Deterministic Experiments**: Pass. The check is deterministic except for generation timestamp.
- **Complete Traceability**: Pass. Each check records status, severity, message, and paths.
- **Remote Safety and Reversibility**: Pass. The command is local-only and read-only except output files.
- **Objective-Driven Optimization**: Pass. Release readiness supports reliable automated optimization usage.
- **Testable, Modular Automation**: Pass. Check logic and CLI output are tested.

## Project Structure

```text
src/vllm_optimizer/release_check.py
tests/unit/test_release_check.py
tests/integration/test_cli_release_check.py
```

## Release Design

**Status Model**: `pass` when all error-severity checks pass, otherwise `fail`.

**Initial Checks**: Version metadata, README badge, active SpecKit files, artifact contracts, README release workflow references, and essential project files.

## Complexity Tracking

No constitution violations.
