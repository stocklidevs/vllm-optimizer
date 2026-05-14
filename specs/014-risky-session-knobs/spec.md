# Feature Specification: Risky Session Knobs

**Feature Branch**: `014-risky-session-knobs`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Explore higher-impact vLLM session knobs using risk tiers. Extend serve profile rendering and sweep planning to support explicitly approved risky-session flags such as block-size, kv-cache-dtype, and enforce-eager while continuing to block persistent/system flags. Risky-session sweep plans must be previewable, blocked by default, and require explicit operator opt-in before live execution. Anchor the sweep on the confirmed recommended Qwen profile, run a small live sweep, rank it, update version, and commit."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preview Risk-Tiered Knobs (Priority: P1)

As the operator, I want risky session knobs to appear in dry-run previews with clear risk labels so I can inspect them before any live run.

**Why this priority**: Higher-impact flags should be visible and auditable before they can affect a live vLLM session.

**Independent Test**: Generate a sweep plan and preview containing a risky-session flag and verify the preview is blocked by default with the changed parameters and command line visible.

**Acceptance Scenarios**:

1. **Given** a sweep definition with a risky-session flag, **When** preview is generated without opt-in, **Then** the preview is blocked and explains that risky-session flags require explicit permission.
2. **Given** a sweep definition with only safe flags, **When** preview is generated, **Then** existing behavior remains unblocked.

---

### User Story 2 - Run Explicitly Allowed Risky Session Sweep (Priority: P2)

As the operator, I want to run a small risky-session sweep only after explicit opt-in so we can test higher-impact settings without opening the door to persistent host changes.

**Why this priority**: This is the first step beyond safe knobs; it must still be controlled and reversible.

**Independent Test**: Run the live sweep command against a plan with risky-session flags and verify it refuses without the opt-in flag and proceeds with the opt-in flag.

**Acceptance Scenarios**:

1. **Given** a risky-session plan, **When** live sweep is requested without opt-in, **Then** the command exits without running trials.
2. **Given** a risky-session plan and explicit opt-in, **When** live sweep is requested, **Then** trials run sequentially through the existing managed benchmark lifecycle.

---

### User Story 3 - Keep Blocked Flags Blocked (Priority: P3)

As the operator, I want persistent/system flags to remain refused so high-impact exploration does not mutate host settings or storage behavior.

**Why this priority**: The GX10 is a real remote machine; exploration must not blur the safety boundary.

**Independent Test**: Attempt to include a blocked persistent/system flag and verify the sweep definition is rejected before planning.

**Acceptance Scenarios**:

1. **Given** a sweep definition containing a blocked flag, **When** it is loaded, **Then** validation fails with a clear message.
2. **Given** an unknown flag, **When** it is loaded, **Then** validation fails.

### Edge Cases

- A sweep mixes safe and risky-session flags.
- A risky flag value has the wrong type.
- A risky flag value is outside the allowed value set.
- A risky plan is generated with opt-in but live run is attempted without opt-in.
- A risky flag causes a trial failure; subsequent trials continue only when requested by existing sweep failure behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST classify sweep parameters as safe-session, risky-session, or blocked/unknown.
- **FR-002**: System MUST allow dry-run planning and preview for risky-session parameters.
- **FR-003**: System MUST block risky-session previews by default unless explicit risky-session preview allowance is recorded.
- **FR-004**: System MUST refuse live risky-session sweeps unless the live command includes explicit risky-session opt-in.
- **FR-005**: System MUST continue to reject blocked persistent/system and unknown parameters before plan generation.
- **FR-006**: System MUST render approved risky-session flags in the vLLM serve command only when present in the profile or sweep overrides.
- **FR-007**: System MUST include risk tier metadata in sweep plans and previews.
- **FR-008**: System MUST provide a checked-in small risky-session sweep anchored on the confirmed recommended Qwen profile.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST measure latency, throughput, failure rate, and balanced ranking.
- **ER-002**: Feature MUST record profile path, prompt set, risky parameters, risk allowance, and source artifacts.
- **ER-003**: Feature MUST retain sweep plan, preview, live results, and ranking artifacts.
- **ER-004**: Feature MUST classify planning/preview as local-only and live sweep as session-mutating.
- **ER-005**: Feature MUST require dry-run preview before live remote use.

### Key Entities *(include if feature involves data)*

- **Risky Knob Rule**: Parameter name, CLI flag, type, allowed values, and risk tier.
- **Risky Sweep Plan**: Sweep plan with per-parameter risk tiers and risky-session allowance state.
- **Risky Sweep Preview**: Dry-run preview indicating blocked/unblocked status and reasons.
- **Risky Sweep Result**: Live sequential sweep artifacts and ranked objective report.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Risky-session preview blocks without opt-in in 100% of tested risky plans.
- **SC-002**: Live risky-session sweep command refuses to run without opt-in in 100% of tested risky plans.
- **SC-003**: Blocked or unknown flags are rejected before plan output in 100% of tested cases.
- **SC-004**: A small risky-session live sweep produces ranking artifacts when explicitly allowed.
- **SC-005**: Existing safe sweep tests continue to pass unchanged.

## Assumptions

- Initial risky-session candidates are limited to `block-size` and `enforce-eager` around the confirmed recommended profile.
- `kv-cache-dtype` remains available for planning but is not included in the first live sweep unless explicitly added later.
- Risky-session flags are session-local vLLM serve flags, not persistent Linux or NVIDIA settings.
