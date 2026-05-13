# Feature Specification: GX10 Read-Only Discovery

**Feature Branch**: `002-gx10-readonly-discovery`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add read-only GX10 discovery over Tailscale SSH. The system should verify connectivity, collect host, operating system, GPU, NVIDIA driver, CUDA visibility, Python, and vLLM environment facts, redact configured secrets, save discovery artifacts, and fail safely without mutating the remote host or starting vLLM."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verify GX10 Connectivity Safely (Priority: P1)

As the operator, I want to check whether the GX10 is reachable over Tailscale
SSH using read-only commands so I know whether live discovery can proceed.

**Why this priority**: Connectivity is the first real contact with the remote
machine and must prove the safety boundary before collecting deeper facts.

**Independent Test**: Can be tested with a mocked SSH executor that returns a
successful identity response and with a mocked timeout/failure response.

**Acceptance Scenarios**:

1. **Given** valid local connection settings, **When** discovery starts, **Then**
   the system records a successful read-only connectivity check.
2. **Given** the GX10 is unreachable, **When** discovery starts, **Then** the
   system records the failure, avoids all remaining probes, and exits with a
   clear non-mutating failure result.

---

### User Story 2 - Collect Host and Accelerator Facts (Priority: P2)

As the operator, I want to collect host, operating system, GPU, NVIDIA driver,
CUDA visibility, Python, and vLLM facts so later optimization plans can be tied
to the actual GX10 environment.

**Why this priority**: Reproducible optimization requires the machine state to
be captured before benchmark planning or vLLM execution.

**Independent Test**: Can be tested by feeding recorded command outputs into
the discovery parser and verifying the normalized facts.

**Acceptance Scenarios**:

1. **Given** connectivity succeeds, **When** discovery runs, **Then** the system
   captures normalized facts for host identity, operating system, GPU, NVIDIA
   driver, CUDA visibility, Python, and vLLM availability.
2. **Given** one optional probe is unavailable, **When** discovery runs, **Then**
   the system records that probe as unavailable and preserves successful facts
   from other probes.

---

### User Story 3 - Save Redacted Discovery Artifacts (Priority: P3)

As the operator, I want raw and normalized discovery artifacts saved locally
with configured secrets redacted so I can inspect the environment without
leaking credentials or private paths.

**Why this priority**: Discovery is only useful if it becomes auditable input
for later benchmark specs, and secret hygiene matters before we store logs.

**Independent Test**: Can be tested by passing command outputs containing
configured secret values and verifying the saved artifacts contain redactions.

**Acceptance Scenarios**:

1. **Given** discovery outputs include configured secret values, **When**
   artifacts are saved, **Then** those values are replaced with a redaction
   marker in raw and normalized artifacts.
2. **Given** discovery completes with partial failures, **When** artifacts are
   saved, **Then** the report includes successful facts, failed probe reasons,
   command classifications, and no secret values.

---

### Edge Cases

- The Tailscale host alias is missing or incorrect.
- SSH authentication fails or prompts for interaction.
- SSH connects but a probe command times out.
- `nvidia-smi` is absent, broken, or reports no visible GPU.
- CUDA is installed but unavailable to Python.
- Python exists but vLLM is not installed.
- vLLM import succeeds but version discovery fails.
- Probe output contains a hostname, token, model path, username, or private
  directory configured for redaction.
- The operator accidentally requests a non-read-only command.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the operator to define a GX10 discovery target
  using local configuration that is not committed to the repository.
- **FR-002**: System MUST perform an initial read-only connectivity check before
  running any other discovery probe.
- **FR-003**: System MUST run only read-only discovery probes in this feature.
- **FR-004**: System MUST collect host identity and operating system facts when
  connectivity succeeds.
- **FR-005**: System MUST collect GPU, NVIDIA driver, and CUDA visibility facts
  when available.
- **FR-006**: System MUST collect Python availability and vLLM availability
  facts when available.
- **FR-007**: System MUST record probe command, classification, start/end
  status, exit status, stdout, stderr, and timeout state for each attempted
  probe.
- **FR-008**: System MUST stop after connectivity failure and save a failure
  artifact explaining that no additional probes were attempted.
- **FR-009**: System MUST redact configured secret values from all saved raw and
  normalized artifacts.
- **FR-010**: System MUST save raw probe artifacts and normalized discovery
  summary artifacts locally.
- **FR-011**: System MUST reject or block any command classified as
  session-mutating or persistent-mutating for this feature.
- **FR-012**: System MUST NOT start, stop, benchmark, configure, install,
  upgrade, or tune vLLM, Linux, NVIDIA, CUDA, or system packages in this
  feature.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: This feature measures environment readiness rather than
  optimizing a performance objective.
- **ER-002**: Discovery artifacts MUST include target label, timestamp, tool
  version, local repository commit when available, probe definitions, command
  outputs, normalized facts, redaction metadata, and failure status.
- **ER-003**: Raw artifacts retained MUST include per-probe command logs and a
  normalized discovery report.
- **ER-004**: All GX10 actions in this feature MUST be read-only.
- **ER-005**: A mock discovery mode MUST support local tests without contacting
  the GX10.

### Key Entities *(include if feature involves data)*

- **Discovery Target**: Local, non-committed connection description for the
  remote GX10, including target label and SSH destination.
- **Probe Definition**: A read-only command the system is allowed to run,
  including its purpose, timeout, and expected parser.
- **Probe Result**: Raw result of one attempted probe, including command,
  status, stdout, stderr, and timing.
- **Host Facts**: Normalized host, OS, GPU, NVIDIA, CUDA, Python, and vLLM
  facts derived from probe results.
- **Discovery Artifact**: Saved raw and normalized records from one discovery
  run after redaction.
- **Redaction Rule**: A local value or pattern that must be removed from saved
  artifacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When connectivity fails in tests, 100% of non-connectivity probes
  are skipped and the failure artifact explains why.
- **SC-002**: In mocked successful discovery tests, the system captures at
  least host, OS, GPU/driver, CUDA visibility, Python, and vLLM availability
  fields in the normalized report.
- **SC-003**: Redaction tests remove 100% of configured secret values from raw
  and normalized artifacts.
- **SC-004**: Safety validation blocks 100% of session-mutating and
  persistent-mutating probe definitions in tests.
- **SC-005**: Discovery can be demonstrated locally with a mock executor and
  recorded outputs without contacting the GX10.

## Assumptions

- The operator will provide the GX10 SSH destination through local config or an
  environment variable outside version control.
- The known Tailscale address can be supplied locally as configuration and
  should be included in redaction values before artifacts are saved.
- Tailscale SSH or an SSH route to the GX10 already exists before live
  discovery is attempted.
- Initial implementation may use mock executor fixtures before a real SSH
  executor is enabled.
- This feature is read-only; starting vLLM, stopping vLLM, installing packages,
  changing drivers, or tuning Linux/NVIDIA settings belongs to later specs.
- Some facts may be unavailable on a healthy system; unavailable optional facts
  should not make the whole discovery fail after connectivity succeeds.
