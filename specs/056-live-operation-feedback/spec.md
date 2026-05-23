# Feature Specification: Live Operation Feedback

## User Story

As a cockpit user, I want immediate visible feedback after starting
optimization so I can tell whether work is running, how long it has been
running, and whether I can request cancellation.

## Requirements

- Starting an active controller action must update visible operation feedback
  near the top/right of the cockpit immediately after confirmation.
- The right-rail `Execution` panel must show the active job status and progress
  instead of remaining a static artifact summary.
- Long-running jobs must return elapsed-time and heartbeat progress while the
  background thread is still running.
- The existing operation result panel and cancel button must continue to work.
- Static HTML fallback behavior must remain command-copy only.

## Acceptance Criteria

- The page contains live execution status/progress targets.
- `renderOperationResult()` updates the operation result panel and the right-rail
  execution panel.
- Running jobs returned by the active server include elapsed seconds and a
  progress heartbeat.
- Focused tests, full tests, and browser validation pass.
