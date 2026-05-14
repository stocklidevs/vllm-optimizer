# Feature Specification: Full Pipeline Orchestration

**Feature Branch**: `025-full-pipeline-orchestration`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Move the optimizer pipeline from staged commands to an end-to-end run that can continue through confirmation until the best config emerges."

## User Scenarios & Testing

### User Story 1 - Run One End-to-End Workload Pipeline (Priority: P1)

As an operator, I want one command to run a workload sweep, rank it, generate a candidate profile, benchmark current vs candidate repeatedly, and write a final confirmation report so I can see whether a best config emerged without manually arranging each stage.

**Why this priority**: This is the missing bridge between the current staged MVP and the intended release workflow.

**Independent Test**: Run the pipeline in full mode with mocked benchmark execution and verify the stage order, generated candidate profile, repeated confirmation artifact paths, A/B report, and promotion gate.

**Acceptance Scenarios**:

1. **Given** a sweep, remote config, current profile, and prompt set, **When** full mode is run, **Then** the pipeline completes plan, preview, run, report, confirmation benchmark, and confirm stages in order.
2. **Given** the A/B report recommends the candidate, **When** full mode is run without promotion approval, **Then** the final summary reports the recommendation but does not write the confirmed profile.
3. **Given** the A/B report recommends the candidate and promotion is approved, **When** full mode is run, **Then** the confirmed profile is written with confirmation provenance.

---

### User Story 2 - Preserve Operator Safety (Priority: P2)

As an operator, I want full mode to keep the same explicit safety gates as the staged workflow so remote session mutations and profile promotion remain visible and reversible.

**Why this priority**: The pipeline starts and stops vLLM repeatedly over SSH, so it must remain explicit about live remote requirements and promotion.

**Independent Test**: Run full mode without a remote config or required confirmation inputs and verify the command fails before live work.

**Acceptance Scenarios**:

1. **Given** no remote config, **When** full mode is requested, **Then** the pipeline fails with a clear remote-config requirement.
2. **Given** no current profile or prompt set, **When** full mode is requested, **Then** the pipeline fails before running confirmation benchmarks.

---

### Edge Cases

- If the sweep produces no ranking, full mode fails before confirmation benchmarks.
- If a confirmation benchmark repetition fails, its summary is still retained and the A/B decision accounts for the failure rate.
- If confirmation summaries already exist, full mode overwrites them deterministically for the requested run.
- If the confirmation decision is inconclusive or keep-original, promotion is not written even when promotion approval is supplied.

## Requirements

### Functional Requirements

- **FR-001**: System MUST add an end-to-end pipeline mode for `optimize-workload`.
- **FR-002**: System MUST run sweep, report, candidate profile generation, repeated current benchmark, repeated candidate benchmark, A/B confirmation, and optional promotion in one command.
- **FR-003**: System MUST require a remote config for full mode because it performs live GX10 vLLM sessions.
- **FR-004**: System MUST require current profile, prompt set, candidate profile output, and confirmed profile output inputs for full mode.
- **FR-005**: System MUST write current confirmation repetitions under `<out>/confirmation/current-rN/`.
- **FR-006**: System MUST write candidate confirmation repetitions under `<out>/confirmation/candidate-rN/`.
- **FR-007**: System MUST keep promotion disabled unless `--allow-promotion` is explicitly provided.
- **FR-008**: System MUST include full mode stage completion and promotion decision details in `pipeline-summary.json`.

### Experiment Requirements

- **ER-001**: Objective family is balanced throughput and latency for one workload prompt set.
- **ER-002**: Reproducibility inputs include sweep definition, current profile, generated candidate profile, prompt set, remote config label, repetition count, stage artifacts, and git-managed version.
- **ER-003**: Raw artifacts retained include sweep live outputs, ranking, comparison report, benchmark plans, metrics, responses, logs, summaries, A/B report, and candidate or confirmed profile outputs.
- **ER-004**: GX10 actions are session-mutating vLLM lifecycle and benchmark commands; no persistent Linux/NVIDIA tuning is included.
- **ER-005**: Dry-run expectations remain available through existing plan and preview modes before full mode is used.

### Key Entities

- **Full Pipeline Run**: One workload optimization execution with ordered stage names, artifact paths, and promotion decision.
- **Confirmation Benchmark Repetition**: One benchmark run for current or candidate profile with retained plan, metrics, logs, and summary.
- **Candidate Profile**: A generated serve profile derived from the top ranked sweep candidate.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A full mode run records every completed stage in deterministic order.
- **SC-002**: A full mode run creates exactly N current and N candidate confirmation summary paths for N requested repetitions.
- **SC-003**: A full mode run can report `switch-to-recommended` without writing a confirmed profile unless promotion approval is present.
- **SC-004**: The full test suite passes after implementation.

## Assumptions

- Full mode optimizes one sweep and one prompt set per invocation.
- Confirmation benchmarks use the existing baseline benchmark runner rather than introducing a new benchmark engine.
- Candidate profile generation continues to use the top balanced objective winner from the sweep ranking.
- Persistent system tuning remains out of scope.
