# Feature Specification: Confirm C8 Saturation

**Feature Branch**: `022-confirm-c8-saturation`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Run repeated confirmation for the c8 concurrency saturation winner, promote it if confirmed, update version/documentation, and commit."

## User Scenarios & Testing

### User Story 1 - Confirm the C8 Winner (Priority: P1)

As the optimizer operator, I want repeated A/B evidence for the c8 saturation winner against the current concurrent recommendation, so a small throughput lead is not promoted from noise.

**Why this priority**: The c8 result was the best saturation point, but c4 and c6 were close enough that repeated confirmation is required before changing defaults.

**Independent Test**: Run repeated benchmarks for the current concurrent profile and the c8 candidate on the same concurrency-8 prompt set, then generate an A/B confirmation report.

**Acceptance Scenarios**:

1. **Given** the current concurrent profile and the c8 candidate profile, **When** both are benchmarked repeatedly, **Then** the confirmation report aggregates latency, throughput, spread, and failures.
2. **Given** the confirmation report, **When** it approves switching, **Then** the concurrent recommended profile is updated with confirmation provenance.
3. **Given** the confirmation report, **When** it does not approve switching, **Then** the current concurrent profile remains unchanged and the result is documented.

## Requirements

- **FR-001**: The system MUST generate a candidate profile from the c8 saturation ranking.
- **FR-002**: The live confirmation MUST run the current concurrent recommended profile and c8 candidate on the concurrency-8 prompt set.
- **FR-003**: The confirmation MUST use repeated A/B aggregation before promotion.
- **FR-004**: Promotion MUST only update `config/profiles/qwen3-coder-next-awq-concurrent-recommended.json` if the A/B report status is `switch-to-recommended`.
- **FR-005**: Documentation and version metadata MUST record the result.

## Success Criteria

- **SC-001**: Candidate and current profiles each have repeated live benchmark summaries.
- **SC-002**: `artifacts/reports/qwen-c8-concurrency-confirmation.json` and `.md` are generated.
- **SC-003**: The concurrent recommended profile is either confirmed unchanged or updated with provenance.
- **SC-004**: The full automated test suite passes.

## Assumptions

- Five repetitions per side are enough for this confirmation pass.
- The concurrency-8 prompt set is the correct pressure test for the c8 saturation winner.
- The existing A/B and confirmed-promotion gates are authoritative for promotion decisions.
