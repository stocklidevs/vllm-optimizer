# Feature Specification: Pipeline Control Manifest

**Feature Branch**: `035-pipeline-control-manifest`

**Created**: 2026-05-15

**Status**: Draft

**Input**: Project roadmap Phase 5: expose deterministic pipeline control through the future web UI. Start with a local control manifest generated from a selected knob group.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate UI Control Steps (Priority: P1)

As a future web UI, I need a command manifest for a selected knob group so I can display plan, preview, run, report, confirm, and promotion controls with correct safety gates.

**Why this priority**: The UI should orchestrate existing deterministic commands instead of hardcoding workflow knowledge.

**Independent Test**: Given a knob group catalog and group id, generate a control manifest and verify stage names, command hints, required gates, and promotion status.

**Acceptance Scenarios**:

1. **Given** a safe sweep group, **When** a manifest is generated, **Then** it includes plan, preview, run, report, confirm, and optional promotion stages.
2. **Given** a risky group, **When** a manifest is generated, **Then** run stages include the required explicit opt-in gate.

### Edge Cases

- Selected group id does not exist.
- Selected group is read-only discovery rather than a pipeline sweep.
- Selected group is session tuning and uses session tuning commands instead of `optimize-workload`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a machine-readable control manifest for a selected knob group.
- **FR-002**: Manifest MUST include ordered stages, command hints, remote-action markers, required gates, and artifact paths.
- **FR-003**: Manifest MUST mark promotion as disabled unless explicit promotion gate is selected later.
- **FR-004**: Manifest MUST support safe sweep, risky sweep, session tuning sweep, and read-only discovery groups.
- **FR-005**: Manifest generation MUST perform no GX10 actions.
- **FR-006**: Manifest generation MUST be deterministic from unchanged inputs.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST preserve selected objective/knob family context from the group catalog.
- **ER-002**: Feature MUST identify remote and mutating stages before execution.
- **ER-003**: Feature MUST preserve config paths and output paths needed to execute later.
- **ER-004**: Feature MUST keep promotion explicitly gated.
- **ER-005**: Feature MUST support dry local preview.

### Key Entities *(include if feature involves data)*

- **Control Manifest**: UI-readable plan for a selected knob group.
- **Control Stage**: Ordered action with command hint, artifact target, gate, and remote flag.
- **Safety Gate**: Required explicit option before risky, session tuning, or promotion actions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Manifest generation produces at least four actionable stages for sweep groups.
- **SC-002**: Risky/session groups include opt-in gates in 100% of tested cases.
- **SC-003**: Read-only discovery groups do not include run/promotion stages.
- **SC-004**: Manifest generation requires no GX10 connection.

## Assumptions

- This phase generates a control contract, not a running web service.
- Future UI will execute or queue these stages through approved backend orchestration.
