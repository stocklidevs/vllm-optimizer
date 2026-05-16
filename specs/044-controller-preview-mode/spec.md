# Feature Specification: Controller Preview Mode

**Feature Branch**: `044-controller-preview-mode`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Continue the web interface roadmap by adding a safe local controller path for browser-triggered plan and preview only.

## User Scenarios and Testing

### Primary User Story

As the optimizer operator, I want a local controller endpoint that can generate plan and preview artifacts for a selected sweep so the cockpit can eventually trigger safe preparation steps without launching live GX10 runs.

### Acceptance Scenarios

1. **Given** a local sweep config, **when** the controller preview action is requested, **then** it writes `sweep-plan.json` and `sweep-preview.json` under the requested artifact output directory.
2. **Given** a risky sweep is requested without its explicit gate, **when** preview is generated, **then** the preview remains blocked and records the gate reason.
3. **Given** a request tries to write outside `artifacts/`, **when** it is validated, **then** the controller rejects it.

## Requirements

- **FR-001**: Add controller preview logic for plan plus preview generation.
- **FR-002**: Add a `cockpit-preview` CLI command for deterministic local action execution.
- **FR-003**: The command MUST only support plan/preview generation and MUST NOT run live sweeps, confirmations, or promotion.
- **FR-004**: The command MUST restrict sweep paths to `config/` and output paths to `artifacts/`.
- **FR-005**: The command MUST preserve explicit risky-session gate behavior.

## Non-Goals

- Long-running local HTTP server.
- Live GX10 execution.
- Browser-triggered promotion.

## Success Criteria

- Unit tests cover allowed and rejected controller requests.
- CLI tests cover plan/preview artifact generation.
- Full pytest suite remains green.
