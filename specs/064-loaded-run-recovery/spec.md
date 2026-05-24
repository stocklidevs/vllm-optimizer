# Feature Specification: Loaded Run Recovery

**Status**: Completed

**Created**: 2026-05-24

## User Story

As a cockpit user, I want to close a previously loaded run from the dashboard so
I can start a fresh optimization without being trapped in stale report-review
state.

## Requirements

- When a report/status artifact is loaded as history, the cockpit must clearly
  label that state as loaded run history.
- The dashboard must expose a `Close Loaded Run` action that hides the loaded
  history in the current browser session.
- Closing loaded history must not delete report, status, run index, or
  controller artifacts from disk.
- A `Start New Optimization` action must remain visible even when loaded report
  history is present.
- Closing loaded history must reset the visible progress copy to a fresh ready
  state so the old run does not look active or completed.
- Existing controller endpoints, command hints, report rendering, and static
  HTML fallback behavior must remain intact.
- Version, documentation, tests, and release metadata must be updated and the
  work committed.

## Success Criteria

- A cockpit opened with a previous report offers both `Close Loaded Run` and
  `Start New Optimization`.
- Clicking `Close Loaded Run` hides report-history panels, disables the close
  control, reveals a fresh-ready message, and leaves start controls enabled.
- Rendered desktop and mobile validation show no broken layout or console
  errors in the loaded-history recovery flow.
