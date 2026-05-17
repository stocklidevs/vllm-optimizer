# Implementation Plan: Active Cockpit Operation Feedback

## Summary

Add a simple operation result layer on top of the active cockpit controller.
Server actions become tracked jobs with status/progress/cancel metadata, and
the web cockpit shows a progress bar plus plain-language explanations.

## Technical Context

- Language: Python 3.11
- HTTP: stdlib `ThreadingHTTPServer`
- UI: static generated HTML/CSS/JS, no npm
- Safety: Run remains explicitly confirmed and cancellation is represented
  honestly as requested/cancelled rather than pretending to hard-kill remote
  work.

## Architecture

- Extend `cockpit_server.py` with a small in-memory `CockpitJobStore`.
- Add job status and cancel endpoint handling.
- Keep direct `handle_controller_action` for existing tests and CLI-safe logic.
- Extend `web_cockpit.py` with an Operation Result panel, progress bar, and
  polling/cancel JS.

## Verification

- Focused unit tests for job lifecycle.
- Focused web cockpit tests for operation feedback UI.
- Full pytest suite.
