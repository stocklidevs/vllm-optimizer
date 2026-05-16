# Feature Specification: Active Cockpit Server and Help UX

**Feature Branch**: `029-session-tuning-sweeps`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: User requested active controller buttons, tooltips/question marks,
and a How to Use page.

## User Scenarios & Testing

### Primary User Story

As an operator using the vLLM cockpit, I want the page to explain controller
actions and run safe actions through a local controller server, so that I do not
need to copy commands manually for routine plan/preview steps.

### Acceptance Scenarios

1. Given the cockpit is served by the local controller server, when the user
   clicks Plan, then the server runs the deterministic local planning workflow
   and returns artifact paths.
2. Given the cockpit is served by the local controller server, when the user
   clicks Preview, then the server runs the deterministic local preview workflow
   and returns plan/preview artifacts.
3. Given Run is requested without confirmation, then the server rejects the
   request before any remote execution.
4. Given the cockpit is opened without the server, then controller buttons fall
   back to command-copy behavior.
5. Given a user does not know what Plan or Preview means, then question-mark
   help and a How to Use tab explain the workflow in the UI.

## Requirements

- **REQ-001**: Add a `cockpit-server` CLI command that serves the cockpit on a
  localhost host/port.
- **REQ-002**: Serve `GET /` and `GET /index.html` with the cockpit HTML.
- **REQ-003**: Serve `POST /api/controller/plan` and
  `POST /api/controller/preview` through existing deterministic controller or
  pipeline logic.
- **REQ-004**: Serve `POST /api/controller/run` but require an explicit
  `confirm_live_run` request field before invoking remote-capable execution.
- **REQ-005**: Keep inputs under `config/` and outputs under `artifacts/`.
- **REQ-006**: Add tooltip/question-mark help beside controller stages and
  safety concepts.
- **REQ-007**: Add a How to Use tab that explains choose, plan, preview, run,
  report, confirm, and promote.
- **REQ-008**: Use no npm dependencies in this slice.

## Out of Scope

- Background job queues.
- Streaming progress.
- Browser-triggered promotion.
- Persistent GX10 system changes.

## Success Criteria

- Unit tests cover controller server action dispatch and safety rejection.
- Web cockpit tests cover help UX and active API hooks.
- CLI parser exposes `cockpit-server`.
- Full pytest passes.
