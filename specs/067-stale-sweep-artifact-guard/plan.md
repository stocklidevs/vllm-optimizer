# Implementation Plan: Stale Sweep Artifact Guard

**Status**: Completed

## Summary

Prevent reused cockpit output directories from showing or reporting stale sweep
artifacts. The immediate bug was a C8-configured cockpit reusing
`qwen-small-sweep` ranking/report artifacts, producing a misleading 50 tok/s
Performance result.

## Architecture

- Validate cached sweep plans by `sweep_id` before reuse.
- Validate cached rankings by `sweep_id` before reuse.
- Regenerate rankings only from results that match the current sweep plan.
- Raise an explicit stale-artifact error when old results/rankings cannot be
  reconciled with the current sweep.
- Suppress implicit active cockpit reports when output-directory artifacts do
  not match the configured sweep.

## Verification

- Red/green tests for stale ranking rejection and stale active-report hiding.
- Focused optimizer pipeline and cockpit server tests.
- Full pytest suite.
- Release check.
- Local browser validation against stale `cockpit-active` artifacts and valid
  C8 artifacts.
