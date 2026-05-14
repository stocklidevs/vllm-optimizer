# Feature Specification: Benchmark Concurrency

**Feature Branch**: `017-benchmark-concurrency`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Add benchmark-side request concurrency controls so workload benchmarks can send prompt cases concurrently, record concurrency in plans/artifacts, and support concurrency-specific prompt sets for future sweeps."

## User Scenarios & Testing

### User Story 1 - Measure Concurrent Requests (Priority: P1)

As the optimizer operator, I want benchmark prompt sets to declare request concurrency, so I can measure vLLM behavior under simultaneous coding-assistant requests instead of only sequential prompts.

**Why this priority**: Serve-side knobs like sequence count and batched tokens matter most when requests overlap.

**Independent Test**: Load a concurrent prompt set, render a benchmark plan, and verify the plan and saved prompt artifacts include the configured concurrency.

**Acceptance Scenarios**:

1. **Given** a prompt set with concurrency `3`, **When** a benchmark plan is rendered, **Then** the plan records concurrency `3`.
2. **Given** concurrent request metrics, **When** the summary is generated, **Then** aggregate throughput uses the measured batch duration rather than the sum of overlapping request durations.

---

### User Story 2 - Promote A Workload-Specific Concurrent Profile (Priority: P2)

As the optimizer operator, I want a confirmed profile for concurrent interactive coding, so the optimizer can preserve a workload-specific recommendation without replacing the sequential default.

**Why this priority**: The best concurrent profile can differ from the best sequential profile.

**Independent Test**: Run a repeated A/B confirmation for the concurrent winner and write a separate concurrent recommended profile only when the report approves switching.

**Acceptance Scenarios**:

1. **Given** a concurrent sweep winner and a repeated A/B report that approves switching, **When** confirmed promotion runs, **Then** a concurrent recommended profile is written with confirmation provenance.

### Edge Cases

- A prompt set declares invalid concurrency such as `0`, `false`, or a non-integer.
- Concurrent requests finish in a different order than submitted.
- A candidate wins concurrent throughput but regresses sequential performance.

## Requirements

### Functional Requirements

- **FR-001**: Prompt sets MUST support an optional positive integer concurrency field that defaults to `1`.
- **FR-002**: Benchmark plans and saved prompt artifacts MUST record concurrency.
- **FR-003**: Concurrent benchmark execution MUST issue prompt cases with a bounded worker count.
- **FR-004**: Aggregate throughput MUST use batch duration when concurrent request duration is available.
- **FR-005**: The repository MUST include a concurrent interactive coding prompt set and a bounded concurrent sweep config.
- **FR-006**: The repository MUST include a confirmed concurrent recommended profile when repeated A/B confirmation approves it.

### Experiment Requirements

- **ER-001**: Objective family is concurrent latency, throughput, and balanced ranking for interactive coding.
- **ER-002**: Reproducibility inputs are prompt set id, concurrency, profile path, candidate list, benchmark summaries, and A/B report path.
- **ER-003**: Raw artifacts retained are sweep plans, previews, live rankings, benchmark summaries, A/B report, and promotion summary.
- **ER-004**: GX10 actions are session-mutating benchmark runs only.
- **ER-005**: Dry-run plan and preview must succeed before live concurrent sweep execution.

### Key Entities

- **Concurrent Prompt Set**: Prompt set with concurrency greater than one.
- **Batch Duration**: Wall-clock duration for a concurrent request batch.
- **Concurrent Recommended Profile**: Workload-specific profile confirmed for concurrent interactive coding.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Concurrent prompt sets validate through the benchmark loader.
- **SC-002**: Concurrent live A/B confirmation uses at least three successful repetitions per side.
- **SC-003**: Confirmed concurrent profile improves both mean latency and throughput by more than the 1% noise band.
- **SC-004**: The full automated test suite passes after concurrency support is added.

## Assumptions

- Concurrent prompt cases are independent and can be sent in parallel.
- Workload-specific concurrent promotion does not replace the global sequential default profile.
- The current confirmed default remains the control for concurrent A/B confirmation.
