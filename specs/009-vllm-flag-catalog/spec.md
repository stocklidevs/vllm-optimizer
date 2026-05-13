# Feature Specification: vLLM Flag Catalog

**Feature Branch**: `009-vllm-flag-catalog`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add read-only vLLM flag discovery and safe performance knob cataloging. The system should capture the exact vLLM version and vLLM serve help text from the GX10, parse available serve flags, classify known performance-relevant flags into safe session-sweepable, session-risky, blocked persistent/system, and not-relevant categories, save redacted artifacts, and provide a checked-in seed policy for Qwen future sweeps. This feature must be read-only on the GX10 and must not start vLLM, run benchmarks, install packages, or change Linux/NVIDIA settings."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Parse Available vLLM Serve Flags (Priority: P1)

As the operator, I want the tool to parse a captured full `vllm serve --help` output
so future sweeps can be based on the actual installed vLLM flags.

**Why this priority**: vLLM flags vary by version; parsing the installed help
text avoids guessing from external docs.

**Independent Test**: Can be tested with a fixture help text and no GX10 access.

**Acceptance Scenarios**:

1. **Given** a captured serve help text, **When** the parser runs, **Then** it
   extracts long option names and preserves source text.
2. **Given** malformed or empty help text, **When** parsing runs, **Then** the
   system rejects it with a clear validation error.

---

### User Story 2 - Classify Performance-Relevant Flags (Priority: P2)

As the operator, I want known vLLM flags classified by safety and relevance so
future sweeps can use a policy instead of ad hoc decisions.

**Why this priority**: The optimizer should know which flags are safe to sweep,
which need caution, and which are outside scope.

**Independent Test**: Can be tested by applying a checked-in policy to fixture
flags and verifying expected categories.

**Acceptance Scenarios**:

1. **Given** parsed flags and a Qwen safe policy, **When** classification runs,
   **Then** safe session-sweepable flags include known performance knobs that
   are present in the installed vLLM help.
2. **Given** a policy flag that is absent from the installed vLLM help, **When**
   classification runs, **Then** the catalog records it as unavailable.

---

### User Story 3 - Capture GX10 Flag Catalog Read-Only (Priority: P3)

As the operator, I want to capture the GX10 vLLM version and serve help text
over SSH without starting vLLM or mutating the host.

**Why this priority**: Live capture anchors the catalog to the actual machine
and installed environment.

**Independent Test**: Can be tested with a mock executor, then with one approved
read-only GX10 run.

**Acceptance Scenarios**:

1. **Given** GX10 SSH config and approval, **When** live capture runs, **Then**
   it records version, help text, parsed flags, classified catalog, redaction
   report, and no mutating action.
2. **Given** the vLLM command is unavailable, **When** capture runs, **Then**
   the failure is recorded without running fallback install or mutation.

### Edge Cases

- vLLM help wraps option descriptions across multiple lines.
- A flag has comma-separated aliases.
- A flag appears in docs but not installed help.
- The configured vLLM executable path differs from `vllm`.
- SSH succeeds but the vLLM environment is missing.
- Help output contains usernames, paths, or host values.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse long vLLM serve flags from captured help text.
- **FR-002**: System MUST classify parsed flags using a checked-in Qwen policy.
- **FR-003**: System MUST record unavailable policy flags.
- **FR-004**: System MUST save raw full help text, version output, catalog JSON, and
  redaction report.
- **FR-005**: System MUST support mock/local catalog generation without GX10
  access.
- **FR-006**: System MUST support an approved read-only SSH capture from GX10.
- **FR-007**: System MUST NOT start vLLM, run benchmark requests, install
  packages, or change Linux/NVIDIA settings.
- **FR-008**: System MUST redact configured secret values from artifacts.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Objective family is flag discovery and safe optimizer policy
  preparation.
- **ER-002**: Artifacts MUST include source help text, vLLM version, parsed
  flags, category assignments, unavailable flags, and redaction report.
- **ER-003**: GX10 action classification is read-only only.
- **ER-004**: Future sweep specs SHOULD consume the catalog before adding new
  flags.
- **ER-005**: Persistent/system tuning remains blocked.

### Key Entities *(include if feature involves data)*

- **Flag Policy**: Checked-in category map and rationale for known vLLM flags.
- **Parsed Flag**: One installed vLLM serve option extracted from help text.
- **Flag Catalog**: Classified view of installed flags, unavailable policy
  flags, source metadata, and safety notes.
- **Flag Capture Artifact**: Raw version/help output and redaction report from
  local mock or read-only SSH capture.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Fixture help parsing extracts 100% of expected long flags in unit
  tests.
- **SC-002**: Classification places known performance flags into expected
  categories in unit tests.
- **SC-003**: Mock capture writes version, help, catalog, and redaction artifacts
  without opening SSH.
- **SC-004**: Live GX10 capture, when approved, completes without starting vLLM
  or leaving any server process.
- **SC-005**: Unavailable policy flags are listed in 100% of catalog outputs.

## Assumptions

- The Qwen profile's `vllm_executable` is the preferred executable for capture.
- vLLM help/version commands are read-only.
- The first policy should be conservative and can be expanded by future specs.
