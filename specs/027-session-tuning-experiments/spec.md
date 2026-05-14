# Feature Specification: Session Tuning Experiments

**Feature Branch**: `027-session-tuning-experiments`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Begin impactful tuning with guarded session-only experiments using the live system tuning catalog."

## User Scenarios & Testing

### User Story 1 - Preview Session Tuning (Priority: P1)

As an optimizer operator, I want to preview session-only tuning changes before a live benchmark so I can see exactly which environment variables and shell limits would be applied.

**Why this priority**: Session tuning must remain explicit and reversible before we let it touch live benchmark sessions.

**Independent Test**: Run a session tuning preview from a JSON profile and system tuning catalog, then verify the output lists only approved session-mutating actions and refuses persistent actions.

**Acceptance Scenarios**:

1. **Given** a tuning profile with approved env vars and `ulimit -n`, **When** preview is run, **Then** the preview writes the planned shell exports and ulimit command with `will_execute=false`.
2. **Given** a tuning profile that requests persistent THP changes, **When** preview is run, **Then** the command fails unless a future persistent gate exists.

---

### User Story 2 - Run Benchmark With Session Tuning (Priority: P2)

As an optimizer operator, I want a benchmark run to apply approved session tuning only inside the remote benchmark shell so the tuning disappears when the session ends.

**Why this priority**: This is the first step toward measuring runtime knobs without changing machine state permanently.

**Independent Test**: Build the remote benchmark script with session tuning and verify the tuning prelude appears before vLLM starts.

**Acceptance Scenarios**:

1. **Given** a benchmark profile and session tuning profile, **When** benchmark run is requested with tuning, **Then** the remote script exports the tuning environment and applies shell limits before starting vLLM.
2. **Given** a tuning profile without explicit session opt-in, **When** benchmark run is requested, **Then** the command fails before SSH execution.

## Requirements

### Functional Requirements

- **FR-001**: System MUST add a session tuning profile format.
- **FR-002**: System MUST add a `session-tuning-preview` CLI command.
- **FR-003**: System MUST reject persistent-mutating and risky/unknown tuning actions.
- **FR-004**: System MUST support approved environment variable exports for the benchmark shell.
- **FR-005**: System MUST support approved `ulimit -n` changes for the benchmark shell.
- **FR-006**: System MUST require explicit opt-in before benchmark execution applies session tuning.
- **FR-007**: System MUST record session tuning metadata in benchmark plans.

### Experiment Requirements

- **ER-001**: Objective family is runtime/session performance tuning.
- **ER-002**: Reproducibility inputs include tuning profile, system tuning catalog path, benchmark profile, prompt set, and command preview.
- **ER-003**: Raw artifacts retained include benchmark plans, metrics, logs, summaries, and tuning preview.
- **ER-004**: GX10 actions are session-mutating only and scoped to benchmark shell execution.
- **ER-005**: Dry-run preview is required before live use.

### Key Entities

- **Session Tuning Profile**: A JSON profile containing approved env vars and shell limits.
- **Session Tuning Preview**: The deterministic command prelude and safety classification.
- **Tuned Benchmark Run**: A benchmark run whose remote shell includes the approved tuning prelude.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Preview output is deterministic for the same profile and catalog.
- **SC-002**: Persistent/risky tuning requests are rejected.
- **SC-003**: Tuned benchmark plans include session tuning metadata.
- **SC-004**: Full pytest suite passes.

## Assumptions

- First tuning knobs are environment variables and `ulimit -n`.
- GPU power limits are excluded because live discovery reported `[N/A]`.
- CPU governor and THP changes are excluded from this spec because they are not scoped to the benchmark shell.
