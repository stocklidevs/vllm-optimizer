# Feature Specification: Cockpit Run Browser

**Feature Branch**: `043-cockpit-run-browser`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Continue the web cockpit roadmap by allowing the cockpit to browse local artifact-backed runs and reports.

## User Scenarios and Testing

### Primary User Story

As the optimizer operator, I want the cockpit to list available local runs and reports so I can find prior results without remembering artifact paths.

### Acceptance Scenarios

1. **Given** an artifact root contains run outputs, **when** I generate a run index, **then** it records run directories, detected artifact types, paths, and modified timestamps.
2. **Given** a run index is passed to the cockpit, **when** the cockpit renders, **then** a Runs tab lists entries and artifact links/paths.
3. **Given** no run artifacts are found, **when** the run browser renders, **then** it shows an empty state.

## Requirements

- **FR-001**: Add a `run-browser` CLI command that scans a local artifact root.
- **FR-002**: The command MUST write a JSON run index and optional standalone HTML.
- **FR-003**: The run index MUST detect known artifact filenames including `summary.json`, `ranking.json`, `canonical-report.json`, `execution-status.json`, `pipeline-summary.json`, and `results.jsonl`.
- **FR-004**: The cockpit MUST accept an optional `--run-index` artifact and render a Runs tab.
- **FR-005**: The feature MUST remain local-only and read-only.

## Non-Goals

- Opening files from the browser through OS integration.
- Live filesystem watching.
- Triggering CLI runs.

## Success Criteria

- Unit tests cover run index generation and cockpit rendering.
- CLI tests cover `run-browser`.
- Full pytest suite remains green.
