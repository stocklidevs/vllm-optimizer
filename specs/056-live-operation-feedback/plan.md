# Implementation Plan: Live Operation Feedback

## Summary

Make active cockpit runs visibly alive by wiring job state into the right-rail
execution panel and adding elapsed-time heartbeat progress from the server.

## Architecture

- Add live execution DOM targets to the right rail.
- Update browser-side `renderOperationResult()` to write both the detailed
  operation panel and right-rail execution summary.
- Add runtime-derived progress and elapsed seconds to `CockpitJobStore.get()`
  for running and cancel-requested jobs.
- Keep cancellation and static command-copy behavior unchanged.
- Update docs, version, and tests.

## Verification

- Focused cockpit server/web cockpit tests.
- Full pytest suite.
- Browser validation of generated active cockpit behavior.
