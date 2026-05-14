# Feature Specification: Optimization Pipeline MVP

**Feature Branch**: `023-optimization-pipeline-mvp`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Create the first optimization pipeline orchestrator so the manual plan, preview, run, rank, and report loop becomes repeatable without automatic promotion."

## User Scenarios & Testing

### User Story 1 - Create a Pipeline Plan (Priority: P1)

As the optimizer operator, I want one command to generate a deterministic pipeline plan from a sweep config, so I can see every artifact path and intended stage before running work.

**Why this priority**: The manual workflow is proven, but the artifact naming and command sequence are still hand assembled.

**Independent Test**: Generate a pipeline plan from an existing sweep config and verify it records stage names, input paths, output paths, and safety notes.

**Acceptance Scenarios**:

1. **Given** a valid sweep config and output directory, **When** the pipeline is run in plan mode, **Then** it writes a pipeline plan without running remote work.
2. **Given** a plan, **When** the operator inspects it, **Then** the plan identifies where sweep plan, preview, live, ranking, and report artifacts will live.

---

### User Story 2 - Generate Preview Artifacts (Priority: P2)

As the optimizer operator, I want the pipeline command to generate the sweep plan and safety preview together, so I can approve live work from one predictable artifact directory.

**Why this priority**: Preview is the critical safety gate before remote mutation.

**Independent Test**: Run the pipeline in preview mode and verify it writes pipeline, sweep plan, and sweep preview artifacts.

**Acceptance Scenarios**:

1. **Given** a valid sweep config, **When** preview mode runs, **Then** the sweep plan and preview are generated under the pipeline output directory.
2. **Given** a risky-session sweep, **When** risky flags are not allowed, **Then** preview records the blocked state and does not run live work.

---

### User Story 3 - Run and Report Explicitly (Priority: P3)

As the optimizer operator, I want explicit run and report stages, so live execution and recommendation generation are repeatable but still separated from promotion.

**Why this priority**: Running the GX10 should remain an explicit operator choice.

**Independent Test**: Run the pipeline in report mode against fixture result rows and verify ranking/report artifacts are produced without promotion.

**Acceptance Scenarios**:

1. **Given** approved preview artifacts, **When** run mode is selected, **Then** live sweep execution writes results and ranking artifacts.
2. **Given** ranking artifacts, **When** report mode is selected, **Then** a local recommendation report is generated.
3. **Given** any mode, **When** it completes, **Then** the pipeline summary records completed stages and generated artifacts.

### Edge Cases

- Output directory already contains a prior pipeline run.
- Sweep contains risky-session flags but the operator has not allowed them.
- Report mode is requested before ranking artifacts exist.
- Live run has failed candidates but produces at least one rankable result.

## Requirements

- **FR-001**: The system MUST provide an `optimize-workload` command with `plan`, `preview`, `run`, and `report` modes.
- **FR-002**: The command MUST accept a sweep config, output directory, and optional remote config for live run mode.
- **FR-003**: Plan mode MUST write a pipeline plan and perform no remote actions.
- **FR-004**: Preview mode MUST write the pipeline plan, sweep plan, and sweep preview.
- **FR-005**: Run mode MUST require a remote config and explicit risky-session allowance when the sweep plan contains risky flags.
- **FR-006**: Report mode MUST generate ranking and comparison report artifacts from available pipeline outputs.
- **FR-007**: The pipeline MUST NOT promote profiles automatically.
- **FR-008**: Documentation MUST explain the MVP pipeline boundaries and examples.

## Success Criteria

- **SC-001**: Operators can generate plan and preview artifacts for an existing sweep with one command.
- **SC-002**: The full pipeline artifact directory has predictable paths for plan, preview, live results, ranking, and report.
- **SC-003**: Live execution remains blocked unless explicitly selected with required inputs.
- **SC-004**: Automated tests cover plan, preview, report, and safety error behavior.
- **SC-005**: The full automated test suite passes.

## Assumptions

- This MVP orchestrates a single sweep at a time.
- Automatic search strategy generation and automatic profile promotion are out of scope.
- Existing sweep, ranking, benchmark, and report modules remain the source of truth for their stages.
