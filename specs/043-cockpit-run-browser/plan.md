# Implementation Plan: Cockpit Run Browser

**Branch**: `043-cockpit-run-browser` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)

## Summary

Add a local run browser indexer and render its output inside the web cockpit as a Runs tab, so users can browse existing local artifacts without command-line path hunting.

## Technical Context

**Language/Version**: Python 3.11, static HTML/CSS

**Primary Dependencies**: Existing artifact helpers and web cockpit renderer

**Storage**: JSON run index plus optional HTML

**Testing**: Unit and CLI integration tests

**Target Platform**: Local filesystem artifacts

**Project Type**: Local artifact browser

**Constraints**: Read-only scanning; no live execution; no npm.

## Constitution Check

- **Deterministic Experiments**: Pass. Existing artifacts are indexed without mutation.
- **Complete Traceability**: Pass. Artifact paths are preserved in the index.
- **Remote Safety and Reversibility**: Pass. Local read-only filesystem scan only.
- **Objective-Driven Optimization**: Pass. Runs and reports become easier to inspect.
- **Testable, Modular Automation**: Pass. Indexing and CLI output are tested.

## Project Structure

```text
src/vllm_optimizer/run_browser.py
src/vllm_optimizer/web_cockpit.py
tests/unit/test_run_browser.py
tests/integration/test_cli_run_browser.py
```

## Complexity Tracking

No constitution violations.
