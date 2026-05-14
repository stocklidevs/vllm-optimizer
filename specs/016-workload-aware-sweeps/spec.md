# Feature Specification: Workload-Aware Sweeps

**Feature Branch**: `016-workload-aware-sweeps`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Add workload-aware prompt sets and high-impact sweep definitions around the confirmed Qwen recommended profile so future live runs can compare short interactive coding, long coding, and tool/JSON workloads."

## User Scenarios & Testing

### User Story 1 - Benchmark Distinct Workloads (Priority: P1)

As the optimizer operator, I want separate prompt sets for interactive coding, long coding, and tool/JSON behavior, so performance tuning is measured against realistic workload shapes instead of one tiny baseline.

**Why this priority**: Different workloads can prefer different vLLM settings; the optimizer needs to reveal those differences before choosing another default.

**Independent Test**: Load each prompt set and verify it has a stable id, three deterministic cases, and workload-specific token budgets.

**Acceptance Scenarios**:

1. **Given** the workload prompt files, **When** they are loaded, **Then** each prompt set validates and exposes a distinct prompt set id.
2. **Given** the long coding prompt set, **When** a benchmark plan is rendered, **Then** the request sequence uses larger generation budgets than the interactive set.

---

### User Story 2 - Sweep Intentional High-Impact Candidates (Priority: P2)

As the optimizer operator, I want explicit candidate lists for high-impact knobs, so a sweep can test meaningful parameter combinations without a large cartesian explosion.

**Why this priority**: High-impact knobs interact strongly. Explicit candidates make the search bounded, auditable, and faster to run live.

**Independent Test**: Build sweep plans for all workload configs and verify candidate counts, risk metadata, prompt set ids, and preview safety status.

**Acceptance Scenarios**:

1. **Given** a high-impact workload sweep config, **When** a plan is generated, **Then** the plan uses explicit candidates and deterministic candidate ids.
2. **Given** a candidate with risky-session flags, **When** preview is rendered with config-level opt-in, **Then** the preview is not blocked and still records risky-session risk tiers.

### Edge Cases

- An explicit candidate includes a blocked persistent/system parameter.
- A workload prompt file is malformed or empty.
- A high-impact candidate uses a value outside the approved safe/risky-session bounds.
- A live run may fail for a risky candidate such as FP8 KV cache; the sweep runner should continue only when explicitly asked.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST support explicit sweep candidates in addition to cartesian parameter grids.
- **FR-002**: Explicit candidates MUST use the same parameter validation and risk classification as cartesian sweeps.
- **FR-003**: The repository MUST include prompt sets for short interactive coding, long coding, and tool/JSON workloads.
- **FR-004**: The repository MUST include high-impact sweep configs for each workload using the confirmed recommended profile as the baseline profile.
- **FR-005**: High-impact sweep configs MUST cover at least block size, batch token budget, sequence count, performance mode, GPU utilization, and KV cache dtype candidates.
- **FR-006**: Documentation MUST show how to generate dry-run plans/previews before running live workload sweeps.

### Experiment Requirements

- **ER-001**: Objective family is latency, throughput, and balanced ranking per workload.
- **ER-002**: Reproducibility inputs are prompt set id, profile path, explicit candidate list, seed, repetitions, vLLM model identity, and git version.
- **ER-003**: Raw artifacts retained are sweep plans, previews, results JSONL, rankings, and per-trial benchmark artifacts.
- **ER-004**: GX10 actions are session-mutating benchmark runs only; no persistent Linux/NVIDIA tuning is included.
- **ER-005**: Dry-run expectations require successful local `sweep-plan` and `sweep-preview` before any live `sweep-run`.

### Key Entities

- **Workload Prompt Set**: Deterministic benchmark cases for a specific workload shape.
- **Explicit Sweep Candidate**: A named set of parameter overrides validated independently before planning.
- **Workload Sweep Plan**: Dry-run plan binding one workload prompt set to a bounded candidate list.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Three workload prompt sets validate through the benchmark loader.
- **SC-002**: Three high-impact sweep configs produce unblocked dry-run previews with explicit candidate metadata.
- **SC-003**: Blocked parameters inside explicit candidates are refused before plan generation.
- **SC-004**: The full automated test suite passes after adding workload-aware sweeps.

## Assumptions

- The confirmed `qwen3-coder-next-awq-recommended` profile is the starting baseline for new high-impact sweeps.
- High-impact live runs will be launched intentionally after reviewing dry-run previews.
- FP8 KV cache candidates are risky-session probes and may be rejected by the remote vLLM install at runtime without invalidating the local plan.
