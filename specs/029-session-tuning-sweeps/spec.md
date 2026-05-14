# Feature Specification: Session Tuning Sweeps

**Feature Branch**: `029-session-tuning-sweeps`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Systematically test multiple shell-scoped runtime tuning variants instead of one hand-picked env combo."

## User Scenarios & Testing

### User Story 1 - Plan Session Tuning Candidates (Priority: P1)

As an optimizer operator, I want to define a sweep of session tuning profiles and generate a deterministic plan so runtime tuning variants can be reviewed before live benchmark runs.

**Why this priority**: The first single tuning profile was neutral; the next useful move is systematic candidate planning.

**Independent Test**: Load a session tuning sweep definition and verify the generated plan contains stable candidate ids, repeated trial ids, session tuning previews, and benchmark plans.

**Acceptance Scenarios**:

1. **Given** a sweep definition with multiple session tuning profiles, **When** a plan is generated, **Then** every candidate has a deterministic id and preview.
2. **Given** repetitions greater than one, **When** a plan is generated, **Then** each candidate produces one trial per repetition.

---

### User Story 2 - Preview Session Tuning Sweep Safety (Priority: P2)

As an optimizer operator, I want to preview a session tuning sweep and see whether any candidate is blocked before live execution.

**Why this priority**: Runtime tuning remains session-mutating and must keep the same explicit dry-run discipline as vLLM parameter sweeps.

**Independent Test**: Generate a preview from a plan and verify all candidates are marked non-executing and blocked candidates include reasons.

**Acceptance Scenarios**:

1. **Given** safe session tuning profiles, **When** preview is generated, **Then** the preview is unblocked.
2. **Given** an unsafe profile, **When** the sweep is loaded, **Then** validation fails before a plan is written.

## Requirements

### Functional Requirements

- **FR-001**: System MUST add session tuning sweep definitions.
- **FR-002**: System MUST add `session-tuning-sweep-plan`.
- **FR-003**: System MUST add `session-tuning-sweep-preview`.
- **FR-004**: System MUST validate every referenced session tuning profile with existing session tuning safety rules.
- **FR-005**: System MUST include session tuning preview metadata in every trial.
- **FR-006**: System MUST keep live execution out of scope for this spec.

### Experiment Requirements

- **ER-001**: Objective family is runtime/session tuning candidate exploration.
- **ER-002**: Reproducibility inputs include base serve profile, prompt set, session tuning profiles, repetitions, and seed.
- **ER-003**: Raw artifacts retained include sweep definition, plan, and preview.
- **ER-004**: GX10 actions are none in this spec; output is local dry-run only.
- **ER-005**: Dry-run preview is the primary deliverable.

### Key Entities

- **Session Tuning Sweep Definition**: JSON file listing base benchmark inputs and session tuning profile candidates.
- **Session Tuning Sweep Plan**: Deterministic dry-run plan with candidates and repeated trial metadata.
- **Session Tuning Sweep Preview**: Safety and execution preview for the plan.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Same sweep definition produces identical candidate and trial ids.
- **SC-002**: Preview reports blocked status without running remote commands.
- **SC-003**: Full pytest suite passes.

## Assumptions

- Live execution and ranking for session tuning sweeps will be a later spec.
- Candidate profiles are explicit JSON files under `config/session-tuning/`.
