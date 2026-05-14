# Feature Specification: Session Tuning Sweep Run

**Feature Branch**: `030-session-tuning-sweep-run`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Add live execution and ranking for session tuning sweeps."

## User Scenarios & Testing

### User Story 1 - Run Session Tuning Sweep (Priority: P1)

As an optimizer operator, I want to execute a planned session tuning sweep so each runtime tuning candidate gets benchmarked with retained artifacts.

**Why this priority**: Spec 029 can plan candidates, but cannot yet produce live results.

**Independent Test**: Run the sweep runner with a fake benchmark runner and verify one JSONL row is written per trial.

**Acceptance Scenarios**:

1. **Given** a session tuning sweep plan and explicit approval, **When** the sweep run executes, **Then** every trial writes benchmark artifacts and a result row.
2. **Given** missing approval, **When** the sweep run is requested, **Then** it fails before benchmark execution.

---

### User Story 2 - Rank Session Tuning Candidates (Priority: P2)

As an optimizer operator, I want to rank session tuning sweep results by throughput, latency, and balanced score so I can choose candidates for repeated confirmation.

**Why this priority**: Ranking turns raw live results into an actionable next candidate.

**Independent Test**: Rank a JSONL result set and verify the highest-throughput candidate wins the throughput objective.

**Acceptance Scenarios**:

1. **Given** successful session tuning result rows, **When** ranking runs, **Then** ranked objectives are written to JSON.
2. **Given** failed trials and `--continue-on-failure`, **When** ranking runs, **Then** failed candidates are reflected in failure rates.

## Requirements

### Functional Requirements

- **FR-001**: System MUST add `session-tuning-sweep-run`.
- **FR-002**: System MUST add `session-tuning-sweep-rank`.
- **FR-003**: Sweep run MUST require `--allow-session-tuning`.
- **FR-004**: Sweep run MUST write `results.jsonl` with one row per attempted trial.
- **FR-005**: Sweep rank MUST output objectives for throughput, latency, and balanced scores.
- **FR-006**: Sweep run MUST support `--continue-on-failure`.
- **FR-007**: No promotion occurs in this spec.

### Experiment Requirements

- **ER-001**: Objective family is runtime/session tuning performance.
- **ER-002**: Reproducibility inputs include session tuning sweep plan, target config, timeout, and result rows.
- **ER-003**: Raw artifacts retained include every benchmark trial directory and `results.jsonl`.
- **ER-004**: GX10 actions are session-mutating benchmark sessions only.
- **ER-005**: Dry-run preview remains available before live use.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Run output contains exactly one result row per planned trial when all trials complete.
- **SC-002**: Ranking output contains all three objectives.
- **SC-003**: Full pytest suite passes.

## Assumptions

- Ranking can reuse the existing sweep ranking semantics.
- Promotion and repeated confirmation remain later steps.
