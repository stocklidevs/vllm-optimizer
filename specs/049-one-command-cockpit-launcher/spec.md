# Feature Specification: One-Command Cockpit Launcher

**Feature Branch**: `029-session-tuning-sweeps`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User requested a one-command launcher for the active cockpit.

## User Scenarios & Testing

### Primary User Story

As an operator, I want to start the cockpit with one command, so that I do not
need to remember the catalog, manifest, run index, sweep, config, out-dir, host,
and port flags.

### Acceptance Scenarios

1. Given a normal repository checkout, when the user runs `cockpit-launch`,
   then the launcher generates the default cockpit artifacts and starts the
   active cockpit server on `127.0.0.1:8787`.
2. Given the user wants a different sweep or port, when they pass optional
   overrides, then the launcher uses those overrides while keeping the same
   generated artifact conventions.
3. Given the launch command is inspected with `--help`, then the CLI explains
   the defaults and optional overrides.

## Requirements

- **REQ-001**: Add a `cockpit-launch` CLI command.
- **REQ-002**: Default to `config/sweeps/qwen-small-sweep.json`.
- **REQ-003**: Default to `config/local.gx10.json` when present, otherwise
  `config/gx10.example.json`.
- **REQ-004**: Generate `artifacts/catalog/knob-groups.json`.
- **REQ-005**: Generate a pipeline-control manifest for the selected sweep group.
- **REQ-006**: Generate `artifacts/catalog/run-index.json`.
- **REQ-007**: Start `cockpit-server` using the generated artifacts.
- **REQ-008**: Keep the implementation dependency-free and npm-free.

## Out of Scope

- Automatically opening the browser.
- Remembering last-used sweep in a settings file.
- Selecting a sweep from the web UI before server start.

## Success Criteria

- Unit tests cover launch preparation and server config generation.
- CLI integration tests cover launcher help.
- Full pytest passes.
