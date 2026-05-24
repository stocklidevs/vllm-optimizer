# Implementation Plan: Completed Run Pipeline Sync

## Summary

Synchronize the cockpit's pipeline and next-action display with completed
controller job results.

## Architecture

- Add stable DOM ids/data attributes to the pipeline progress bar, caption, and
  next-action controls.
- Add browser-side job result parsing for `result.pipeline_summary` and
  `completed_stages`.
- Update pipeline stage classes and progress after `renderOperationResult()`.
- Update the next-action card to `Load Report` after run completion.
- Add a server-side `report` controller action using `optimize-workload --mode
  report`.
- Update docs, version, and tests.

## Verification

- Focused cockpit server/web cockpit tests.
- Full pytest suite.
- Browser validation with simulated completed job state.
