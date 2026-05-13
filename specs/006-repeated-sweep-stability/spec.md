# Feature Specification: Repeated Sweep Stability

**Feature Branch**: `006-repeated-sweep-stability`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add repeated sweep stability analysis for Qwen parameter sweeps. The system should allow a sweep definition to request multiple repetitions per candidate, generate deterministic repeated trial plans, execute repetitions sequentially through the existing safe lifecycle, aggregate per-candidate mean latency, throughput, spread, failure rate, and baseline deltas, rank candidates with stability-aware tie breakers, and support a narrowed live sweep comparing the baseline-ish 0.90/32768 candidate against the current 0.86/32768 winner. It must not add persistent Linux/NVIDIA tuning or concurrent load testing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Plan Repeated Candidates (Priority: P1)

As the operator, I want each candidate in a sweep to run a fixed number of
deterministic repetitions so a small apparent win can be checked against
run-to-run variation.

**Why this priority**: The first sweep found a small winner, and repeated
measurements are needed before treating it as meaningful.

**Independent Test**: Can be tested locally by generating a plan twice and
verifying each candidate has the same repeated trial identifiers, repetition
indexes, and artifact paths.

**Acceptance Scenarios**:

1. **Given** a sweep definition with two candidates and three repetitions,
   **When** the operator generates a plan twice, **Then** both plans contain
   the same candidate ids and repeated trial ids in the same order.
2. **Given** a repetition count below one, **When** the operator generates a
   plan, **Then** the system rejects it with a clear validation error.

---

### User Story 2 - Aggregate Stability Metrics (Priority: P2)

As the operator, I want completed repeated trial results aggregated by
candidate so I can compare mean performance, spread, failures, and baseline
deltas.

**Why this priority**: Ranking a single sample is fragile; aggregate reports
make optimizer decisions auditable.

**Independent Test**: Can be tested with fixture repeated results and a
baseline summary without contacting the GX10.

**Acceptance Scenarios**:

1. **Given** repeated result rows for each candidate, **When** aggregation is
   requested, **Then** the report includes mean latency, mean throughput,
   spread, repetition count, failure rate, and baseline deltas.
2. **Given** a candidate with a failed repetition, **When** aggregation is
   requested, **Then** the candidate remains visible with failure rate and only
   successful repetitions contributing to mean metrics.

---

### User Story 3 - Rank With Stability Tie-Breakers (Priority: P3)

As the operator, I want throughput, latency, and balanced rankings to account
for repeated-run stability so recommendations do not overfit to noisy samples.

**Why this priority**: The project should call out when a winner is stable,
not merely fastest once.

**Independent Test**: Can be tested with fixture candidates where the fastest
mean has worse spread or failures than a close competitor.

**Acceptance Scenarios**:

1. **Given** aggregate candidate metrics, **When** ranking is generated, **Then**
   each objective includes rank, score, mean metrics, spread, failure rate,
   baseline delta, and source repetitions.
2. **Given** two candidates with near-identical primary metrics, **When**
   ranking is generated, **Then** lower failure rate and lower spread act as
   deterministic tie-breakers.

### Edge Cases

- A candidate has zero successful repetitions.
- A repetition is interrupted after vLLM starts.
- Results are missing repetition indexes or candidate ids.
- The baseline summary is missing or from an earlier run.
- Two candidates have equal mean and equal spread.
- A repeated live run leaves port 8001 occupied between repetitions.
- Logs include host, user, token, model path, or cache path values.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support a positive repetition count in sweep
  definitions.
- **FR-002**: System MUST generate deterministic candidate ids and repeated
  trial ids for the same definition.
- **FR-003**: System MUST execute repetitions sequentially through the existing
  safe benchmark lifecycle.
- **FR-004**: System MUST aggregate successful repetitions by candidate and
  preserve failed repetitions in the report.
- **FR-005**: System MUST compute candidate mean latency, mean throughput,
  latency spread, throughput spread, success count, failure count, and failure
  rate.
- **FR-006**: System MUST compute baseline deltas when a baseline summary is
  available.
- **FR-007**: System MUST rank candidates for throughput, latency, and balanced
  objectives using stability-aware tie-breakers.
- **FR-008**: System MUST link aggregate rows back to all source repetition
  artifacts.
- **FR-009**: System MUST provide a narrowed sample sweep comparing the
  baseline-ish 0.90/32768 candidate with the current 0.86/32768 winner.
- **FR-010**: System MUST NOT add persistent Linux/NVIDIA tuning, package
  installation, or concurrent load testing.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Objective family is repeated-run stability analysis for Qwen
  session-level vLLM parameter optimization.
- **ER-002**: Reproducibility inputs MUST include repetition count, candidate
  ids, repeated trial ids, seed, parameter overrides, prompt set, baseline
  summary reference, and artifact paths.
- **ER-003**: Raw artifacts MUST include every repetition's benchmark artifacts,
  repeated result manifest, aggregate candidate report, ranking report, and
  cleanup evidence.
- **ER-004**: GX10 actions remain session-mutating only and require dry-run
  preview before live use.
- **ER-005**: Persistent-mutating actions remain blocked.

### Key Entities *(include if feature involves data)*

- **Repeated Sweep Definition**: Sweep definition with repetition count and
  candidate parameter space.
- **Candidate**: One unique parameter combination with deterministic id.
- **Repeated Trial**: One execution attempt for a candidate and repetition
  index.
- **Candidate Aggregate**: Stability summary across all repetitions for one
  candidate.
- **Stability Ranking**: Objective-specific recommendation report using mean
  metrics, spread, failure rate, and baseline deltas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Re-running the same repeated sweep definition produces identical
  candidate ids and repeated trial ids in 100% of deterministic tests.
- **SC-002**: Fixture aggregation reports success count, failure count, failure
  rate, mean metrics, and spread for 100% of candidates.
- **SC-003**: Fixture ranking links 100% of ranked candidates back to source
  repetition artifacts.
- **SC-004**: A candidate with failed repetitions remains visible in aggregate
  output with a nonzero failure rate.
- **SC-005**: The narrowed live repeated sweep compares exactly the 0.90/32768
  and 0.86/32768 candidates and writes aggregate ranking artifacts.

## Assumptions

- Three repetitions per candidate are sufficient for the first stability check.
- Sequential execution remains the safest default for repeated live runs.
- The existing baseline summary is acceptable for initial deltas.
- More rigorous statistical testing can be added after repeated aggregate data
  exists.
