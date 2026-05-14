# Feature Specification: Pipeline Confirmation Stage

**Feature Branch**: `024-pipeline-confirmation-stage`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Add an explicit pipeline confirmation stage that can generate a candidate profile, aggregate repeated A/B evidence, and optionally promote only when explicitly allowed and confirmed."

## User Scenarios & Testing

### User Story 1 - Confirm a Pipeline Winner (Priority: P1)

As the optimizer operator, I want `optimize-workload` to run a confirmation stage for a ranked winner, so the manual proof step becomes repeatable and auditable.

**Why this priority**: The project now has a pipeline MVP, but candidate confirmation and promotion still require several hand-assembled commands.

**Independent Test**: Run confirmation mode against an existing ranking and repeated summary artifacts, then verify candidate profile and A/B report artifacts are generated.

**Acceptance Scenarios**:

1. **Given** a pipeline ranking and repeated current/candidate summaries, **When** confirm mode runs, **Then** it writes a candidate profile and A/B confirmation report.
2. **Given** no promotion allowance, **When** confirm mode approves switching, **Then** it still does not update the confirmed profile output.

---

### User Story 2 - Promote Only With Explicit Approval (Priority: P2)

As the optimizer operator, I want profile promotion to require an explicit promotion flag, so the pipeline cannot silently change defaults.

**Why this priority**: Remote optimization is powerful, but default profile changes must stay intentional.

**Independent Test**: Run confirmation mode with `allow_promotion=true` and a `switch-to-recommended` report, then verify the confirmed profile output is written with confirmation provenance.

**Acceptance Scenarios**:

1. **Given** a confirmation report whose decision is `switch-to-recommended`, **When** promotion is allowed, **Then** the confirmed profile output is updated.
2. **Given** a confirmation report whose decision is not `switch-to-recommended`, **When** promotion is allowed, **Then** promotion fails safely and the existing profile is not overwritten.

### Edge Cases

- Confirmation mode is requested before ranking exists.
- Repeated summary counts are lower than the requested repetition count.
- Candidate profile path already exists.
- Promotion is requested without a confirmed profile output path.

## Requirements

- **FR-001**: `optimize-workload` MUST support `confirm` mode.
- **FR-002**: Confirm mode MUST require current profile, prompt set, candidate profile output, and confirmation labels.
- **FR-003**: Confirm mode MUST generate a candidate profile from the pipeline ranking.
- **FR-004**: Confirm mode MUST aggregate repeated current and candidate summaries into an A/B confirmation report.
- **FR-005**: Confirm mode MUST NOT update a confirmed profile unless `--allow-promotion` is provided.
- **FR-006**: Confirm mode MUST only promote when the A/B decision is `switch-to-recommended`.
- **FR-007**: Pipeline artifacts MUST record confirmation and promotion outputs in the summary.

## Success Criteria

- **SC-001**: Confirmation mode can generate candidate profile and A/B report from repeated summary artifacts.
- **SC-002**: Promotion remains blocked by default.
- **SC-003**: Explicit promotion writes confirmation provenance only after a positive A/B decision.
- **SC-004**: Automated tests cover confirm mode, promotion gating, and CLI arguments.
- **SC-005**: The full automated test suite passes.

## Assumptions

- The MVP confirmation stage operates on one ranked sweep winner.
- Live benchmark execution for missing confirmation summaries may be added later; this spec focuses on orchestrating existing repeated summary artifacts and promotion gates.
- Existing A/B and promotion modules remain authoritative for decision and profile generation.
