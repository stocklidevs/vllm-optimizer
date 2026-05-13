# Feature Specification: Expanded Qwen Sweep

**Feature Branch**: `008-expanded-qwen-sweep`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add an expanded but safe repeated Qwen sweep around the current 0.90/32768 winner. The sweep should test gpu_memory_utilization values 0.88, 0.90, and 0.92 at max_model_len 32768, compare performance_mode interactivity versus throughput, use three repetitions per candidate, preserve the same prompt set and baseline summary, produce dry-run previews and rankings through the existing local report pipeline, and remain session-level only with no Linux/NVIDIA persistent tuning or broad concurrent load testing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Plan the Expanded Sweep (Priority: P1)

As the operator, I want a deterministic expanded sweep around the current Qwen
winner so I can test whether nearby safe settings outperform 0.90/32768.

**Why this priority**: The current best result came from a tiny search space;
the next measurement should check nearby values without increasing remote risk.

**Independent Test**: Can be tested locally by generating the expanded sweep
plan twice and verifying identical candidate ids, trial ids, and repetition
counts.

**Acceptance Scenarios**:

1. **Given** the expanded sweep definition, **When** a plan is generated,
   **Then** it contains exactly six candidates and eighteen repeated trials.
2. **Given** repeated plan generation from the same definition, **When** the
   outputs are compared, **Then** candidate and trial ordering is identical.

---

### User Story 2 - Preview Safety Before Live Execution (Priority: P2)

As the operator, I want the expanded sweep preview to list all candidate
settings, repetitions, commands, artifacts, and cleanup behavior before the GX10
is touched.

**Why this priority**: Eighteen sequential runs are a larger session mutation
than prior sweeps, so the execution shape must be reviewable first.

**Independent Test**: Can be tested without SSH by rendering a preview and
verifying all actions are session-mutating only.

**Acceptance Scenarios**:

1. **Given** the expanded sweep plan, **When** the preview is generated,
   **Then** it reports no blocked actions and no remote execution.
2. **Given** any persistent or unsupported parameter, **When** preview or plan
   validation runs, **Then** the sweep is blocked before live use.

---

### User Story 3 - Compare Expanded Results With Existing Reports (Priority: P3)

As the operator, I want the expanded sweep results to feed the existing ranking
and report pipeline so the new winner, baseline deltas, and stability trade-offs
are easy to inspect.

**Why this priority**: The value of the expanded sweep is the decision it
supports, not merely the raw artifacts.

**Independent Test**: Can be tested by ranking fixture repeated results and
generating a comparison report without GX10 access.

**Acceptance Scenarios**:

1. **Given** completed expanded sweep results, **When** ranking is generated,
   **Then** each candidate has aggregate metrics, spread, failure rate, and
   artifact links.
2. **Given** an expanded ranking report, **When** the comparison report is
   generated, **Then** it names the current recommendation and explains
   stability trade-offs.

### Edge Cases

- `performance_mode=throughput` is unsupported by the remote vLLM version.
- A higher GPU memory utilization setting starts but becomes unstable.
- One repetition times out while others complete.
- The expanded sweep takes too long for a single session.
- The best throughput and best balanced objective disagree.
- Existing report artifacts are missing when the expanded report is generated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an expanded Qwen sweep definition with six
  candidates: three GPU memory utilization values crossed with two performance
  modes at max model length 32768.
- **FR-002**: System MUST use three repetitions per candidate.
- **FR-003**: System MUST preserve the existing Qwen prompt set and baseline
  summary reference.
- **FR-004**: System MUST generate deterministic plans and previews through the
  existing sweep commands.
- **FR-005**: System MUST support ranking completed expanded results through
  the existing repeated sweep ranking behavior.
- **FR-006**: System MUST support report generation from expanded rankings
  through the existing report command.
- **FR-007**: System MUST keep all GX10 actions session-mutating only.
- **FR-008**: System MUST NOT install packages, alter persistent Linux/NVIDIA
  settings, or run concurrent load tests.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Objective family is expanded repeated Qwen session-level vLLM
  parameter optimization.
- **ER-002**: Reproducibility inputs MUST include the expanded sweep definition,
  prompt set, baseline summary reference, candidate values, repetitions, and
  artifact paths.
- **ER-003**: Raw artifacts MUST include plan, preview, per-repetition benchmark
  artifacts, results JSONL, ranking JSON, and comparison report outputs.
- **ER-004**: GX10 actions remain session-mutating only during live execution.
- **ER-005**: Dry-run preview MUST be generated before live execution.

### Key Entities *(include if feature involves data)*

- **Expanded Sweep Definition**: The fixed safe candidate grid for Qwen.
- **Expanded Candidate**: One combination of GPU memory utilization,
  performance mode, and max model length.
- **Repeated Trial**: One sequential execution of a candidate repetition.
- **Expanded Ranking**: Aggregate candidate ranking for throughput, latency,
  and balanced objectives.
- **Expanded Comparison Report**: Human-readable and machine-readable summary
  comparing expanded results with prior baseline context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Expanded sweep plan generation produces six candidates and
  eighteen trials in 100% of local tests.
- **SC-002**: Expanded preview performs zero SSH commands and reports zero
  blocked actions for the shipped config.
- **SC-003**: All expanded candidates use only session-level safe parameters.
- **SC-004**: Fixture or live expanded results can be ranked and reported
  through existing commands.
- **SC-005**: If live execution is approved, the run writes per-repetition
  artifacts and a ranking report for all completed candidates.

## Assumptions

- The current winner `0.90 / 32768` is the center of the expanded search.
- `max_model_len=32768` remains fixed to keep the first expanded sweep bounded.
- Three repetitions per candidate are enough for this iteration.
- `performance_mode=throughput` is safe to attempt as a session-level vLLM
  serve option and should be treated as a candidate setting, not a host tuning.
