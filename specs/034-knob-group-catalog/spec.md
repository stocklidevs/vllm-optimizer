# Feature Specification: Knob Group Catalog

**Feature Branch**: `034-knob-group-catalog`

**Created**: 2026-05-15

**Status**: Draft

**Input**: Project roadmap Phase 4: let users choose optimization knob families from the web interface. Start with a deterministic local catalog generated from existing safe sweep, risky sweep, session tuning, and discovery configuration files.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List Available Knob Groups (Priority: P1)

As a user, I want to see available knob families and their safety level so I can decide what category of optimization to run next.

**Why this priority**: The web UI needs a stable source for knob group selection.

**Independent Test**: Generate a catalog from repository configuration and verify it includes safe vLLM sweeps, concurrency/workload sweeps, risky session sweeps, session tuning sweeps, and read-only discovery.

**Acceptance Scenarios**:

1. **Given** repository configs, **When** catalog generation runs, **Then** the output lists knob groups with id, label, family, safety tier, config path, and allowed actions.
2. **Given** risky groups, **When** catalog generation runs, **Then** the output marks them as requiring explicit opt-in.

---

### User Story 2 - Render a Selector Preview (Priority: P2)

As a user, I want a static HTML selector preview so that the first web UI can show knob groups before live execution is wired in.

**Why this priority**: This continues the web interface path without adding a live server.

**Independent Test**: Generate HTML from the catalog and verify it shows group cards, safety labels, and command hints.

### Edge Cases

- Config directories are missing.
- No sweep configs exist.
- Unknown filenames should be classified conservatively.
- Risky and session-mutating groups must be visually distinct.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a machine-readable knob group catalog from existing local config files.
- **FR-002**: Each group MUST include id, label, family, safety tier, config path, command kind, and whether explicit opt-in is required.
- **FR-003**: Catalog generation MUST classify safe, risky-session, session-tuning, concurrency, workload, fp8, and read-only discovery groups.
- **FR-004**: System MUST optionally generate standalone HTML that previews selectable knob groups.
- **FR-005**: Catalog generation MUST perform no GX10 actions.
- **FR-006**: Catalog output MUST be deterministic when regenerated from unchanged config files.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST identify objective family or workload category when inferable from config name.
- **ER-002**: Feature MUST preserve config paths needed to run the selected group later.
- **ER-003**: Feature MUST classify remote side effects before execution.
- **ER-004**: Feature MUST support dry local preview.
- **ER-005**: Feature MUST keep persistent system tuning out of selectable run groups.

### Key Entities *(include if feature involves data)*

- **Knob Group**: Selectable optimization family or discovery action.
- **Safety Tier**: Read-only, safe-session, risky-session, or session-tuning classification.
- **Selector Preview**: Static HTML view of catalog options.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Catalog generation identifies at least five knob families from the current repository.
- **SC-002**: Risky or mutating groups are marked as requiring opt-in in 100% of tested cases.
- **SC-003**: The selector preview displays group label, safety tier, and config path for every catalog group.
- **SC-004**: Catalog generation requires no GX10 connection.

## Assumptions

- The first selector is a static preview and catalog contract, not an interactive run launcher.
- The future web UI will use the catalog to build controls and route selections to existing pipeline commands.
