# Feature Specification: A/B Benchmark Confirmation

**Feature Branch**: `013-ab-benchmark-confirmation`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Run repeated A/B benchmark confirmation for original and recommended Qwen profiles using the same prompt set. Aggregate per-profile repeated benchmark summaries, compute mean latency, mean throughput, spread, failure rate, and a keep-original/switch-to-recommended/inconclusive decision. The workflow must use the existing managed benchmark lifecycle for live runs, support local aggregation/reporting from existing benchmark artifacts, preserve provenance, and update version plus commit."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define A/B Confirmation Plan (Priority: P1)

As the operator, I want a clear A/B confirmation plan comparing the original and recommended profiles over repeated runs so the benchmark work is auditable before live execution.

**Why this priority**: The previous single-run comparison was inside the noise band; repeated confirmation needs explicit profiles, repetitions, prompt set, and artifact locations.

**Independent Test**: Generate or inspect the confirmation inputs and verify both profiles, prompt set, repetition count, and output locations are deterministic and local.

**Acceptance Scenarios**:

1. **Given** original and recommended profiles, **When** the operator prepares confirmation, **Then** both profiles and the shared prompt set are listed with the same repetition count.
2. **Given** a missing profile, **When** confirmation is requested, **Then** the workflow fails before live benchmark execution.

---

### User Story 2 - Aggregate Repeated A/B Results (Priority: P2)

As the operator, I want repeated benchmark summaries aggregated by profile so I can compare means, spreads, and failures instead of judging one noisy run.

**Why this priority**: Aggregation is the core value of the confirmation pass and separates real signal from ordinary run variance.

**Independent Test**: Provide fixture benchmark summary directories for both profiles and verify aggregate latency, throughput, spread, failure rate, and provenance.

**Acceptance Scenarios**:

1. **Given** three successful summaries for each profile, **When** the report is generated, **Then** it includes per-profile mean latency, mean throughput, spread metrics, and zero failure rate.
2. **Given** one failed repetition, **When** the report is generated, **Then** failure rate is included and the decision accounts for the failure.

---

### User Story 3 - Decide Default Profile (Priority: P3)

As the operator, I want a conservative keep/switch/inconclusive decision so I know whether the recommended profile should replace the original default.

**Why this priority**: The project needs a practical decision gate before moving on to broader knob exploration.

**Independent Test**: Feed aggregate fixtures where the recommended profile clearly wins, loses, or is within the noise band and verify the decision.

**Acceptance Scenarios**:

1. **Given** recommended has materially better latency and throughput with no higher failure rate, **When** the report is generated, **Then** decision is switch-to-recommended.
2. **Given** original is materially better or recommended has failures, **When** the report is generated, **Then** decision is keep-original.
3. **Given** differences are inside the noise band, **When** the report is generated, **Then** decision is inconclusive.

### Edge Cases

- Profile groups have different repetition counts.
- A summary is missing required numeric metrics.
- A repetition has failures but still has partial metrics.
- Recommended wins one metric but loses the other.
- Artifact directories exist from previous runs and must not be overwritten accidentally.
- GX10 is unavailable; aggregation from existing local artifacts must still work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST aggregate repeated benchmark summaries for original and recommended profiles.
- **FR-002**: System MUST compute success count, failure count, failure rate, mean latency, latency spread, mean throughput, and throughput spread per profile.
- **FR-003**: System MUST compare original and recommended aggregates and emit one decision: keep-original, switch-to-recommended, or inconclusive.
- **FR-004**: System MUST include profile ids, source summary paths, repetition counts, prompt set assumptions, and generation timestamp in the report.
- **FR-005**: System MUST fail clearly when required summaries are missing or malformed.
- **FR-006**: System MUST use only the existing benchmark-run lifecycle for live GX10 repetitions.
- **FR-007**: System MUST support local-only aggregation/report generation without contacting the GX10.
- **FR-008**: System MUST treat small metric differences inside a configured noise band as inconclusive.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST measure latency, throughput, failure rate, and stability spread.
- **ER-002**: Feature MUST record profile paths, prompt set, repetition count, source summary paths, and decision thresholds.
- **ER-003**: Feature MUST retain per-repetition benchmark artifacts plus aggregate JSON and Markdown reports.
- **ER-004**: Feature MUST classify aggregation/reporting as local-only and live repetitions as session-mutating through existing benchmark-run.
- **ER-005**: Feature MUST support local planning before live remote use.

### Key Entities *(include if feature involves data)*

- **A/B Confirmation Input**: Profile labels, summary paths, prompt set, repetition count, and threshold settings.
- **Profile Aggregate**: Per-profile mean/spread/failure metrics and source summaries.
- **A/B Decision Report**: JSON/Markdown comparison with decision, rationale, deltas, and provenance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Aggregation report generation completes in under 10 seconds for six benchmark summaries.
- **SC-002**: Report includes all required aggregate metrics for both profiles in 100% of valid cases.
- **SC-003**: Missing or malformed summaries are rejected before report output is written in 100% of tested failure cases.
- **SC-004**: Live confirmation writes three benchmark artifact sets per profile when all repetitions succeed.
- **SC-005**: The Markdown report states the default-profile decision without requiring raw JSON inspection.

## Assumptions

- Default confirmation uses three repetitions per profile.
- The same Qwen baseline prompt set is used for both profiles.
- The default noise band is one percent for latency and throughput comparisons.
- The next knob exploration starts after this confirmation report is committed.
