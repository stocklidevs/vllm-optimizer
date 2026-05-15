# Feature Specification: Artifact Contract Catalog

**Feature Branch**: `037-artifact-contract-catalog`  
**Created**: 2026-05-15  
**Status**: Draft  
**Input**: Phase 7 release polish needs versioned report contracts and stable documentation for CLI/web artifacts.

## User Scenarios and Testing

### Primary User Story

As a project maintainer preparing the optimizer for repeatable use, I want a deterministic catalog of supported artifact contracts so the CLI, static dashboards, and future web interface can agree on which JSON fields are stable.

### Acceptance Scenarios

1. **Given** the repository is installed locally, **when** I run the artifact contract command, **then** it writes a JSON catalog with schema version, generated timestamp, contract entries, producer commands, required fields, optional fields, and consumers.
2. **Given** I request Markdown output, **when** the command completes, **then** it writes a human-readable contract reference suitable for release documentation.
3. **Given** future dashboard code needs to know if canonical reports are stable, **when** it reads the catalog, **then** the `canonical-report` entry exposes schema version `1.0`, required top-level fields, and downstream consumers.

## Requirements

- **FR-001**: The system MUST expose an `artifact-contracts` CLI command.
- **FR-002**: The command MUST be local-only and MUST NOT read or mutate live GX10 state.
- **FR-003**: The JSON catalog MUST include a catalog schema version and optimizer package version.
- **FR-004**: Each contract entry MUST include artifact type, schema version, producer command, stability, required fields, optional fields, and consumers.
- **FR-005**: The catalog MUST include contracts for canonical reports, execution status, knob group catalogs, and pipeline control manifests.
- **FR-006**: The command MUST optionally write a Markdown reference with one section per contract.

## Non-Goals

- Generating formal JSON Schema files.
- Validating existing artifacts against the contracts.
- Changing existing report payloads.

## Success Criteria

- The focused CLI test proves JSON and Markdown contract generation.
- The full test suite remains green.
- README documents the release-polish command.
