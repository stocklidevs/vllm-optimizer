# Feature Specification: Active Cockpit Operation Feedback

**Feature Branch**: `029-session-tuning-sweeps`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: User said the active cockpit is still hard to understand, asked for
5-year-old-simple feedback, a progress bar, and stop/cancel.

## User Scenarios & Testing

### Primary User Story

As an operator who is not thinking about artifact internals, I want every
cockpit action to explain what just happened, why it matters, and what I should
do next, so that Plan, Preview, and Run feel like a guided workflow instead of
silent command execution.

### Acceptance Scenarios

1. Given the user clicks Plan, when it finishes, then the page shows a simple
   result card explaining that a blueprint was made, with candidate/trial
   counts when available and Preview as the next step.
2. Given the user clicks Preview, when it finishes, then the page shows whether
   the plan is ready or blocked, any safety reason, and whether Run is allowed.
3. Given the user clicks Run, then the page shows a progress bar and keeps
   polling job status instead of staying on "running run".
4. Given the user clicks Cancel, then the server records a cancellation request
   and the page explains whether the job is cancelled or waiting for current
   work to finish.
5. Given the page is used by someone new, then labels use plain language and
   the Operation Result area gives "what happened" and "next step" text.

## Requirements

- **REQ-001**: Add server-side job status for controller actions.
- **REQ-002**: Add status polling endpoints for controller jobs.
- **REQ-003**: Add cancellation request endpoint for controller jobs.
- **REQ-004**: Add an Operation Result panel with a progress bar.
- **REQ-005**: Show plain-language summaries for Plan and Preview.
- **REQ-006**: Keep Run remote execution gated by explicit confirmation.
- **REQ-007**: Avoid claiming a running remote operation stopped instantly if
  only a cancellation request has been recorded.

## Out of Scope

- Hard-killing remote vLLM processes.
- Per-token live progress metrics.
- WebSocket streaming.
- Browser-triggered profile promotion.

## Success Criteria

- Unit tests cover job start/status/cancel behavior.
- Web cockpit tests cover the progress panel and kid-simple copy.
- Full pytest passes.
