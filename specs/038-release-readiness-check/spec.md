# Feature Specification: Release Readiness Check

**Feature Branch**: `038-release-readiness-check`  
**Created**: 2026-05-15  
**Status**: Draft  
**Input**: Phase 7 release polish needs repeatable local checks for packaging, documentation, active SpecKit metadata, and release-facing artifacts.

## User Scenarios and Testing

### Primary User Story

As a maintainer preparing a release or handoff, I want a local command that summarizes repository readiness so I can catch stale versions, missing SpecKit metadata, and missing release-facing docs before shipping.

### Acceptance Scenarios

1. **Given** the repository is checked out locally, **when** I run `release-check`, **then** it writes a JSON report with overall status, individual checks, severity, and paths.
2. **Given** Markdown output is requested, **when** the command completes, **then** it writes a concise checklist report for release notes or handoff review.
3. **Given** package metadata and README badges agree, **when** the command runs, **then** the version checks pass.

## Requirements

- **FR-001**: The system MUST expose a local-only `release-check` CLI command.
- **FR-002**: The command MUST NOT require GX10 access or live artifacts.
- **FR-003**: The JSON output MUST include schema version, tool version, generated timestamp, overall status, and checks.
- **FR-004**: Checks MUST cover package version consistency, README version badge consistency, active SpecKit feature files, artifact contract command availability, and release-facing documentation references.
- **FR-005**: The command MUST optionally write Markdown output.

## Non-Goals

- Building or publishing a package.
- Running the full test suite.
- Validating live GX10 connectivity.

## Success Criteria

- Focused unit and CLI tests pass.
- Full pytest suite remains green.
- README documents the release readiness command.
