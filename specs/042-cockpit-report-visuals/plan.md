# Implementation Plan: Cockpit Report Visuals

**Branch**: `042-cockpit-report-visuals` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)

## Summary

Enhance the static cockpit Reports tab with artifact-driven visual summaries for recommendation, candidate throughput, latency, failure rates, rationale, and next actions.

## Technical Context

**Language/Version**: Python 3.11, generated HTML/CSS

**Primary Dependencies**: Existing `web_cockpit` renderer

**Storage**: Static HTML output

**Testing**: Unit renderer tests plus existing CLI integration tests

**Target Platform**: Browser-openable local file

**Project Type**: Static report visualization

**Constraints**: No npm, no chart libraries, no browser-side recomputation of recommendations.

## Constitution Check

- **Deterministic Experiments**: Pass. Visuals consume canonical report metrics.
- **Complete Traceability**: Pass. Report provenance remains visible.
- **Remote Safety and Reversibility**: Pass. The cockpit remains read-only.
- **Objective-Driven Optimization**: Pass. Objective, winner, metrics, and failure summaries are visible.
- **Testable, Modular Automation**: Pass. Markup and CLI generation are tested.

## Project Structure

```text
src/vllm_optimizer/web_cockpit.py
tests/unit/test_web_cockpit.py
```

## Complexity Tracking

No constitution violations.
