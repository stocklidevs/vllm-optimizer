# Implementation Plan: Loaded Run Recovery

**Status**: Completed

## Summary

Fix the cockpit state trap where a loaded canonical report was treated as the
only current action. The page now distinguishes loaded history from active
execution and gives the user a local close-history path plus a fresh start
action.

## Architecture

- Detect loaded artifact state with the existing report/status helper.
- Render loaded-run recovery controls near the primary command surfaces.
- Mark report-history sections with stable data attributes so the browser can
  hide them without mutating artifacts.
- Add a fresh-ready decision card that becomes visible after loaded history is
  closed.
- Preserve controller `run` hooks so `Start New Optimization` works through
  `cockpit-server` and falls back to deterministic command-copy behavior in
  static HTML.

## Verification

- Regression unit test for a report-loaded dashboard exposing close and fresh
  start controls.
- Focused cockpit renderer tests.
- Rendered Playwright validation for desktop and mobile loaded-run recovery.
- Version, docs, release-check, and full pytest verification.
