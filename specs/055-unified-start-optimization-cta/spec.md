# Feature Specification: Unified Start Optimization CTA

## User Story

As a cockpit user, I want one clear `Start Optimization` action so that I do
not have to manually choose internal pipeline stages such as `Generate Plan`.

## Requirements

- Replace user-facing primary `Generate Plan` calls-to-action with
  `Start Optimization`.
- Keep `Plan` / `Generate Plan` visible only as an internal pipeline stage for
  progress, traceability, and command inspection.
- The right rail `Next Action` card must describe the automatic flow and use a
  `Start Optimization` button.
- The overview command shell must default to the automatic run command, not the
  standalone plan command.
- The existing local controller endpoint hooks, command-copy fallback, live-run
  confirmation behavior, and promotion gate behavior must remain intact.
- Static cockpit output must remain dependency-free.

## Acceptance Criteria

- Initial cockpit state shows `Start Optimization` as the primary right-rail
  action.
- The right rail no longer presents `Generate Plan` as the button or headline.
- The overview command shell presents an automatic optimization command.
- Pipeline progress still lists the plan stage for traceability.
- Focused tests, full tests, and browser validation pass.
