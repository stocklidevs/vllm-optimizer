# Implementation Plan: Web Cockpit Interface

**Branch**: `040-web-cockpit-interface` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)

## Summary

Add a local `web-cockpit` command that generates a high-tech standalone static HTML dashboard from existing deterministic artifacts: knob catalog, optional pipeline control manifest, optional execution status, and optional canonical report.

## Technical Context

**Language/Version**: Python 3.11, standalone HTML/CSS

**Primary Dependencies**: Existing artifact helpers and generated JSON contracts

**Storage**: Static HTML output

**Testing**: Unit render tests and CLI integration tests

**Target Platform**: Local browser-openable artifact

**Project Type**: Python CLI static web generation

**Constraints**: No npm for this spec; no browser-triggered live actions; no external assets.

## Constitution Check

- **Deterministic Experiments**: Pass. The UI consumes deterministic artifacts.
- **Complete Traceability**: Pass. Source artifact paths are rendered in the cockpit.
- **Remote Safety and Reversibility**: Pass. The cockpit is read-only.
- **Objective-Driven Optimization**: Pass. Reports and objectives remain artifact-driven.
- **Testable, Modular Automation**: Pass. Rendering and CLI output are tested.

## Project Structure

```text
src/vllm_optimizer/web_cockpit.py
tests/unit/test_web_cockpit.py
tests/integration/test_cli_web_cockpit.py
```

## Complexity Tracking

No constitution violations.
