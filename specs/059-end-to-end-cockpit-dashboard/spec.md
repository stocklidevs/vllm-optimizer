# Feature Specification: End-to-End Cockpit Dashboard

**Status**: Completed

**Created**: 2026-05-23

## User Story

As a cockpit user, I want the dashboard to show the whole optimization journey in
plain operational terms, so I always know what is running, what is done, what I
can click next, and which steps are explicit safety gates rather than broken
buttons.

## Requirements

- Spec 059 must become the active SpecKit feature.
- Spec 053 must be visibly marked completed.
- The cockpit overview must provide a useful end-to-end flow map for:
  - Start Optimization
  - Load Report
  - Review Report
  - Confirmation gate
  - Promotion gate
- Dashboard copy must distinguish runnable controller actions from manual or
  gated decisions.
- The cockpit must not render unsupported `confirm` or `promote` controller
  actions as primary clickable actions.
- When a report exists, the primary next action must guide the user to review
  the Reports tab instead of calling an unsupported confirmation endpoint.
- Redundant dashboard summaries should be reduced in favor of operational state:
  what is selected, what is running, what artifact is ready, and what gate is
  next.
- The implementation must remain deterministic, dependency-free, and safe to
  open as static HTML.

## Acceptance Criteria

- Unit tests prove the end-to-end flow map is rendered.
- Unit tests prove report-ready dashboards expose `Review Report` as a tab jump.
- Unit tests prove report-ready primary UI does not call `/api/controller/confirm`.
- Browser validation confirms the dashboard renders meaningful end-to-end
  guidance with no framework overlay or console errors.
- Version and documentation are updated, and the work is committed.
