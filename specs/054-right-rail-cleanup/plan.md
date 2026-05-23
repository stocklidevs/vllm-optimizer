# Implementation Plan: Right Rail Cleanup

## Summary

Simplify the cockpit right rail by removing deprecated duplicate panels and
moving action feedback to the command shell.

## Architecture

- Update `render_right_rail` to render only next action and execution status.
- Add `#controller-feedback` to the command shell card.
- Adjust tests so controller behavior remains covered without requiring the
  deprecated right-rail controller panel.
- Update version, README, changelog, and lockfile.

## Verification

- Focused cockpit and release-doc tests.
- Full pytest suite.
- Browser validation of generated cockpit HTML.
