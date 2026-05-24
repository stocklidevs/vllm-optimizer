# Feature Specification: Family Filter Tuning Area Selection

**Status**: Completed

**Created**: 2026-05-23

## User Story

As a cockpit user, I want family filters to change the visible tuning areas in
the left selector, so choosing `risky-session` does not leave me staring at
safe-session cards.

## Requirements

- Family filter buttons must filter both:
  - the left-rail tuning area selector
  - the Tuning Areas tab grid
- Left-rail tuning area cards must carry raw family metadata.
- When a family filter is applied, the cockpit should auto-select the first
  visible tuning area for that family.
- If no tuning areas match, the left rail should show a clear empty state.
- Existing search behavior in the Tuning Areas tab must continue to work.
- Static HTML behavior and active cockpit server behavior must remain
  dependency-free.

## Acceptance Criteria

- Unit tests prove left-rail tuning areas include `data-family`.
- Unit tests prove the filtering JavaScript targets both `.group-card` and
  `.tuning-area-option`.
- Unit tests prove the selection behavior updates when filters change.
- Browser validation confirms clicking `risky-session` hides safe-session cards
  from the left selector and selects the risky tuning area.
