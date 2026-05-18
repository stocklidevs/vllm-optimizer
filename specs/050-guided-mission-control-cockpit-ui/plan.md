# Implementation Plan: Guided Mission Control Cockpit UI

## Summary

Reshape the cockpit into a guided mission-control experience while preserving
the existing Python HTML renderer, controller API hooks, and deterministic
artifact contracts.

## Architecture

- Extend `web_cockpit.py` with small workflow helpers:
  - workflow step metadata
  - current action inference
  - next-action guidance
  - command shell rendering
- Reorder the page so the workflow strip appears before secondary tabs.
- Move the active-step explanation and command preview into the overview first
  viewport.
- Promote the right rail controller into a Next Action panel.
- Keep existing tab panels and data source rendering intact.

## Data Flow

- Inputs remain catalog, manifest, status, report, run index, and source paths.
- Workflow state is inferred conservatively from available artifacts:
  - no manifest: Plan is current
  - manifest without completed status/report: Preview or Run remains next
  - report without confirmation: Confirm is next
  - confirmed report/promotion gate: Promote remains gated
- Controller command hints are still read from the manifest when present, with
  existing fallback commands otherwise.

## Verification

- Add targeted unit tests for workflow stepper and Next Action rendering.
- Run focused cockpit tests.
- Run full pytest suite.
- Validate the generated cockpit in-browser at desktop and mobile widths.

