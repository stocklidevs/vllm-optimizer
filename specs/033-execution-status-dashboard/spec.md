# Feature Specification: Execution Status Dashboard

**Feature Branch**: `033-execution-status-dashboard`

**Created**: 2026-05-15

**Status**: Draft

**Input**: Project roadmap Phase 3: add execution feedback for live runs and pipeline stages using deterministic local artifacts that a future web dashboard can read.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Summarize Run Progress (Priority: P1)

As a user running optimization workflows, I want a local status artifact that summarizes stage completion, trial progress, failures, and produced artifacts so that I can monitor execution without reading every raw file.

**Why this priority**: This creates the progress contract for the future web execution dashboard.

**Independent Test**: Given a run directory with pipeline plan, summary, and result rows, generate status JSON and verify stages, trial counts, failures, and artifact availability.

**Acceptance Scenarios**:

1. **Given** a pipeline plan and partial results, **When** status is generated, **Then** the output identifies completed stages and per-trial progress.
2. **Given** failed result rows, **When** status is generated, **Then** the output includes failure count and failure reasons.

---

### User Story 2 - Preview Status in Browser (Priority: P2)

As a user, I want the status artifact rendered as a static HTML dashboard so that progress can be inspected visually before a live web server exists.

**Why this priority**: This is a safe incremental step toward the web execution dashboard.

**Independent Test**: Generate HTML from a status artifact and verify it shows current status, stages, trial counts, and artifact paths.

**Acceptance Scenarios**:

1. **Given** a status JSON artifact, **When** HTML is generated, **Then** the page shows stage state, trial summary, and artifact availability.

### Edge Cases

- Run directory has a plan but no summary yet.
- Results file exists with completed and failed rows.
- Artifacts listed in a plan are missing.
- Status generation is repeated from unchanged inputs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate execution status JSON from an existing local run directory.
- **FR-002**: Status MUST include stage names, stage state, artifact paths, and whether artifacts exist.
- **FR-003**: Status MUST include trial counts by status when result rows are available.
- **FR-004**: Status MUST include failure reasons when failed trials are present.
- **FR-005**: Status MUST support optional standalone HTML rendering from the same status data.
- **FR-006**: Status generation MUST perform no GX10 actions.
- **FR-007**: Status generation MUST be deterministic when regenerated from unchanged inputs.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST report the workflow family and stage objective when present in source artifacts.
- **ER-002**: Feature MUST preserve artifact paths needed to audit execution.
- **ER-003**: Feature MUST perform no remote mutation.
- **ER-004**: Feature MUST support incomplete runs.
- **ER-005**: Feature MUST be usable before live web orchestration exists.

### Key Entities *(include if feature involves data)*

- **Execution Status**: Snapshot of run progress, stages, trials, failures, and artifacts.
- **Stage Status**: Per-stage state and artifact availability.
- **Trial Status**: Aggregated trial counts and failure reasons from result rows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can identify whether a run is planned, running, completed, or failed from status output in under 30 seconds.
- **SC-002**: Status output reports trial counts and failure counts from result rows in 100% of tested cases.
- **SC-003**: Status HTML displays at least four views: overall state, stages, trial summary, and artifacts.
- **SC-004**: Status generation requires no GX10 connection.

## Assumptions

- The first status implementation reads existing local artifacts rather than streaming live process events.
- Future long-running orchestration can update the same status contract incrementally.
