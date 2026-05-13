# Feature Specification: Qwen Baseline Benchmark

**Feature Branch**: `004-qwen-baseline-benchmark`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add a Qwen baseline benchmark workflow for the GX10. The system should generate a dry-run benchmark plan from the known Qwen serve profile and a fixed prompt set, start the server through the existing safe lifecycle wrapper, wait for readiness, run a small controlled sequence of OpenAI-compatible chat requests, capture request durations, token counts, tokens per second, response status, raw responses, server logs, cleanup results, and a baseline summary report, then stop the server cleanly. This feature must not optimize parameters, install packages, or tune Linux/NVIDIA settings."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preview the Baseline Benchmark (Priority: P1)

As the operator, I want a dry-run benchmark plan that lists the Qwen profile,
prompt set, request count, metrics, artifacts, and cleanup behavior before any
remote server is started.

**Why this priority**: A baseline benchmark is the first measurement step and
must be auditable before it mutates the remote session.

**Independent Test**: Can be tested locally by rendering a benchmark plan and
verifying no SSH commands are executed.

**Acceptance Scenarios**:

1. **Given** the Qwen profile and fixed prompt set, **When** the operator
   generates a benchmark plan, **Then** the output lists serve lifecycle,
   prompts, metrics, artifact paths, and cleanup.
2. **Given** an empty prompt set, **When** the operator generates a plan,
   **Then** the system rejects it with a validation error.

---

### User Story 2 - Run Controlled Baseline Requests (Priority: P2)

As the operator, I want the system to start Qwen, run a small fixed sequence of
chat requests, and measure request durations and token throughput.

**Why this priority**: This produces the first real baseline that later
parameter optimization can compare against.

**Independent Test**: Can be tested with mocked lifecycle/request outputs and,
after approval, one live GX10 baseline run.

**Acceptance Scenarios**:

1. **Given** safety checks pass and Qwen becomes ready, **When** the baseline
   runs, **Then** each prompt receives exactly one response and records status,
   duration, usage tokens, and tokens/sec.
2. **Given** one request fails, **When** the baseline completes, **Then** the
   summary records the failure and still attempts cleanup.

---

### User Story 3 - Save Baseline Artifacts and Summary (Priority: P3)

As the operator, I want raw responses, server logs, cleanup results, and a
summary report saved locally so future optimization runs can compare against
this baseline.

**Why this priority**: Optimization without a reproducible baseline is just
wandering around with a stopwatch.

**Independent Test**: Can be tested by saving mocked benchmark results and
verifying redaction, raw artifact links, and summary metrics.

**Acceptance Scenarios**:

1. **Given** a completed baseline run, **When** artifacts are saved, **Then**
   the summary includes per-request metrics and aggregate metrics.
2. **Given** configured secret values appear in logs or responses, **When**
   artifacts are saved, **Then** those values are redacted.

### Edge Cases

- Port 8001 is occupied before the benchmark starts.
- A stale vLLM process is holding GPU memory.
- The model takes longer than expected to become ready.
- One prompt times out while others succeed.
- A response lacks usage token counts.
- Cleanup succeeds but final process verification finds a leftover child.
- Artifacts contain username, IP, model cache paths, or tokens.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a dry-run baseline benchmark plan without
  contacting the GX10.
- **FR-002**: System MUST use the existing Qwen serve profile and safe lifecycle
  checks before live benchmark requests.
- **FR-003**: System MUST run a fixed prompt set with one request per prompt.
- **FR-004**: System MUST capture response status, request duration, token
  counts when available, and tokens/sec when token counts are available.
- **FR-005**: System MUST save raw responses and a summary report.
- **FR-006**: System MUST save server logs and cleanup verification.
- **FR-007**: System MUST attempt cleanup after success, failure, or timeout.
- **FR-008**: System MUST redact configured secret values from all artifacts.
- **FR-009**: System MUST NOT change profile parameters during this feature.
- **FR-010**: System MUST NOT install packages, tune Linux, tune NVIDIA, or run
  broad load tests in this feature.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Objective family is baseline measurement, not optimization.
- **ER-002**: Artifacts MUST include plan, prompt set, raw responses, per-request
  metrics, aggregate metrics, logs, cleanup, and redaction report.
- **ER-003**: The benchmark MUST record the exact serve profile and prompt set.
- **ER-004**: The benchmark MUST run sequentially for this feature.
- **ER-005**: Later optimization features MUST be able to compare against this
  baseline summary.

### Key Entities *(include if feature involves data)*

- **Benchmark Plan**: Dry-run plan describing serve profile, prompt set,
  request sequence, metrics, artifacts, and cleanup.
- **Prompt Case**: One fixed prompt with identifier, messages, max tokens, and
  expected request type.
- **Request Metric**: Duration, response status, token counts, and tokens/sec
  for one request.
- **Baseline Summary**: Aggregate report across all prompt cases.
- **Benchmark Artifact**: Saved plan, prompts, raw responses, metrics, logs, and
  cleanup evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dry-run plan generation performs zero SSH commands in tests.
- **SC-002**: Mocked benchmark tests produce one metric row per prompt.
- **SC-003**: Summary computes success count, failure count, mean latency, and
  aggregate tokens/sec when usage data is present.
- **SC-004**: Cleanup is attempted in 100% of mocked post-start failure paths.
- **SC-005**: A live baseline run, when approved, writes raw responses, metrics,
  logs, cleanup evidence, and summary artifacts.

## Assumptions

- The smoke-serve workflow has already proven the Qwen profile can start and
  clean up.
- The fixed prompt set should be small enough to avoid load testing.
- Sequential requests are sufficient for the first baseline.
- This feature establishes measurement shape before parameter optimization.
