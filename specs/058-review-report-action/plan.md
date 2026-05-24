# Implementation Plan: Review Report Action

## Summary

Complete the visible process loop by turning report completion into an explicit
`Review Report` action that opens the Reports tab with the freshly generated
artifact loaded.

## Architecture

- Update active cockpit rendering to use `out_dir/report.json` as the default
  generated report artifact.
- Add browser-side next-action state for `Review Report`.
- Add session-backed tab restoration so the active page can reload into the
  Reports tab after generation.
- Update docs, version, and tests.

## Verification

- Focused cockpit server/web cockpit tests.
- Full pytest suite.
- Browser validation against generated cockpit HTML.
