# Feature Specification: Release Documentation

**Feature Branch**: `039-release-documentation`  
**Created**: 2026-05-15  
**Status**: Draft  
**Input**: Phase 7 release polish needs setup, release notes, and handoff documentation that reflects the current CLI.

## User Scenarios and Testing

### Primary User Story

As a future user or maintainer, I want setup and release notes that match the current tool so I can install, verify, and understand the available workflows without relying on conversation history.

### Acceptance Scenarios

1. **Given** a fresh checkout, **when** I read the setup guide, **then** it explains Python/uv setup, local verification, GX10 local config expectations, and safe first commands.
2. **Given** a maintainer is preparing a release, **when** they read the changelog, **then** the current version section summarizes the latest release-polish commands and autonomous phase outputs.
3. **Given** docs are updated, **when** tests run, **then** they verify README links, current version notes, and setup command references.

## Requirements

- **FR-001**: Add a setup guide under `docs/`.
- **FR-002**: Update the changelog with the current version.
- **FR-003**: Link the setup guide from README.
- **FR-004**: Add tests that guard the docs against stale version and missing release commands.

## Non-Goals

- Publishing a package.
- Changing CLI behavior.
- Running live GX10 commands.

## Success Criteria

- Documentation tests pass.
- Full pytest suite remains green.
- Version and README badge are updated.
