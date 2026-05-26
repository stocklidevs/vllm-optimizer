# Feature Specification: Cockpit Risky-Session Gate Alignment

**Status**: Completed

**Created**: 2026-05-26

**Input**: User reported that the active cockpit still failed for the default C8 optimization, and the persisted failure record showed `risky-session sweep requires --allow-risky-session-flags`.

## User Scenarios & Testing

### User Story 1 - Default cockpit run honors selected sweep safety (Priority: P1)

As a cockpit user, I want the one-command launcher to honor the selected sweep's declared risky-session allowance, so the default C8 optimization can start without failing before any trial runs.

**Why this priority**: The default cockpit recipe is the high-throughput C8 sweep. If the launcher prepares that recipe but starts the server without its required safety allowance, the primary workflow is broken.

**Independent Test**: Prepare the default cockpit launch and verify the active server config has risky-session allowance enabled because the selected C8 sweep explicitly declares it.

**Acceptance Scenarios**:

1. **Given** the default C8 sweep declares risky-session allowance, **When** the cockpit launcher prepares the server, **Then** the server receives effective risky-session allowance.
2. **Given** a safe-session sweep override does not declare risky-session allowance, **When** the cockpit launcher prepares the server, **Then** the server remains on the stricter default.
3. **Given** the optimizer pipeline writes a pipeline plan for the C8 sweep, **When** the plan is inspected, **Then** its safety metadata reflects the effective sweep-level allowance.

### User Story 2 - Failure recovery names the missing gate (Priority: P1)

As a cockpit user, I want this failure mode to say exactly which gate is missing, so I can restart correctly instead of seeing a generic unexpected-error message.

**Independent Test**: Force a controller failure with `risky-session sweep requires --allow-risky-session-flags` and verify diagnostics and plain summary mention the missing gate.

**Acceptance Scenarios**:

1. **Given** a controller job fails because the risky-session gate is missing, **When** the cockpit displays failure detail, **Then** the likely cause mentions risky-session knobs and `--allow-risky-session-flags`.
2. **Given** the failure is persisted, **When** the user reloads, **Then** the same actionable next steps remain available from the failure record.

## Requirements

- **FR-001**: `cockpit-launch` MUST compute effective risky-session allowance from the explicit CLI flag or the selected sweep definition.
- **FR-002**: Safe-session sweep overrides MUST NOT gain risky-session allowance unless the sweep definition or CLI flag explicitly enables it.
- **FR-003**: Pipeline safety metadata MUST reflect effective risky-session allowance when the selected sweep declares it.
- **FR-004**: Existing sweep plans MUST be rebuilt when their stored risky-session allowance no longer matches the effective allowance for the selected sweep.
- **FR-005**: Cockpit failure diagnostics MUST classify missing risky-session gate failures with a specific likely cause and next steps.
- **FR-006**: Version metadata, README, changelog, SpecKit pointers, tests, and release checks MUST be updated.

## Success Criteria

- **SC-001**: The default launcher no longer starts the C8 cockpit with `allow_risky_session_flags=false`.
- **SC-002**: A missing risky-session gate failure tells the user which launch flag or launcher path fixes it.
- **SC-003**: Focused regression tests, full tests, release check, and local cockpit validation pass.

## Assumptions

- Sweep-local `allow_risky_session_flags: true` is treated as an explicit curated recipe-level opt-in.
- Promotion remains a separate explicit gate and is not changed by this feature.
