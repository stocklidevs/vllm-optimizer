# Feature Specification: Cockpit Failure Diagnostics

**Status**: Completed

**Created**: 2026-05-26

**Input**: User reported that the cockpit run only said "Failed" and asked why it failed and whether the app can provide useful failure information.

## User Scenarios & Testing

### User Story 1 - Explain failed cockpit runs (Priority: P1)

As a cockpit user, I want a failed optimization to tell me what failed, why it probably failed, what artifact to inspect, and what to do next, so I am not left with a bare "Failed" badge.

**Why this priority**: The cockpit is an operational controller. A failure without diagnosis blocks recovery and destroys trust in the app.

**Independent Test**: Force a controller job to raise a "no rankable sweep trials" error and verify the job result includes diagnostics, next steps, artifact paths, and a persisted failure record.

**Acceptance Scenarios**:

1. **Given** a live run fails before producing rankable results, **When** the job status is displayed, **Then** the cockpit explains that no successful trial was available to rank and points to `live/results.jsonl`.
2. **Given** a failed job occurred before a page refresh, **When** the cockpit reloads, **Then** the most recent failed job can still be displayed from the persisted controller job artifact.
3. **Given** failed trial rows exist, **When** diagnostics are built, **Then** the first failed trial reason is surfaced in the user-facing next steps.

## Requirements

- **FR-001**: Failed controller jobs MUST include structured diagnostics with error type, likely cause, next steps, relevant artifact paths, and failed trial summaries when available.
- **FR-002**: Failed controller jobs MUST be persisted under the cockpit output directory.
- **FR-003**: The active cockpit MUST expose a recent-job API that can recover the latest persisted job after refresh.
- **FR-004**: The web cockpit MUST render failure detail beyond the status label.
- **FR-005**: Static/offline cockpit mode MUST continue to work when no recent-job API exists.
- **FR-006**: Documentation, version metadata, tests, and SpecKit pointers MUST be updated.

## Success Criteria

- **SC-001**: A failed run no longer displays only "Failed"; it shows likely cause, next step, and artifact paths.
- **SC-002**: Refreshing the page after a failed run can restore the failure detail from disk.
- **SC-003**: Focused tests, full tests, release check, and local browser validation pass.

## Assumptions

- Exact failure context may be unavailable for failures created by older server versions because previous cockpit jobs were only stored in memory.
- The new diagnostics should preserve raw artifacts and avoid deleting or mutating failed run outputs.
