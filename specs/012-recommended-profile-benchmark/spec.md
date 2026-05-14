# Feature Specification: Recommended Profile Benchmark

**Feature Branch**: `012-recommended-profile-benchmark`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Benchmark the promoted recommended profile as a standalone candidate, compare it against the original baseline and source sweep winner, and generate a refresh report that says whether the promoted profile should remain the default starting point. The workflow should be deterministic, use existing benchmark prompts, produce local plan/report artifacts, support a live GX10 benchmark run only through the existing benchmark safety path, and require no new remote mutation beyond the managed vLLM benchmark lifecycle."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Plan Recommended Profile Benchmark (Priority: P1)

As the operator, I want a deterministic benchmark plan for the promoted recommended profile so I can verify what will run before touching the GX10.

**Why this priority**: The recommended profile is only trustworthy if it can be benchmarked through the same visible, reproducible path as previous baseline runs.

**Independent Test**: Can be tested by generating a benchmark plan for the recommended profile and verifying it uses the existing prompt corpus, promoted profile id, and local artifact destination without starting vLLM.

**Acceptance Scenarios**:

1. **Given** the recommended profile exists, **When** the operator creates a benchmark plan, **Then** the plan identifies the promoted profile, prompt set, request sequence, and expected metrics.
2. **Given** the recommended profile is invalid or missing, **When** the operator requests the plan, **Then** the workflow fails before any live remote action.

---

### User Story 2 - Compare Recommended Benchmark Evidence (Priority: P2)

As the operator, I want a report comparing the recommended profile benchmark against the original baseline and the source scheduler winner so I can decide whether the promoted profile remains the default.

**Why this priority**: Promotion happened from sweep evidence; a standalone benchmark report confirms whether the profile holds up outside that sweep context.

**Independent Test**: Can be tested using fixture summaries and ranking artifacts to produce a report that includes recommendation status, metric deltas, and source provenance.

**Acceptance Scenarios**:

1. **Given** original baseline, recommended benchmark summary, and promotion provenance, **When** the report is generated, **Then** it shows latency and throughput deltas and a default-profile recommendation.
2. **Given** the recommended benchmark underperforms the original baseline, **When** the report is generated, **Then** the report says the profile should not be promoted as the default without more evidence.

---

### User Story 3 - Run Live Recommended Benchmark Safely (Priority: P3)

As the operator, I want to run the recommended profile benchmark on the GX10 only through the existing managed benchmark lifecycle so the host remains safe and cleanup is preserved.

**Why this priority**: The live benchmark gives the strongest signal, but it must not introduce a new remote execution path.

**Independent Test**: Can be tested by verifying the command uses the existing benchmark runner, produces artifacts under the recommended-profile benchmark destination, and records cleanup artifacts.

**Acceptance Scenarios**:

1. **Given** GX10 SSH configuration is available, **When** the operator runs the recommended benchmark, **Then** it uses the existing benchmark lifecycle and writes summary, metrics, responses, server log, and cleanup artifacts.
2. **Given** the live run fails, **When** artifacts are inspected, **Then** failure status and cleanup evidence are retained.

### Edge Cases

- Recommended profile exists but lacks promotion provenance.
- Recommended benchmark summary is missing or has failed prompts.
- Original baseline summary is missing.
- Source scheduler ranking is missing or does not contain the promoted candidate.
- Recommended profile benchmark performs within noise of baseline, requiring a neutral recommendation.
- GX10 is unavailable; local planning and report generation from existing artifacts should remain usable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a deterministic plan for benchmarking the recommended profile using the existing prompt set.
- **FR-002**: System MUST produce a comparison report from original baseline summary, recommended benchmark summary, promoted profile provenance, and optional source ranking artifact.
- **FR-003**: System MUST report latency and throughput deltas between the recommended benchmark and original baseline.
- **FR-004**: System MUST report whether the recommended profile should remain the default starting point, based on successful completion and metric deltas.
- **FR-005**: System MUST include promotion provenance, profile id, candidate id, and source sweep id in the report when available.
- **FR-006**: System MUST classify live benchmark execution as session-mutating and use the existing managed benchmark lifecycle only.
- **FR-007**: System MUST support report generation without connecting to the GX10 when required artifacts already exist.
- **FR-008**: System MUST fail clearly when required report inputs are missing or malformed.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST measure the recommended profile for throughput, latency, and balanced default suitability.
- **ER-002**: Feature MUST use the recommended profile, prompt set, original baseline summary, recommended benchmark summary, and promotion provenance as reproducibility inputs.
- **ER-003**: Feature MUST retain benchmark plan, live benchmark artifacts, comparison JSON, and Markdown summary.
- **ER-004**: Feature MUST identify planning/reporting as local-only and live benchmarking as session-mutating through the existing runner.
- **ER-005**: Feature MUST define dry-run benchmark-plan expectations before live remote use.

### Key Entities *(include if feature involves data)*

- **Recommended Benchmark Plan**: Local benchmark plan for the promoted profile and prompt set.
- **Recommended Benchmark Result**: Summary and artifacts from running the promoted profile benchmark.
- **Default Decision Report**: Comparison artifact with deltas, provenance, and default-profile recommendation.
- **Default Decision**: Outcome indicating keep, reject, or inconclusive for using the recommended profile as the default starting point.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The recommended profile benchmark plan is generated in under 10 seconds without contacting the GX10.
- **SC-002**: The comparison report includes latency and throughput deltas for 100% of valid baseline/recommended summary pairs.
- **SC-003**: Missing or malformed required inputs are rejected before report output is written in 100% of tested failure cases.
- **SC-004**: A live recommended benchmark writes the same core artifact classes as the existing baseline benchmark runner.
- **SC-005**: The report recommendation can be understood from the Markdown summary without opening raw JSON artifacts.

## Assumptions

- The promoted recommended profile from Spec 011 is the candidate under validation.
- The existing Qwen baseline prompt set remains the benchmark workload.
- The default decision threshold is conservative: keep the recommended profile when it completes successfully and is not worse than baseline on both latency and throughput.
- Live benchmarking may be skipped when the GX10 is unavailable; local report generation can use existing artifacts.
