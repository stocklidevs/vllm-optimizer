# Feature Specification: Live Run Control

**Feature Branch**: `029-session-tuning-sweeps`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Autonomous roadmap phase for cockpit pipeline control

## User Scenarios & Testing

### Primary User Story

As an operator using the cockpit, I want a deterministic controller command that
can start a live optimization run only after an explicit confirmation gate, so
that web controls can graduate from preview artifacts to safe live execution
without bypassing the existing pipeline.

### Acceptance Scenarios

1. Given a sweep under `config/`, an artifact output under `artifacts/`, and a
   remote config under `config/`, when the live run is confirmed, then the
   controller writes a controller result and invokes the optimizer pipeline in
   `run` mode.
2. Given the same inputs without the explicit live confirmation, when the
   controller is called, then it fails before any remote execution can begin.
3. Given an output path outside `artifacts/`, when the controller is called,
   then it fails before any pipeline work begins.
4. Given a risky-session sweep, when the risky gate is not present, then the
   existing pipeline and preview safety gates remain authoritative.

## Requirements

- **REQ-001**: Provide a local controller API for live run requests.
- **REQ-002**: Provide a CLI command for live cockpit run control.
- **REQ-003**: Require an explicit live-run confirmation flag before invoking
  remote-capable pipeline execution.
- **REQ-004**: Restrict sweep and config inputs to `config/`, and output
  artifacts to `artifacts/`.
- **REQ-005**: Preserve existing risky-session and pipeline safety behavior.
- **REQ-006**: Write a controller result artifact with run status, artifact
  paths, and confirmation metadata.

## Out of Scope

- Browser-triggered HTTP execution.
- Persistent Linux/NVIDIA/system changes.
- Automatic promotion.
- Running a real GX10 live sweep during test validation.

## Success Criteria

- Focused controller and CLI tests pass.
- Full pytest passes.
- Documentation explains the confirmation gate and local artifact contract.
