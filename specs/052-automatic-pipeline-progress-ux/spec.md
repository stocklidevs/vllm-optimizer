# Feature Specification: Automatic Pipeline Progress UX

**Status**: Draft

**Created**: 2026-05-23

## User Story

As a cockpit user, I want to start an optimization flow instead of manually
clicking every internal pipeline stage, so the app feels like an optimizer
rather than a checklist of implementation phases.

## Requirements

- Keep the six internal stages: Plan, Preview, Run, Report, Confirm, Promote.
- Present the main user action as a single optimization flow:
  `Select Tuning Area -> Review Plan -> Start Optimization`.
- Show the six stages as automatic pipeline progress, not as six equal manual
  decisions.
- Show an overall progress bar and per-stage status rows.
- Clearly identify human decision gates:
  - live GX10 execution
  - risky/session tuning opt-in
  - promotion
- Keep promotion explicit and manual.
- Keep existing controller API endpoints and command-copy fallback.
- Keep advanced/manual commands visible for traceability.

## Acceptance Criteria

- The cockpit renders a primary "Start Optimization" flow.
- The cockpit renders an "Automatic Pipeline Progress" panel with stage rows.
- The cockpit labels stages as automatic, waiting, running, complete, or manual
  gate as appropriate.
- Existing active controller operation progress remains available.
- Existing tests continue to pass.

