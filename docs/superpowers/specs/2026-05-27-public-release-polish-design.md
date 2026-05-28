# Public Release Polish Design

## Goal

Make the public alpha easier to understand in the first minute without changing
optimizer behavior. The release branch should show what the project does, how
to run it safely, what the cockpit looks like, what results mean, and how
external users should report issues or model-validation evidence.

## Scope

- README first-impression polish.
- Cockpit screenshot asset generated from repository configs.
- Release notes draft for the GitHub release body.
- Issue templates for bugs and model validation reports.
- Release-check coverage for the new public-facing files.

## Non-Goals

- No live GX10 execution.
- No cockpit behavior changes.
- No new runtime dependencies.
- No public publishing, tagging, or merge to `main`.

## Validation

- Public docs tests.
- Version tests.
- Release-check.
- Full pytest.
- Pinned npm install and high-severity audit.
