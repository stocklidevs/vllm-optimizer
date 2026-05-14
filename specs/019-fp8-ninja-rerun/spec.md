# Feature Specification: FP8 Ninja Rerun

**Feature Branch**: `019-fp8-ninja-rerun`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Fix the FP8/ninja blocker, rerun FP8 KV cache probes for interactive, long, and tool/JSON workloads, refresh the workload leaderboard, update version/documentation, and commit."

## User Scenarios & Testing

### User Story 1 - Rerun FP8 Without Manual PATH Setup (Priority: P1)

As the optimizer operator, I want remote benchmark scripts to expose the selected vLLM executable directory on `PATH`, so subprocesses launched by vLLM can find helper binaries installed in the same virtual environment.

**Why this priority**: The GX10 has `ninja` installed in the Qwen venv but not on the system path.

**Independent Test**: Build a remote benchmark script from a profile whose executable lives in `$HOME/qwen3next-venv/bin/vllm` and verify it prepends that `bin` directory to `PATH`.

**Acceptance Scenarios**:

1. **Given** a vLLM executable with a directory component, **When** a benchmark script is rendered, **Then** the executable directory is exported on `PATH` before launching vLLM.
2. **Given** a pathless vLLM executable, **When** a benchmark script is rendered, **Then** no synthetic `PATH` export is added.

---

### User Story 2 - Capture FP8 Workload Evidence (Priority: P2)

As the optimizer operator, I want FP8 rerun sweep artifacts for each workload, so I can decide whether FP8 KV cache is worth pursuing after the dependency blocker is fixed.

**Why this priority**: FP8 is a risky-session knob and needs workload-specific live evidence.

**Independent Test**: Generate FP8-only sweep plans/previews and run them with explicit risky-session opt-in.

**Acceptance Scenarios**:

1. **Given** the FP8 rerun sweep configs, **When** plans and previews are generated, **Then** all candidates require risky-session opt-in.
2. **Given** live GX10 runs, **When** the workload leaderboard is refreshed, **Then** the report includes FP8 rerun labels and failed dtype findings.

### Edge Cases

- `ninja` exists in the venv but not on system `PATH`.
- `fp8_e5m2` is rejected by vLLM for FP8 checkpoints.
- A risky candidate fails while other candidates in the sweep succeed.

## Requirements

### Functional Requirements

- **FR-001**: The benchmark script renderer MUST prepend the vLLM executable directory to `PATH` when the executable includes a directory.
- **FR-002**: FP8 rerun sweep configs MUST be explicit risky-session sweeps.
- **FR-003**: The live rerun MUST include interactive, long, and tool/JSON workloads.
- **FR-004**: The refreshed workload leaderboard MUST include FP8 rerun ranking artifacts.
- **FR-005**: Documentation MUST record the live rerun outcome and the `fp8_e5m2` incompatibility.

### Experiment Requirements

- **ER-001**: Objective family is workload-specific balanced ranking with throughput and latency also retained.
- **ER-002**: Reproducibility inputs are sweep configs, plans, previews, ranking artifacts, and profile paths.
- **ER-003**: Raw artifacts retained are plans, previews, live result JSONL, ranking JSON, and refreshed report outputs.
- **ER-004**: GX10 actions are session-mutating vLLM serve trials only.
- **ER-005**: Risky-session flags require explicit preview/run opt-in.

### Key Entities

- **FP8 Rerun Sweep**: Workload-specific risky-session sweep focused on KV cache dtype.
- **PATH Export**: Script prelude that exposes the vLLM venv binary directory to child processes.
- **FP8 Workload Finding**: Outcome summary for `fp8` and `fp8_e5m2` candidates.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Unit tests cover vLLM executable directory `PATH` export behavior.
- **SC-002**: FP8 rerun sweep config tests verify risky-session gating.
- **SC-003**: Plain `fp8` completes successfully for interactive, long, and tool/JSON workloads.
- **SC-004**: The refreshed workload leaderboard includes FP8 rerun evidence.
- **SC-005**: The full automated test suite passes after implementation.

## Assumptions

- The selected vLLM executable path points at the same virtual environment that contains `ninja`.
- Plain `fp8` remains the compatible FP8 KV cache dtype for the current AWQ/FP8 checkpoint.
- `fp8_e5m2` failures are useful evidence and should remain captured rather than hidden.
