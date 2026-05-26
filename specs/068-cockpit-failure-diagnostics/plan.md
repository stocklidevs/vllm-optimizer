# Implementation Plan: Cockpit Failure Diagnostics

**Status**: Completed

## Summary

Turn bare active-cockpit failures into recoverable operational feedback. The
server now persists recent job state and failed job diagnostics, while the web
cockpit renders the likely cause, next steps, artifact paths, and failed trial
context.

## Architecture

- Persist `controller-last-job.json` for active cockpit jobs.
- Persist `controller-failure.json` for failed jobs.
- Add a recent-job server path backed by memory first, disk second.
- Build failure diagnostics from the exception, configured output directory,
  and `live/results.jsonl` when it exists.
- Hydrate the web operation panel from the recent-job endpoint after page load.
- Keep static cockpit mode tolerant of missing recent-job API support.

## Verification

- Red/green tests for failed job persistence and diagnostics.
- Red/green tests for recent persisted job recovery.
- Web rendering tests for failure diagnostics and recent-job hydration hooks.
- Full pytest suite.
- Release check.
- Local browser validation with a seeded failed job.
