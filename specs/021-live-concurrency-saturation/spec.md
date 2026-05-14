# Feature Specification: Live Concurrency Saturation

**Feature Branch**: `021-live-concurrency-saturation`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Run the live GX10 concurrency saturation ladder, generate the full report, update version/documentation, and commit."

## User Scenarios & Testing

### User Story 1 - Complete the Live Saturation Curve (Priority: P1)

As the optimizer operator, I want the planned concurrency saturation levels run on the GX10, so the report can identify the real throughput knee rather than relying on one prior concurrency point.

**Why this priority**: The current best win is concurrent interactive throughput, and the missing evidence is where it saturates.

**Independent Test**: Run the planned c1, c2, c4, c6, and c8 sweeps and verify each produces a ranking artifact.

**Acceptance Scenarios**:

1. **Given** existing saturation plans and previews, **When** the live ladder is executed, **Then** each missing level writes live results and ranking artifacts.
2. **Given** live rankings for all planned levels plus the existing c3 ranking, **When** the report is generated, **Then** it recommends a concurrency level with metrics and overrides.

## Requirements

- **FR-001**: The live run MUST execute c1, c2, c4, c6, and c8 saturation plans sequentially.
- **FR-002**: The report MUST include c1, c2, c3, c4, c6, and c8 ranking inputs.
- **FR-003**: Documentation MUST summarize the live result and next action.
- **FR-004**: Version metadata MUST be updated and committed.

## Success Criteria

- **SC-001**: Each missing saturation level has a live `ranking.json`.
- **SC-002**: `artifacts/reports/qwen-concurrency-saturation.json` and `.md` are regenerated from all available live rankings.
- **SC-003**: The full automated test suite passes.

## Assumptions

- Existing c3 live ranking remains the reference for concurrency 3.
- Live runs are session-scoped and use existing sweep cleanup behavior.
