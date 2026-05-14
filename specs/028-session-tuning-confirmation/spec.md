# Feature Specification: Session Tuning Confirmation

**Feature Branch**: `028-session-tuning-confirmation`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Repeated A/B confirmation for a session tuning profile against the same serve profile without tuning."

## User Scenarios & Testing

### User Story 1 - Confirm Session Tuning Signal (Priority: P1)

As an optimizer operator, I want one command to run repeated untuned vs tuned benchmarks and aggregate the result so I can tell whether a session tuning profile is real signal or run noise.

**Why this priority**: The first live tuned run looked plausible but inconclusive; repeated confirmation is needed before we promote the tuning into broader pipeline candidates.

**Independent Test**: Run confirmation with a fake benchmark runner and verify it writes paired repetition directories, A/B JSON, Markdown, and a summary.

**Acceptance Scenarios**:

1. **Given** a serve profile, prompt set, and session tuning profile, **When** confirmation runs for N repetitions, **Then** it writes N `current-rN` summaries and N `tuned-rN` summaries.
2. **Given** repeated summaries, **When** confirmation finishes, **Then** it writes an A/B report using labels for current and tuned runs.

---

### User Story 2 - Preserve Session Tuning Safety Gate (Priority: P2)

As an optimizer operator, I want repeated confirmation to require explicit session tuning approval so the live remote run remains intentional.

**Why this priority**: Confirmation performs multiple live vLLM sessions over SSH and applies shell-scoped tuning to half of them.

**Independent Test**: Run the command without `--allow-session-tuning` and verify it fails before benchmark execution.

**Acceptance Scenarios**:

1. **Given** a session tuning profile without approval, **When** confirmation is requested, **Then** the command fails before live work.
2. **Given** a non-positive repetition count, **When** confirmation is requested, **Then** the command fails before live work.

## Requirements

### Functional Requirements

- **FR-001**: System MUST add a `session-tuning-confirm` CLI command.
- **FR-002**: System MUST run repeated untuned and tuned benchmark pairs.
- **FR-003**: System MUST require `--allow-session-tuning`.
- **FR-004**: System MUST write `current-rN` and `tuned-rN` benchmark artifacts under the output directory.
- **FR-005**: System MUST generate A/B confirmation JSON and Markdown.
- **FR-006**: System MUST write a summary with labels, repetitions, artifact paths, and decision.

### Experiment Requirements

- **ER-001**: Objective family is runtime/session tuning confirmation.
- **ER-002**: Reproducibility inputs include serve profile, prompt set, session tuning profile, repetition count, and timeout.
- **ER-003**: Raw artifacts retained include benchmark artifacts for every repetition plus A/B reports.
- **ER-004**: GX10 actions are session-mutating benchmark sessions only.
- **ER-005**: Live use requires explicit `--allow-session-tuning`.

### Key Entities

- **Session Tuning Confirmation Run**: Paired repeated untuned and tuned benchmark runs.
- **Confirmation Summary**: Final decision and artifact map for one repeated confirmation.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Confirmation produces exactly N untuned and N tuned summary artifacts.
- **SC-002**: Confirmation report is compatible with existing A/B decision semantics.
- **SC-003**: Missing approval fails before benchmark execution.
- **SC-004**: Full pytest suite passes.

## Assumptions

- The tuned side uses one session tuning profile.
- The untuned side uses the same serve profile and prompt set without session tuning.
- Promotion or pipeline integration of winning session tuning profiles remains a later spec.
