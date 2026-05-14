# Feature Specification: System Tuning Discovery

**Feature Branch**: `026-system-tuning-discovery`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Start the more impactful tuning chapter with read-only Linux/NVIDIA/runtime discovery before mutating anything."

## User Scenarios & Testing

### User Story 1 - Capture Read-Only Tuning State (Priority: P1)

As an optimizer operator, I want a command that captures current Linux, NVIDIA, GPU, CPU, memory, kernel, and vLLM runtime tuning facts from the GX10 without changing anything so future specs can decide which knobs are safe to test.

**Why this priority**: We should not tune persistent or risky system settings without a reproducible baseline of current state and available knobs.

**Independent Test**: Run the command with a mock executor and verify it writes raw probes, a structured catalog, and a redaction report where every probe is classified read-only.

**Acceptance Scenarios**:

1. **Given** a target config and mock command outputs, **When** tuning discovery runs, **Then** it writes raw probe outputs and a catalog of parsed tuning facts.
2. **Given** a failed optional probe, **When** tuning discovery runs, **Then** the catalog records the knob as unavailable without failing the whole run.

---

### User Story 2 - Classify Future Tuning Knobs (Priority: P2)

As an optimizer developer, I want discovered knobs classified by mutation risk so later specs can require explicit safety gates before session or persistent changes.

**Why this priority**: The project must keep read-only discovery separate from session and persistent tuning.

**Independent Test**: Inspect the generated catalog and verify each known knob has a family, classification, source probe, current value, and future action hint.

**Acceptance Scenarios**:

1. **Given** discovery output, **When** the catalog is generated, **Then** GPU power, clock, CPU governor, THP, swap, limits, and environment facts are categorized consistently.
2. **Given** a knob that cannot be read, **When** the catalog is generated, **Then** it is marked unavailable with a reason.

## Requirements

### Functional Requirements

- **FR-001**: System MUST add a `system-tuning-discover` CLI command.
- **FR-002**: System MUST execute only read-only probes.
- **FR-003**: System MUST capture raw probe outputs, structured tuning catalog, and redaction report.
- **FR-004**: System MUST classify each catalog entry as read-only, session-mutating, persistent-mutating, or risky/unknown for future actions.
- **FR-005**: System MUST not fail the entire run when an optional probe fails.
- **FR-006**: System MUST support mock executor inputs for tests and offline development.

### Experiment Requirements

- **ER-001**: Objective family is discovery and future tuning eligibility, not benchmark performance.
- **ER-002**: Reproducibility inputs include target config, probe commands, raw outputs, parser version, and CLI version.
- **ER-003**: Raw artifacts retained include every probe command, stdout, stderr, exit code, timeout state, and parsed catalog.
- **ER-004**: GX10 actions are read-only only.
- **ER-005**: Dry-run expectation is satisfied by command preview through raw probe definitions and mock execution tests.

### Key Entities

- **System Tuning Probe**: A read-only command with purpose, family, parser, and timeout.
- **Tuning Catalog Entry**: Parsed current state for one tuning area with risk classification and future action hint.
- **System Tuning Catalog**: The complete structured output from one discovery run.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Mock discovery produces catalog, raw, and redaction artifacts.
- **SC-002**: All probes in the first release are classified read-only.
- **SC-003**: Optional failed probes are represented as unavailable entries.
- **SC-004**: Full pytest suite passes.

## Assumptions

- `nvidia-smi`, `/proc`, `/sys`, and shell builtins are enough for the first read-only tuning catalog.
- Persistent tuning and session-mutating experiments are explicitly out of scope.
- Existing SSH executor and redaction helpers are reused.
