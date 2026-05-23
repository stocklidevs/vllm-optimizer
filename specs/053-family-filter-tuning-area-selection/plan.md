# Implementation Plan: Family Filter Tuning Area Selection

## Summary

Fix the cockpit family filter so it behaves like a real selector filter, not
only a tab-grid filter.

## Architecture

- Update `render_left_rail` to render all tuning areas with raw `data-family`
  metadata.
- Add a left-rail empty state.
- Update `applyGroupFilters()` to filter both card collections.
- Add `syncSelectedTuningArea()` to auto-select the first visible left option.
- Keep tab behavior: family filter still opens the Tuning Areas detail tab.

## Verification

- Focused web cockpit tests.
- Full pytest suite.
- Browser validation against generated cockpit HTML.

