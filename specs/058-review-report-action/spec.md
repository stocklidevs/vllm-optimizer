# Feature Specification: Review Report Action

## User Story

As a cockpit user, I want a clear `Review Report` action after report
generation so that every instruction in the optimization flow has a visible
button or destination.

## Requirements

- After `Load Report` completes, the next action must become `Review Report`.
- `Review Report` must open the Reports tab.
- In active server mode, `Review Report` must reload the cockpit first so newly
  generated report artifacts are loaded.
- The active server must automatically load `out_dir/report.json` when no
  explicit report path is configured.
- Existing `Start Optimization` and `Load Report` behavior must remain intact.

## Acceptance Criteria

- The rendered cockpit includes browser logic for a `Review Report` next action.
- Active cockpit rendering includes a generated report from `out_dir/report.json`.
- The Reports tab can be selected by the review action.
- Focused tests, full tests, and browser validation pass.
