# Feature Specification: Qwen Parameter Sweep

**Feature Branch**: `005-qwen-parameter-sweep`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add a deterministic Qwen parameter sweep workflow that generates bounded session-level vLLM serve-profile variants from the known Qwen baseline profile, previews every trial before live execution, optionally runs trials sequentially through the existing safe serve and benchmark lifecycle, records raw per-trial artifacts, compares results against the baseline summary, and ranks candidates for throughput, latency, and balanced objectives. The feature must not install packages, change persistent Linux or NVIDIA settings, or expand into broad load testing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a Deterministic Sweep Plan (Priority: P1)

As the operator, I want to define a bounded set of safe Qwen vLLM parameter
choices and generate a deterministic ordered sweep plan before starting any
remote server.

**Why this priority**: Parameter optimization must begin with reproducible
trial definitions that can be reviewed locally before the GX10 is touched.

**Independent Test**: Can be tested locally by generating the same sweep plan
twice and verifying identical trial identifiers, order, profile overrides,
objectives, and artifact destinations.

**Acceptance Scenarios**:

1. **Given** the Qwen baseline profile and a bounded parameter space, **When**
   the operator generates a sweep plan twice, **Then** both plans contain the
   same trials in the same order with the same identifiers.
2. **Given** a parameter space that includes a disallowed or persistent system
   setting, **When** the operator generates a sweep plan, **Then** the system
   rejects it with a clear safety error.

---

### User Story 2 - Preview Trial Execution and Safety (Priority: P2)

As the operator, I want a dry-run preview of every trial's serve parameters,
benchmark workload, artifacts, cleanup, and expected side effects so I can
review the sweep before live execution.

**Why this priority**: The sweep will repeatedly start and stop a real remote
vLLM server, so the full execution shape must be auditable before live use.

**Independent Test**: Can be tested without SSH by rendering a sweep preview
from a plan and verifying all trials are classified as session-mutating only.

**Acceptance Scenarios**:

1. **Given** a valid sweep plan, **When** the operator requests a dry-run
   preview, **Then** the output lists every trial, changed parameters,
   benchmark prompt set, metric targets, artifact paths, and cleanup action.
2. **Given** any trial with an unsafe command or unsupported side effect,
   **When** the preview is generated, **Then** the output marks the plan as
   blocked and identifies the rejected trial.

---

### User Story 3 - Run and Rank a Small Sweep (Priority: P3)

As the operator, I want to run a small sequential sweep through the existing
safe lifecycle, compare each candidate with the baseline, and rank candidates
for throughput, latency, and balanced objectives.

**Why this priority**: This turns the project from measurement into practical
optimization while preserving traceability and remote safety.

**Independent Test**: Can be tested with mocked trial outputs and fixture
baseline data, then verified with one approved live GX10 sweep.

**Acceptance Scenarios**:

1. **Given** a valid sweep plan and approved live execution, **When** the sweep
   runs, **Then** each trial starts from a clean preflight state, executes the
   fixed benchmark sequence, saves raw artifacts, and attempts cleanup before
   the next trial.
2. **Given** one trial fails to start, times out, or returns invalid metrics,
   **When** the sweep completes, **Then** the failed trial is recorded with a
   reason, cleanup is attempted, and remaining eligible trials can continue.
3. **Given** completed trial metrics and a baseline summary, **When** ranking
   is generated, **Then** each recommendation names its objective, constraints,
   score, tie-breakers, baseline delta, and source artifacts.

### Edge Cases

- Parameter combinations exceed the safe model length or GPU memory bounds.
- A trial uses a value type that does not match the parameter definition.
- The baseline summary is missing, malformed, or from a different prompt set.
- Port 8001 is occupied before a trial starts.
- vLLM starts for one trial but fails readiness before benchmarking.
- Cleanup succeeds for the process but GPU memory remains occupied.
- A trial succeeds but lacks token usage data for one or more responses.
- Two candidates tie under the selected objective.
- The operator interrupts a sweep between trials.
- Logs include usernames, host addresses, cache paths, tokens, or model paths.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a bounded sweep definition for safe
  session-level vLLM serve parameters derived from the Qwen baseline profile.
- **FR-002**: System MUST generate deterministic trial identifiers and ordering
  from the same sweep definition and seed inputs.
- **FR-003**: System MUST reject persistent Linux, NVIDIA, package-management,
  credential-printing, destructive, or unbounded shell actions.
- **FR-004**: System MUST generate a dry-run preview that lists every trial,
  changed parameter, objective, benchmark workload, artifact destination, and
  cleanup action without contacting the GX10.
- **FR-005**: System MUST support throughput, latency, and balanced objective
  ranking for sweep results.
- **FR-006**: System MUST record the baseline summary used for comparison or
  explicitly record that no baseline comparison was available.
- **FR-007**: System MUST save raw per-trial artifacts, derived metrics,
  ranking reports, command logs, cleanup evidence, and failure records.
- **FR-008**: System MUST attempt cleanup after every trial that starts,
  regardless of success, failure, timeout, or interruption.
- **FR-009**: System MUST continue past an individual failed trial when it is
  safe to do so and record why any trial was skipped.
- **FR-010**: System MUST redact configured secret values from all artifacts
  and reports.
- **FR-011**: System MUST limit the first sweep workflow to small sequential
  runs, not broad concurrent load testing.
- **FR-012**: System MUST NOT install packages, alter persistent host settings,
  or change Linux/NVIDIA configuration in this feature.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Objective family is session-level Qwen vLLM parameter
  optimization for throughput, latency, and balanced rankings.
- **ER-002**: Reproducibility inputs MUST include sweep definition, seed,
  baseline profile, prompt set identifier, baseline summary path, model
  identity, vLLM version when available, host facts when available, command
  lines, and repository commit when available.
- **ER-003**: Raw artifacts MUST include sweep definition, sweep plan, dry-run
  preview, per-trial benchmark artifacts, logs, cleanup evidence, failure
  records, aggregate metrics, and ranking report.
- **ER-004**: GX10 actions are session-mutating only during live execution and
  MUST have dry-run previews before live use.
- **ER-005**: Persistent-mutating actions are out of scope and MUST be blocked.

### Key Entities *(include if feature involves data)*

- **Sweep Definition**: Operator-authored objective, parameter space, bounds,
  seed, prompt set, baseline profile, baseline summary reference, and maximum
  trial count.
- **Parameter Candidate**: One candidate value for a safe vLLM serve parameter,
  including type, allowed values, and safety bounds.
- **Sweep Trial**: One concrete profile variant with deterministic identifier,
  changed parameters, objective metadata, artifact paths, and execution state.
- **Sweep Preview**: Dry-run report describing all trial actions, side-effect
  classifications, blocked reasons, metrics, and cleanup.
- **Trial Result**: Per-trial metrics, raw response references, command logs,
  cleanup evidence, failure reason, and baseline deltas.
- **Sweep Ranking**: Objective-specific ordered recommendations with score,
  constraints, tie-breakers, baseline comparison, and source artifact links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Re-running the same sweep definition produces identical trial
  order and identifiers in 100% of deterministic tests.
- **SC-002**: Dry-run preview performs zero SSH commands in tests and lists
  100% of planned trials and cleanup actions.
- **SC-003**: Safety validation blocks 100% of persistent-mutating and
  disallowed parameter actions covered by unit tests.
- **SC-004**: Fixture-based ranking produces throughput, latency, and balanced
  reports that link 100% of ranked candidates back to trial artifacts.
- **SC-005**: A mocked sweep with at least one failing trial records the failure,
  attempts cleanup, and still ranks successful trials.
- **SC-006**: The first live sweep, when approved, runs sequentially and writes
  per-trial artifacts plus an aggregate ranking report.

## Assumptions

- The existing Qwen baseline profile and prompt set remain the starting point.
- Initial parameter candidates are vLLM serve options that are already exposed
  through profile rendering, such as GPU memory utilization, maximum model
  length, and performance mode.
- The first sweep is intentionally small and sequential so remote lifecycle
  behavior stays understandable.
- Baseline comparison uses the most recent approved baseline summary supplied
  by the operator or configured path.
- Persistent Linux/NVIDIA tuning will be handled by a later, explicitly
  authorized spec.
