# Feature Specification: Qwen Smoke Serve

**Feature Branch**: `003-qwen-smoke-serve`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add a safe Qwen vLLM smoke serve workflow for the GX10. The system should generate a dry-run lifecycle plan from the Qwen3 Coder Next profile, refuse to start if port 8001 or another matching vLLM process is active, start the server with the discovered qwen3next venv executable only when explicitly requested, poll readiness, run one tiny OpenAI-compatible request, collect logs and timing artifacts, stop the server cleanly, verify cleanup, and never install packages or tune Linux/NVIDIA settings."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preview the Smoke Serve Lifecycle (Priority: P1)

As the operator, I want to generate a dry-run lifecycle plan so I can inspect
the exact serve command, safety checks, readiness checks, smoke request, and
cleanup steps before the GX10 starts a model.

**Why this priority**: Starting vLLM is the first session-mutating operation;
the operator needs an auditable plan before live execution.

**Independent Test**: Can be tested locally by rendering a plan from the Qwen
profile and verifying no remote action is executed.

**Acceptance Scenarios**:

1. **Given** the Qwen profile, **When** the operator generates a smoke plan,
   **Then** the output lists preflight checks, serve command, readiness poll,
   smoke request, log paths, cleanup command, and cleanup verification.
2. **Given** an invalid profile, **When** the operator generates a smoke plan,
   **Then** the system rejects the plan with a clear validation error.

---

### User Story 2 - Refuse Unsafe Live Start Conditions (Priority: P2)

As the operator, I want live smoke serve to refuse to start when port 8001 or a
matching vLLM process is already active so we do not collide with an existing
server.

**Why this priority**: The smoke workflow must not disrupt a running vLLM
server or hide a port conflict behind benchmark failures.

**Independent Test**: Can be tested with mocked SSH preflight outputs that show
an occupied port or existing vLLM process.

**Acceptance Scenarios**:

1. **Given** port 8001 is occupied, **When** live smoke serve is requested,
   **Then** the system refuses to start and records the refusal artifact.
2. **Given** a matching Qwen vLLM process is already running, **When** live
   smoke serve is requested, **Then** the system refuses to start and records
   the matching process details.

---

### User Story 3 - Run and Clean Up One Smoke Request (Priority: P3)

As the operator, I want the system to start the known Qwen vLLM profile, wait
for readiness, send one tiny request, save artifacts, stop the server, and
verify that cleanup succeeded.

**Why this priority**: This proves controlled vLLM lifecycle management before
larger benchmark automation.

**Independent Test**: Can be tested with mocked lifecycle executor outputs and,
after approval, one live GX10 smoke run.

**Acceptance Scenarios**:

1. **Given** safety checks pass, **When** live smoke serve runs, **Then** the
   system starts vLLM, records readiness timing, sends one tiny request,
   records the response status and duration, stops vLLM, and verifies no
   managed process remains.
2. **Given** readiness times out, **When** live smoke serve fails, **Then** the
   system still attempts cleanup and records logs and failure reason.

### Edge Cases

- SSH succeeds but the Qwen venv executable is missing.
- Port 8001 is occupied by a non-vLLM process.
- Another vLLM process is already serving the same model or port.
- The model download/cache step makes startup exceed the readiness timeout.
- The server starts but the smoke request fails.
- Cleanup command runs but the process remains.
- Logs contain local paths, username, IP address, model cache paths, or tokens.
- The operator tries to run live smoke without first producing a plan.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a dry-run smoke lifecycle plan from the Qwen
  serve profile without contacting the GX10.
- **FR-002**: System MUST include preflight port and process checks in the plan.
- **FR-003**: System MUST refuse live start when the target port is occupied.
- **FR-004**: System MUST refuse live start when a matching vLLM process is
  already active.
- **FR-005**: System MUST start vLLM only with the configured profile command
  and discovered venv executable.
- **FR-006**: System MUST poll readiness before sending the smoke request.
- **FR-007**: System MUST send exactly one tiny OpenAI-compatible smoke request
  during this feature.
- **FR-008**: System MUST collect serve logs, preflight outputs, readiness
  timings, smoke request result, cleanup result, and final process check.
- **FR-009**: System MUST attempt cleanup after success, failure, or timeout.
- **FR-010**: System MUST redact configured secret values from saved artifacts.
- **FR-011**: System MUST NOT install packages, change model files, tune Linux,
  tune NVIDIA settings, or run benchmark load in this feature.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: This feature validates lifecycle control for one known profile
  rather than optimizing performance.
- **ER-002**: Artifacts MUST include dry-run plan, preflight checks, raw logs,
  timing data, response status, cleanup verification, and redaction report.
- **ER-003**: Live actions are session-mutating and MUST have cleanup steps.
- **ER-004**: The smoke request MUST be minimal and not a throughput benchmark.
- **ER-005**: Mock lifecycle tests MUST exist before live smoke execution.

### Key Entities *(include if feature involves data)*

- **Smoke Serve Plan**: Dry-run lifecycle plan derived from a serve profile.
- **Preflight Check**: Read-only remote check for port/process safety.
- **Managed Serve Process**: vLLM process started by the smoke workflow.
- **Readiness Probe**: Poll that determines when the OpenAI-compatible API is
  available.
- **Smoke Request**: One tiny request sent after readiness.
- **Smoke Artifact**: Saved plan, logs, timings, response, cleanup, and summary.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dry-run plan generation succeeds locally and performs zero SSH
  commands in tests.
- **SC-002**: Mocked occupied-port and existing-process tests refuse live start
  100% of the time.
- **SC-003**: Mocked failure tests attempt cleanup 100% of the time after start.
- **SC-004**: Live smoke run, when approved, records readiness, request, cleanup,
  and final process-check artifacts.
- **SC-005**: Redaction tests remove 100% of configured secret values from saved
  smoke artifacts.

## Assumptions

- Key-based SSH to the GX10 is already working.
- The Qwen serve profile points to `$HOME/qwen3next-venv/bin/vllm`.
- Port 8001 is the intended port for this smoke workflow.
- The first smoke request may take longer if the model cache is cold.
- This feature starts one vLLM process only for lifecycle validation and then
  stops it.
