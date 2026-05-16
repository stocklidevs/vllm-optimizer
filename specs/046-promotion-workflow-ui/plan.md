# Implementation Plan: Promotion Workflow UI

## Summary

Extend the static `web-cockpit` artifact renderer with a dedicated Promotion
tab. The view is advisory and gated: it reads canonical report and manifest
metadata, displays the promotion workflow, and shows command hints without
triggering promotion.

## Technical Context

- Language: Python 3.11
- UI: generated static HTML/CSS/JS, no npm dependencies
- Existing module: `src/vllm_optimizer/web_cockpit.py`
- Tests: pytest unit and CLI integration

## Architecture

- Add a Promotion tab button.
- Add `render_promotion_workflow(report, manifest)`.
- Use canonical report recommendation and manifest promotion metadata.
- Preserve disabled controller action semantics.

## Verification

- Focused web cockpit tests.
- Version/release documentation tests.
- Full pytest suite.
