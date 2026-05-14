# Feature Specification: Scheduler Knob Sweep

**Feature Branch**: `010-scheduler-knob-sweep`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add catalog-approved optional vLLM serve flags and a focused Qwen scheduler/prefill sweep. The system should extend serve profiles to render safe optional flags from an explicit allowlist, reject unknown or risky flags, support sweep overrides for max_num_batched_tokens, max_num_seqs, enable_chunked_prefill, and enable_prefix_caching, and provide a bounded scheduler sweep config around the current Qwen performance champion. This feature must remain session-level only and must not add arbitrary shell flags, persistent Linux/NVIDIA tuning, installs, or concurrent load testing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Render Approved Optional Flags (Priority: P1)

As the operator, I want serve profiles to render only catalog-approved optional
vLLM flags so new performance knobs can be tested without arbitrary command
injection.

**Why this priority**: Scheduler sweeps require more flags than the original
profile schema, but safety must remain explicit.

**Independent Test**: Can be tested locally by loading profiles with approved
and rejected optional flags and verifying rendered commands.

**Acceptance Scenarios**:

1. **Given** a profile with approved optional flags, **When** the serve command
   is rendered, **Then** the command includes the expected vLLM flags and
   values.
2. **Given** a profile with an unknown or risky optional flag, **When** the
   profile is loaded, **Then** the system rejects it with a clear safety error.

---

### User Story 2 - Generate Scheduler Sweep Plans (Priority: P2)

As the operator, I want a bounded Qwen scheduler/prefill sweep around the
current performance champion so I can measure batching and prefill effects.

**Why this priority**: The flag catalog identified scheduler knobs as safe
session-level candidates, and they are likely to influence throughput/latency.

**Independent Test**: Can be tested by generating the sweep plan and verifying
candidate count, optional flag overrides, and preview safety.

**Acceptance Scenarios**:

1. **Given** the scheduler sweep definition, **When** a plan is generated,
   **Then** it includes only approved optional flags and deterministic trial
   identifiers.
2. **Given** the generated plan, **When** preview is rendered, **Then** all
   actions are session-mutating only and no GX10 connection is opened.

---

### User Story 3 - Preserve Existing Sweep Safety (Priority: P3)

As the operator, I want existing sweeps and profiles to keep working while the
new optional flag path is added.

**Why this priority**: The optimizer already has trusted benchmark history; new
flags should not regress previous workflows.

**Independent Test**: Can be tested by running the existing unit and CLI suites.

**Acceptance Scenarios**:

1. **Given** existing Qwen sweep configs, **When** tests run, **Then** existing
   commands still render and rank successfully.
2. **Given** optional flags are omitted, **When** a serve profile renders,
   **Then** the command matches the prior fixed profile behavior.

### Edge Cases

- Optional boolean flags are false and should not be emitted.
- Optional integer flags are zero, negative, or not integers.
- Optional flag names use underscores in JSON but must render as hyphenated
  command flags.
- A risky policy flag is attempted through the optional flag path.
- A sweep override attempts to set an unapproved optional flag.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support approved optional vLLM serve flags in serve
  profiles.
- **FR-002**: System MUST render optional flag names with vLLM hyphenated
  command syntax.
- **FR-003**: System MUST reject unknown, risky, persistent, or not-relevant
  optional flags.
- **FR-004**: System MUST support optional boolean flags that render only when
  true.
- **FR-005**: System MUST support optional integer flags for scheduler values.
- **FR-006**: System MUST allow sweep overrides for approved optional flags.
- **FR-007**: System MUST provide a bounded Qwen scheduler sweep config.
- **FR-008**: System MUST NOT allow arbitrary shell fragments or unclassified
  vLLM flags in profiles or sweeps.
- **FR-009**: System MUST NOT install packages, alter persistent host settings,
  or run concurrent load tests.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Objective family is scheduler/prefill session-level Qwen vLLM
  optimization.
- **ER-002**: Reproducibility inputs MUST include optional flags, values,
  prompt set, baseline reference, policy rationale, and artifact paths.
- **ER-003**: Raw artifacts MUST include plan, preview, per-trial artifacts,
  results JSONL, ranking report, and comparison report when live execution is
  run.
- **ER-004**: GX10 actions remain session-mutating only during live execution.
- **ER-005**: Dry-run preview MUST be available before live execution.

### Key Entities *(include if feature involves data)*

- **Optional Serve Flag**: Approved vLLM flag with type, rendering behavior, and
  safety rationale.
- **Extended Serve Profile**: Base profile plus optional serve flags.
- **Scheduler Sweep Definition**: Candidate grid for batching, prefill, and
  prefix-cache flags.
- **Scheduler Candidate**: One concrete optional flag combination.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Unit tests verify approved optional flags render exactly as
  expected.
- **SC-002**: Unit tests verify unapproved optional flags are rejected.
- **SC-003**: Existing profile render tests continue to pass without optional
  flags.
- **SC-004**: Scheduler sweep plan generation produces the expected bounded
  candidate and trial counts.
- **SC-005**: Full local test suite passes before any live scheduler sweep is
  attempted.

## Assumptions

- The first scheduler sweep should use the current Qwen performance champion as
  the base: `gpu_memory_utilization=0.90`, `max_model_len=32768`, and
  `performance_mode=interactivity`.
- Optional flags are supplied with underscore names in JSON for consistency
  with existing profile fields.
- The checked-in Qwen safe policy remains the authority for the first set of
  optional flags.
