# Implementation Plan: Automatic Pipeline Progress UX

## Summary

Reframe the cockpit's six implementation stages as an automatic pipeline with
one primary user-facing optimization flow and visible progress.

## Architecture

- Add pipeline progress helper functions to `web_cockpit.py`.
- Derive stage statuses from existing `status` and `report` artifacts.
- Render a new first-viewport panel:
  - primary flow card
  - overall progress bar
  - automatic stage list
  - human gate summary
- Keep workflow step cards as compact execution-stage telemetry.
- Keep command shell and controller buttons for advanced/manual traceability.

## Verification

- Unit tests for automatic pipeline panel and stage labels.
- Focused cockpit/release tests.
- Full pytest suite.
- Browser validation of the generated cockpit.

