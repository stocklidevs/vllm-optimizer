# Feature Specification: Report Action Recovery After Closing History

**Status**: Completed

**Created**: 2026-05-24

## User Story

As a cockpit user, I want report actions to come back after I close old run
history and complete a new optimization, so closing a stale run does not block
the normal `Load Report` or `Review Report` workflow.

## Requirements

- Closing loaded run history must not permanently hide the main Next Action
  button.
- When a later run completes, the cockpit must be able to reveal a visible
  `Load Report` action.
- When report generation completes, the cockpit must be able to reveal a
  visible `Review Report` action.
- Buttons whose role changes after page load must remain clickable without
  requiring a full page reload.
- The existing close-history behavior must continue to hide stale report panels
  without deleting artifacts.
- Version, documentation, tests, and release metadata must be updated and the
  work committed.

## Success Criteria

- Regression tests prove the loaded-history close flow keeps future report
  loading available.
- Existing cockpit tests continue to pass.
- Release checks pass with the active SpecKit feature pointing to this completed
  spec.
