# Feature Specification: Cockpit End-to-End Recovery

**Status**: Completed

**Created**: 2026-05-25

**Input**: User reported that the cockpit could not test the flow end-to-end because promotion was gated without a launch option, report generation and review required two clicks, candidates could not be selected, the Performance target still used a low-throughput sweep, and duplicate dashboard controls made the workflow unclear.

## User Scenarios & Testing

### User Story 1 - One-click report review (Priority: P1)

As a cockpit user, I want a completed run to offer one clear report action, so I do not have to guess whether to load or review a report.

**Why this priority**: Report review is the handoff between run execution and candidate decisions.

**Independent Test**: Start from completed run artifacts and verify the cockpit shows `Generate & Review Report`, generates the report, and opens the Reports view automatically.

**Acceptance Scenarios**:

1. **Given** a run is completed, **When** the next action is shown, **Then** it says `Generate & Review Report`.
2. **Given** report generation completes, **When** the controller job returns success, **Then** the cockpit reloads into the Reports view.

### User Story 2 - Select and promote a candidate (Priority: P1)

As a cockpit user, I want to choose which candidate is promoted, so the promotion action matches the report evidence I reviewed.

**Why this priority**: Promotion without candidate selection is not an end-to-end flow.

**Independent Test**: Load a report with multiple candidates, select a non-default candidate, and verify the promotion request writes that selected candidate profile when the promotion gate is enabled.

**Acceptance Scenarios**:

1. **Given** a report has multiple candidates, **When** the Reports view opens, **Then** candidate cards are selectable and the current selection is visible.
2. **Given** the cockpit was launched with the promotion gate, **When** the user promotes the selected candidate, **Then** the local promotion artifact records that candidate id.
3. **Given** the promotion gate was not provided, **When** the Promotion view is shown, **Then** the write action is disabled and the required launch flag is named.

### User Story 3 - Performance target starts from the right sweep (Priority: P2)

As a cockpit user choosing performance, I want the default launcher to use the high-throughput Qwen concurrency sweep, so the candidate set reflects the best known performance path instead of the old small sweep.

**Why this priority**: Objective-first UX is misleading if the default experiment still explores the wrong candidate space.

**Independent Test**: Run the one-command launcher with no sweep argument and verify it prepares the C8 concurrency sweep.

**Acceptance Scenarios**:

1. **Given** the user runs the default cockpit launcher, **When** artifacts are prepared, **Then** the selected sweep is `qwen-concurrency-saturation-c8`.
2. **Given** the user needs another recipe, **When** they provide a sweep override, **Then** the override remains honored.

### Edge Cases

- A report may expose candidates as a list or object; both forms must render candidate choices.
- A selected candidate may not exist for the requested objective; promotion must fail without writing a profile.
- Static HTML generation cannot run controller actions; it must keep promotion locked and explain the required server launch gate.

## Requirements

### Functional Requirements

- **FR-001**: The cockpit MUST replace the two-step `Load Report` then `Review Report` path with one user-facing `Generate & Review Report` action.
- **FR-002**: The cockpit MUST automatically open the Reports view after a report generation job completes.
- **FR-003**: The Reports view MUST show selectable candidates when candidate metrics are available.
- **FR-004**: The active controller MUST accept a gated promotion action that writes a selected-candidate profile artifact.
- **FR-005**: Promotion MUST remain disabled unless the cockpit server or launcher was started with the explicit promotion gate.
- **FR-006**: Promotion helpers and CLI commands MUST accept an optional candidate id and select that ranked candidate instead of always selecting the top row.
- **FR-007**: The default one-command launcher MUST use the Qwen C8 concurrency saturation sweep while preserving explicit sweep overrides.
- **FR-008**: The main dashboard MUST avoid duplicate primary calls to action and duplicate progress bars that imply different workflow states.
- **FR-009**: Version, documentation, tests, release metadata, and SpecKit pointers MUST be updated.

### Experiment Requirements

- **ER-001**: Objective families covered are throughput/performance, balanced recommendation, and gated promotion decisioning.
- **ER-002**: Reproducibility inputs are the selected sweep, ranking artifact, report artifact, selected candidate id, selected objective, and output profile paths.
- **ER-003**: Retained artifacts include the generated report, selected promotion profile, promotion summary, controller result, and pipeline summary.
- **ER-004**: GX10 actions remain session-mutating only for live runs; report generation and promotion artifact writes are local.
- **ER-005**: Static cockpit output remains dry-run/copy-only for promotion when the active server gate is absent.

### Key Entities

- **Candidate Selection**: The currently selected report candidate id and objective used by promotion.
- **Promotion Gate**: The explicit opt-in allowing the active controller to write a local profile artifact.
- **Controller Job Result**: The action status, summary, pipeline stages, and output artifacts returned to the cockpit.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A completed run exposes exactly one report next action, labeled `Generate & Review Report`.
- **SC-002**: A report with two candidates allows either candidate to be selected before promotion.
- **SC-003**: Promotion without the explicit gate fails or remains disabled 100% of the time.
- **SC-004**: Promotion with the gate writes a profile whose provenance candidate id equals the selected candidate.
- **SC-005**: The default launcher prepares `config/sweeps/qwen-concurrency-saturation-c8.json`.
- **SC-006**: Focused cockpit, promotion, launcher, server, and CLI tests pass.

## Assumptions

- The cockpit remains a local operator surface over deterministic artifacts, not an independent optimizer.
- Promotion from the active cockpit writes an artifact under the cockpit output directory and does not overwrite the default profile.
- Confirmation remains a separate safety decision; this feature repairs selection and gated promotion mechanics without auto-promoting.
