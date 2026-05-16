# Implementation Plan: Controller Preview Mode

**Branch**: `044-controller-preview-mode` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)

## Summary

Add a local-only cockpit preview controller action and CLI command. It generates sweep plan and preview artifacts from a selected sweep config while enforcing path and safety gates.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing sweep planner and preview builder

**Storage**: Plan/preview JSON under `artifacts/`

**Testing**: Unit and CLI integration tests

**Target Platform**: Local CLI/controller foundation

**Project Type**: Local action controller

**Constraints**: No live GX10 runs, no promotion, no persistent system changes.

## Constitution Check

- **Deterministic Experiments**: Pass. Existing deterministic sweep planning is reused.
- **Complete Traceability**: Pass. Controller writes explicit plan and preview artifacts.
- **Remote Safety and Reversibility**: Pass. No remote execution is possible.
- **Objective-Driven Optimization**: Pass. Preview prepares objective-driven sweeps without running them.
- **Testable, Modular Automation**: Pass. Controller logic and CLI are tested.

## Project Structure

```text
src/vllm_optimizer/cockpit_controller.py
tests/unit/test_cockpit_controller.py
tests/integration/test_cli_cockpit_controller.py
```

## Complexity Tracking

No constitution violations.
