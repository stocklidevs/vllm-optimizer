# Feature Specification: Stale Sweep Artifact Guard

**Status**: Completed

**Created**: 2026-05-25

**Input**: User reported that the cockpit still showed approximately 50 tokens/sec after selecting Performance and asked to inspect the latest logs and run the app.

## User Scenarios & Testing

### User Story 1 - Never show stale sweep results as current performance (Priority: P1)

As a cockpit user, I want report artifacts to match the sweep currently configured for the cockpit, so an old small sweep cannot appear as the latest Performance result.

**Why this priority**: Showing 50 tok/s from an old small sweep while the cockpit says Performance makes the optimizer untrustworthy.

**Independent Test**: Reuse an output directory containing a `qwen-small-sweep` ranking, configure the pipeline for `qwen-concurrency-saturation-c8`, and verify report generation refuses the stale artifacts.

**Acceptance Scenarios**:

1. **Given** an output directory has an old ranking for one sweep, **When** report mode runs for a different sweep, **Then** the report is not generated from the old ranking.
2. **Given** the active cockpit is configured for C8 but the output directory contains a small-sweep report, **When** the page loads, **Then** the stale report is hidden and the page returns to a fresh start state.

### Edge Cases

- Existing output directories may contain a matching sweep plan but a stale report from a previous failed or manual run.
- Existing output directories may contain stale results without a stale ranking.
- Explicitly provided report paths remain operator-selected inputs; the guard applies to implicit active output-directory artifacts.

## Requirements

### Functional Requirements

- **FR-001**: Report generation MUST validate that an existing ranking belongs to the current sweep before reusing it.
- **FR-002**: If an existing ranking does not match the current sweep, the pipeline MUST either regenerate it from matching results or fail loudly with a stale-artifact message.
- **FR-003**: Existing sweep plans MUST be regenerated when their sweep id does not match the requested sweep.
- **FR-004**: Active cockpit rendering MUST hide implicit output-directory reports that do not match the configured sweep.
- **FR-005**: Documentation, version metadata, tests, and SpecKit pointers MUST be updated.

### Experiment Requirements

- **ER-001**: The optimized objective is correctness of report provenance for throughput/performance results.
- **ER-002**: Reproducibility inputs are the configured sweep path, output directory, sweep plan, ranking, results, and report artifacts.
- **ER-003**: Raw stale artifacts are retained; the guard prevents reuse but does not delete them.
- **ER-004**: GX10 actions are not required; this is a local artifact validation fix.
- **ER-005**: Dry-run expectations are covered by unit tests and local cockpit browser validation.

## Success Criteria

- **SC-001**: A stale small-sweep ranking cannot be reused to generate a C8 report.
- **SC-002**: A C8 cockpit opened on a stale small-sweep output directory does not display the stale 50 tok/s candidate.
- **SC-003**: A C8 cockpit opened on valid C8 artifacts displays the 98 tok/s C8 winner.
- **SC-004**: Focused tests, full tests, release check, and local browser validation pass.

## Assumptions

- Output directories may be reused during development, so artifact validation must happen inside the pipeline and active cockpit renderer.
- The active cockpit should prefer hiding stale implicit reports over trying to auto-delete or mutate old artifacts.
