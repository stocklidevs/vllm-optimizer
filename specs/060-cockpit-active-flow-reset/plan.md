# Implementation Plan: Cockpit Active Flow Reset

**Status**: Implementing

## Summary

Fix the active cockpit UX when a previous report is loaded: fresh runs must
clear stale progress/stages, and the report view must guide the user onward.

## Architecture

- Keep the active server model unchanged.
- Add browser-side reset helpers for pipeline, workflow, and flow-map state.
- Add an Optimization Running next-action state for active runs.
- Add a Reports-tab continuation panel with confirmation and promotion gates.
- Validate the user-visible flow with Playwright using mocked controller
  network responses so the GX10 is not touched.

## Verification

- Focused cockpit tests.
- Full pytest suite.
- Playwright browser validation against served cockpit HTML.
