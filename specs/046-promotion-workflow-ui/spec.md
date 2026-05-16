# Feature Specification: Promotion Workflow UI

**Feature Branch**: `029-session-tuning-sweeps`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Autonomous roadmap phase for gated promotion workflow visibility

## User Scenarios & Testing

### Primary User Story

As an operator reviewing optimization results in the cockpit, I want a dedicated
promotion workflow view that shows the recommendation, confirmation state, gate,
and exact command hints before any profile promotion is attempted.

### Acceptance Scenarios

1. Given a canonical report and pipeline manifest, when the web cockpit is
   generated, then a Promotion tab summarizes candidate, objective, status,
   required gate, and command hints.
2. Given no canonical report, when the web cockpit is generated, then the
   Promotion tab shows an empty state instead of failing.
3. Given promotion metadata, when the cockpit renders controller controls, then
   promotion remains visibly gated and disabled.

## Requirements

- **REQ-001**: Add a Promotion tab to the cockpit.
- **REQ-002**: Render recommendation candidate, objective, and status from the
  canonical report.
- **REQ-003**: Render promotion gate metadata from the pipeline manifest.
- **REQ-004**: Show deterministic command hints for preview and confirmed
  promotion workflows.
- **REQ-005**: Keep in-browser promotion action disabled; no automatic
  promotion may be triggered by the static cockpit.

## Out of Scope

- Actually promoting a profile from the browser.
- HTTP server execution.
- Changing promotion scoring or confirmation policy.

## Success Criteria

- Web cockpit unit tests cover populated and empty Promotion tab states.
- CLI web cockpit generation continues to pass.
- Full pytest passes.
