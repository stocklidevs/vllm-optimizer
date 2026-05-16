# Implementation Plan: Active Cockpit Server and Help UX

## Summary

Turn the cockpit into a local active app while preserving static fallback
behavior. A dependency-free stdlib HTTP server serves the existing cockpit HTML
and exposes safe controller endpoints for Plan and Preview. Run is wired but
requires explicit confirmation before remote-capable execution.

## Technical Context

- Language: Python 3.11
- HTTP: `http.server.ThreadingHTTPServer`
- Existing logic: `cockpit_controller`, `optimizer_pipeline`, `web_cockpit`
- UI: generated HTML/CSS/JS, no npm

## Architecture

- Add `src/vllm_optimizer/cockpit_server.py`.
- Add `cockpit-server` CLI command.
- Extend `web_cockpit` with:
  - How to Use tab.
  - question-mark tooltips.
  - active controller fetch calls with command-copy fallback.
- Keep server action handlers testable without binding sockets.

## Verification

- Focused unit tests for server dispatch.
- Focused web cockpit tests for help and active hooks.
- CLI integration test for command availability.
- Full pytest suite.
