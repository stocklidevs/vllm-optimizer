# Feature Specification: Model and Objective Selection

**Status**: Completed

**Created**: 2026-05-24

## User Story

As a cockpit user, I want to choose the model/profile and optimization target
before running a tuning area so recommendations are framed for performance,
stability, tool use, or a balanced objective.

## Requirements

- The cockpit must expose model/profile context as a first-class selection area.
- The static `web-cockpit` command must accept one or more serve profile JSON
  paths and render them without requiring a server.
- The active cockpit launcher/server must be able to pass profile paths through
  to the rendered cockpit.
- The cockpit must expose optimization target choices:
  - Performance,
  - Stability,
  - Tool Use,
  - Balanced.
- Target selection is local UI state in this spec. It must not change optimizer
  ranking semantics until a later scoring/campaign spec wires it into planning.
- The selected target must be visible in the decision strip and primary flow so
  users understand what the current run is trying to optimize.
- Tool Use must be clearly marked as a target foundation whose deeper
  correctness metrics require future tool/JSON benchmark fields.
- Version, documentation, tests, and release metadata must be updated and the
  work committed.

## Acceptance Criteria

- `web-cockpit --profile PROFILE.json ...` renders a model selector with model
  name, served model name, profile id, tool parser, and current profile role.
- Cockpit launch/server defaults include known local profile files when present.
- Clicking target cards updates selected target text in the decision strip and
  primary flow without a page reload.
- Existing cockpit tests continue to pass.
- Release check and full test suite pass.
