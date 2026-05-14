# Tasks: Recommended Profile Benchmark

**Input**: Design documents from `/specs/012-recommended-profile-benchmark/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required for report artifact parsing, decision scoring, CLI behavior,
and benchmark-plan validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish local report module and CLI contract.

- [x] T001 Create default decision report module in src/vllm_optimizer/default_report.py
- [x] T002 [P] Add CLI contract docs in specs/012-recommended-profile-benchmark/contracts/cli.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared summary/provenance parsing and decision helpers.

- [x] T003 Define DefaultReportError and input dataclass in src/vllm_optimizer/default_report.py
- [x] T004 Implement metric delta calculations in src/vllm_optimizer/default_report.py
- [x] T005 Implement keep/reject/inconclusive decision helper in src/vllm_optimizer/default_report.py

---

## Phase 3: User Story 1 - Plan Recommended Profile Benchmark (Priority: P1) MVP

**Goal**: Generate a local benchmark plan for the recommended profile through existing benchmark-plan.

**Independent Test**: Run benchmark-plan against config/profiles/qwen3-coder-next-awq-recommended.json and verify profile id, prompt set, and metrics.

### Tests for User Story 1

- [x] T006 [P] [US1] Add recommended profile benchmark-plan integration test in tests/integration/test_cli_default_report.py

### Implementation for User Story 1

- [x] T007 [US1] Validate recommended profile works with existing benchmark-plan command

---

## Phase 4: User Story 2 - Compare Recommended Benchmark Evidence (Priority: P2)

**Goal**: Produce JSON and Markdown default decision reports from local artifacts.

**Independent Test**: Run report generation against fixture summaries/profile and verify deltas, decision, and provenance.

### Tests for User Story 2

- [x] T008 [P] [US2] Add unit tests for default decision report in tests/unit/test_default_report.py
- [x] T009 [P] [US2] Add recommended-report CLI integration test in tests/integration/test_cli_default_report.py

### Implementation for User Story 2

- [x] T010 [US2] Implement build_default_decision_report and Markdown rendering in src/vllm_optimizer/default_report.py
- [x] T011 [US2] Add recommended-report CLI command in src/vllm_optimizer/cli.py

---

## Phase 5: User Story 3 - Run Live Recommended Benchmark Safely (Priority: P3)

**Goal**: Use existing benchmark-run with the recommended profile and retain artifacts.

**Independent Test**: Execute benchmark-run with the recommended profile when GX10 is available, then generate the default decision report.

### Tests for User Story 3

- [x] T012 [P] [US3] Add missing/malformed input tests in tests/unit/test_default_report.py

### Implementation for User Story 3

- [x] T013 [US3] Run quickstart benchmark-plan locally
- [x] T014 [US3] Run live recommended benchmark with existing benchmark-run
- [x] T015 [US3] Generate recommended default report artifacts from live benchmark

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, versioning, and full regression testing.

- [x] T016 [P] Update README.md with recommended benchmark/report workflow
- [x] T017 Update version to next minor release in pyproject.toml, src/vllm_optimizer/__init__.py, README.md, and uv.lock
- [x] T018 Run uv run pytest and fix regressions
- [x] T019 Commit Spec 012 changes

---

## Dependencies & Execution Order

- Phase 1 before all other work.
- Phase 2 blocks report implementation.
- User Story 1 can validate existing benchmark-plan independently after setup.
- User Story 2 depends on Phase 2.
- User Story 3 depends on User Story 1 and User Story 2.
- Polish depends on all selected user stories.

## Implementation Strategy

1. Keep benchmark execution on the existing runner.
2. Add only local report generation logic.
3. Validate locally with fixture tests and quickstart commands.
4. Run live recommended benchmark if GX10 is reachable.
5. Update version and commit.
