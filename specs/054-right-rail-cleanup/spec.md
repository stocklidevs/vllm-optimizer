# Feature Specification: Right Rail Cleanup

## User Story

As a cockpit user, I want the right rail to show only current operational
guidance so that deprecated duplicate panels do not compete with the primary
workflow.

## Requirements

- Remove the standalone right-rail `Safety Gates` panel from the cockpit.
- Remove the standalone right-rail `Controller` panel from the cockpit.
- Keep the `Next Action` panel as the primary control surface.
- Keep the `Execution` panel for live status feedback.
- Keep controller feedback near the command shell where command execution is
  shown.
- Preserve controller button API hooks and fallback command-copy behavior.
- Preserve safety gate visibility in contextual workflow and promotion areas.

## Acceptance Criteria

- The right rail renders `Next Action` and `Execution`, with no stale
  `Safety Gates` or `Controller` sections.
- Running a controller action still has a feedback target in the page.
- Existing controller endpoint hooks remain present.
- Browser validation confirms the right rail no longer shows the deprecated
  panels.
