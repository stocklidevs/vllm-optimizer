# Feature Specification: vLLM Optimization Lab

**Feature Branch**: `001-vllm-optimization-lab`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Build a deterministic vLLM optimization lab that can define objective families, generate reproducible experiment plans, safely execute dry-run and live benchmark workflows against an Asus GX10 over Tailscale SSH, collect raw artifacts and telemetry, and rank vLLM configurations for throughput, latency, memory efficiency, tool-call reliability, structured output validity, long-context stability, serving stability, and balanced weighted profiles."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a Reproducible Experiment Plan (Priority: P1)

As the operator, I want to define an optimization objective and parameter
space, then generate a deterministic ordered trial plan before touching the
GX10.

**Why this priority**: This provides value without remote risk and establishes
the reproducibility foundation required by all later work.

**Independent Test**: Can be tested by running the same experiment definition
twice and verifying the generated trial list, seeds, and recorded metadata are
identical.

**Acceptance Scenarios**:

1. **Given** an experiment definition with a throughput objective and bounded
   vLLM parameter space, **When** the operator generates a plan twice, **Then**
   both outputs contain the same trials in the same order.
2. **Given** an experiment definition with missing objective criteria, **When**
   the operator requests a plan, **Then** the system rejects it with a clear
   validation error.

---

### User Story 2 - Preview Safe Remote Actions (Priority: P2)

As the operator, I want to preview all planned GX10 SSH actions in dry-run mode
so I can verify commands, side effects, artifacts, and cleanup before live
execution.

**Why this priority**: The project will control a real remote machine; dry-run
preview is the safety bridge between local planning and live benchmarking.

**Independent Test**: Can be tested with a mock remote executor that receives a
generated plan and returns a full command preview without opening SSH.

**Acceptance Scenarios**:

1. **Given** a valid experiment plan, **When** the operator requests dry-run
   execution, **Then** the system lists every read-only probe, vLLM lifecycle
   action, benchmark action, artifact destination, and cleanup action.
2. **Given** a planned command outside the safety allowlist, **When** dry-run
   execution is requested, **Then** the system blocks the plan and identifies
   the rejected action.

---

### User Story 3 - Capture and Rank Benchmark Results (Priority: P3)

As the operator, I want benchmark results and telemetry to be stored as raw
artifacts and summarized into ranked recommendations for a named objective.

**Why this priority**: Ranking is the visible payoff of the optimizer, but it
must depend on trustworthy artifacts from the earlier stories.

**Independent Test**: Can be tested with fixture artifacts that simulate
benchmark runs and verify scoring, ranking, and report traceability.

**Acceptance Scenarios**:

1. **Given** raw fixture results for several configurations, **When** the
   operator requests a throughput ranking, **Then** the report orders
   configurations by the declared throughput criteria and links each result to
   source artifacts.
2. **Given** incomplete or malformed result artifacts, **When** ranking is
   requested, **Then** the system excludes invalid trials with documented
   reasons instead of silently ranking them.

---

### Edge Cases

- A generated parameter combination is invalid for the selected model or vLLM
  version.
- The GX10 is unreachable over Tailscale SSH during live execution.
- vLLM fails to start, exits early, or emits an out-of-memory error.
- Benchmark output is partial because a run is interrupted.
- Telemetry is missing from one source but benchmark output exists.
- Two configurations tie under the primary metric.
- A user requests a persistent Linux/NVIDIA setting change.
- A model path, hostname, token, or SSH identity appears in captured output.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the operator to define named objective
  families for throughput, latency, memory efficiency, tool-call reliability,
  structured output validity, long-context stability, serving stability, and
  balanced weighted profiles.
- **FR-002**: System MUST validate experiment definitions before generating
  trial plans.
- **FR-003**: System MUST generate deterministic trial ordering from the same
  experiment definition and seed inputs.
- **FR-004**: System MUST record all reproducibility metadata required to
  recreate a trial plan.
- **FR-005**: System MUST support dry-run execution that previews remote
  actions without opening a live SSH session.
- **FR-006**: System MUST classify remote actions as read-only,
  session-mutating, or persistent-mutating.
- **FR-007**: System MUST block commands that are not explicitly allowed for
  the selected execution mode.
- **FR-008**: System MUST collect or accept raw benchmark artifacts, telemetry,
  command logs, and failure records for each trial.
- **FR-009**: System MUST produce ranked recommendations only for a named
  objective with declared constraints and tie-breakers.
- **FR-010**: System MUST link every summary result back to raw trial
  artifacts.
- **FR-011**: System MUST redact configured secret values from stored logs and
  reports.
- **FR-012**: System MUST keep local fixture and mock-executor workflows usable
  when the GX10 is unavailable.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: The initial feature MUST support at least dry-run planning for
  all objective families and fixture-based ranking for at least throughput and
  latency.
- **ER-002**: Each run record MUST include objective, constraints, tie-breakers,
  parameter space, seeds, request mix, prompt corpus identifier, model identity,
  vLLM version, host facts, driver/CUDA facts, environment variables, command
  lines, and repository commit when available.
- **ER-003**: Raw artifacts MUST include trial definitions, command previews or
  command logs, benchmark outputs, telemetry records, validation errors, and
  generated summaries.
- **ER-004**: GX10 actions MUST default to read-only or dry-run unless a later
  specification explicitly authorizes live session mutation.
- **ER-005**: Dry-run output MUST be reviewable before any live remote
  execution.

### Key Entities *(include if feature involves data)*

- **Experiment Definition**: The operator-authored objective, constraints,
  parameter space, workload, seeds, target host profile, and execution mode.
- **Trial Plan**: The deterministic ordered list of concrete configurations
  produced from an experiment definition.
- **Remote Action**: A planned command or lifecycle operation classified by
  target, mode, expected side effects, allowlist status, and cleanup behavior.
- **Trial Artifact**: Raw data captured for one trial, including commands,
  metrics, telemetry, logs, errors, and metadata.
- **Objective Score**: A computed score and ranking explanation for a trial
  under a specific objective family.
- **Recommendation Report**: A human-readable and machine-readable summary that
  ranks configurations and links to source artifacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Re-running the same experiment definition produces identical
  trial ordering and trial identifiers in 100% of local deterministic tests.
- **SC-002**: Dry-run mode displays 100% of planned remote actions, artifact
  destinations, and cleanup actions before live execution is possible.
- **SC-003**: Safety validation blocks 100% of commands outside the configured
  allowlist in unit tests.
- **SC-004**: Fixture-based ranking reports link 100% of ranked trials back to
  their raw artifacts.
- **SC-005**: The first useful increment can be demonstrated without live GX10
  access by using fixture artifacts and a mock remote executor.

## Assumptions

- The primary user is the project operator running the local controller from
  this repository.
- The GX10 is reachable through Tailscale SSH when live execution is later
  enabled.
- Initial development prioritizes deterministic local planning, dry-run
  previews, and fixture-based result ranking before live remote mutation.
- Persistent Linux/NVIDIA tuning is out of scope for the initial feature unless
  a later specification explicitly authorizes it.
- vLLM model choices and exact benchmark corpora will be supplied as experiment
  definitions rather than hard-coded project defaults.
