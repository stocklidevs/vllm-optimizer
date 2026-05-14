# Feature Specification: Concurrency Saturation

**Feature Branch**: `020-concurrency-saturation`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Create the next optimization spec to map concurrent interactive saturation around the current winner, generate sweep configs and reports, keep FP8 classifier cleanup, update version/documentation, and commit."

## User Scenarios & Testing

### User Story 1 - See Saturation by Concurrency (Priority: P1)

As the optimizer operator, I want one report that groups concurrent workload rankings by concurrency level, so I can see where throughput gains flatten or instability begins.

**Why this priority**: The largest measured improvement came from concurrent interactive serving, but one concurrency point does not define the safe operating envelope.

**Independent Test**: Build a report from multiple labeled ranking artifacts and verify the report identifies the best candidate at each concurrency level and the best overall safe concurrency point.

**Acceptance Scenarios**:

1. **Given** ranking artifacts labeled with concurrency values, **When** the saturation report is generated, **Then** each level includes winner metrics, overrides, and failure rate.
2. **Given** multiple concurrency levels, **When** a report is generated, **Then** the best overall level prefers higher throughput while rejecting failed or unstable candidates.

---

### User Story 2 - Plan Saturation Sweeps (Priority: P2)

As the optimizer operator, I want deterministic sweep configs and prompt sets for the concurrency ladder, so live GX10 runs can be launched without hand-editing parameters.

**Why this priority**: Saturation testing needs repeated, comparable prompt pressure at multiple concurrency levels.

**Independent Test**: Generate sweep plans and previews for the configured concurrency levels and verify expected candidate and trial counts.

**Acceptance Scenarios**:

1. **Given** saturation sweep configs, **When** plans are generated, **Then** each concurrency level uses the intended prompt concurrency and candidate matrix.
2. **Given** previews, **When** inspected before live execution, **Then** all actions are session-scoped and have explicit artifact destinations.

---

### User Story 3 - Classify Unsupported FP8 Dtype (Priority: P3)

As the optimizer operator, I want FP8 dtype incompatibilities called out accurately, so setup work is not confused with unsupported model/runtime combinations.

**Why this priority**: The FP8 rerun fixed the missing `ninja` path issue for plain FP8 but exposed a separate `fp8_e5m2` incompatibility.

**Independent Test**: Provide failed trial logs containing the vLLM `fp8_e5m2` rejection and verify the workload report emits the specific unsupported-dtype finding.

**Acceptance Scenarios**:

1. **Given** logs that say `fp8_e5m2 kv-cache is not supported with fp8 checkpoints`, **When** failure findings are generated, **Then** the finding names unsupported dtype rather than missing `ninja` or generic benchmark failure.

### Edge Cases

- A concurrency level has no successful candidates.
- Multiple levels have nearly equal throughput but different latency or failure rates.
- Ranking labels are malformed or duplicate a concurrency value.
- Old high-impact ranking artifacts still contain historical missing-`ninja` failures.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST provide a saturation report command that accepts one or more `CONCURRENCY=ranking.json` inputs.
- **FR-002**: The report MUST include per-concurrency winners with latency, throughput, failure rate, and overrides.
- **FR-003**: The report MUST identify a recommended concurrency level using throughput first, then failure rate, latency, and lower concurrency as tie breakers.
- **FR-004**: The report MUST output JSON and optionally Markdown.
- **FR-005**: The project MUST include deterministic prompt sets and sweep configs for the selected concurrency ladder.
- **FR-006**: Workload failure classification MUST identify unsupported `fp8_e5m2` KV cache failures separately from missing-`ninja` failures.
- **FR-007**: Documentation MUST show how to generate plans, previews, live runs, and the saturation report.

### Experiment Requirements

- **ER-001**: Objective family is concurrent interactive throughput with latency and failure-rate constraints.
- **ER-002**: Reproducibility inputs are prompt sets, sweep configs, plans, previews, ranking artifacts, and report version.
- **ER-003**: Raw artifacts retained are per-level plans, previews, results, rankings, and saturation reports.
- **ER-004**: GX10 actions are session-mutating vLLM serve trials only.
- **ER-005**: Persistent Linux/NVIDIA/system changes are out of scope.

### Key Entities

- **Concurrency Level**: A prompt-set concurrency value and its associated sweep ranking.
- **Saturation Winner**: The top balanced candidate for a concurrency level.
- **Saturation Recommendation**: Overall recommended concurrency and configuration for the workload.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A saturation report can summarize at least three concurrency levels in one JSON and Markdown artifact.
- **SC-002**: The report identifies the best overall concurrency using deterministic tie breakers.
- **SC-003**: Sweep plans for the concurrency ladder generate expected trial counts before live execution.
- **SC-004**: `fp8_e5m2` incompatibility is classified with a specific actionable message.
- **SC-005**: The full automated test suite passes after implementation.

## Assumptions

- The first saturation ladder will use interactive coding prompts at concurrency levels 1, 2, 3, 4, 6, and 8.
- The initial candidate matrix stays near the known concurrent winner to limit GX10 runtime.
- Live saturation execution may be run level by level; local planning/reporting is the primary implementation deliverable for this spec.
