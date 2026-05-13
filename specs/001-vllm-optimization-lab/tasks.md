# Tasks: vLLM Optimization Lab

**Input**: Design documents from `/specs/001-vllm-optimization-lab/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required for deterministic planning, dry-run safety, artifact
parsing, and ranking.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Python package, fixtures, and test structure.

- [x] T001 Create Python project metadata in pyproject.toml
- [x] T002 Create package skeleton in src/vllm_optimizer/
- [x] T003 Create test directory structure in tests/
- [x] T004 Add sample experiment fixture in tests/fixtures/experiments/throughput.json
- [x] T005 Add sample result fixture in tests/fixtures/results/throughput.jsonl

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared data loading, validation, artifact IO, and CLI plumbing.

- [x] T006 Implement shared dataclasses/types in src/vllm_optimizer/types.py
- [x] T007 Implement experiment loading and validation in src/vllm_optimizer/experiments.py
- [x] T008 Implement artifact read/write helpers in src/vllm_optimizer/artifacts.py
- [x] T009 Implement CLI command routing in src/vllm_optimizer/cli.py and src/vllm_optimizer/__main__.py
- [x] T010 [P] Add validation tests in tests/unit/test_experiments.py

**Checkpoint**: Foundation ready; user story implementation can begin.

---

## Phase 3: User Story 1 - Generate a Reproducible Experiment Plan (Priority: P1)

**Goal**: Generate identical ordered trial plans from identical experiment definitions.

**Independent Test**: Run planning twice for the same fixture and compare trial ids and ordering.

### Tests for User Story 1

- [x] T011 [P] [US1] Add deterministic planning tests in tests/unit/test_planner.py
- [x] T012 [P] [US1] Add CLI plan integration test in tests/integration/test_cli_plan.py

### Implementation for User Story 1

- [x] T013 [US1] Implement deterministic trial expansion in src/vllm_optimizer/planner.py
- [x] T014 [US1] Wire the plan command output in src/vllm_optimizer/cli.py

**Checkpoint**: User Story 1 can be demonstrated with `vllm-optimizer plan`.

---

## Phase 4: User Story 2 - Preview Safe Remote Actions (Priority: P2)

**Goal**: Produce a dry-run command preview without contacting the GX10.

**Independent Test**: Generate a preview from a trial plan and verify blocked actions are identified.

### Tests for User Story 2

- [x] T015 [P] [US2] Add safety allowlist tests in tests/unit/test_safety.py
- [x] T016 [P] [US2] Add CLI dry-run integration test in tests/integration/test_cli_dry_run.py

### Implementation for User Story 2

- [x] T017 [US2] Implement remote action rendering and allowlist checks in src/vllm_optimizer/safety.py
- [x] T018 [US2] Wire the dry-run command output in src/vllm_optimizer/cli.py

**Checkpoint**: User Story 2 can be demonstrated with `vllm-optimizer dry-run`.

---

## Phase 5: User Story 3 - Capture and Rank Benchmark Results (Priority: P3)

**Goal**: Rank fixture results for throughput and latency objectives with artifact traceability.

**Independent Test**: Rank fixture JSONL results and verify ordering, exclusions, and artifact references.

### Tests for User Story 3

- [x] T019 [P] [US3] Add ranking tests in tests/unit/test_ranking.py
- [x] T020 [P] [US3] Add CLI rank integration test in tests/integration/test_cli_rank.py

### Implementation for User Story 3

- [x] T021 [US3] Implement result parsing and scoring in src/vllm_optimizer/ranking.py
- [x] T022 [US3] Wire the rank command output in src/vllm_optimizer/cli.py

**Checkpoint**: User Story 3 can be demonstrated with `vllm-optimizer rank`.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation validation and complete local verification.

- [x] T023 Update README.md with MVP workflow and safety stance
- [x] T024 Run quickstart commands from specs/001-vllm-optimization-lab/quickstart.md
- [x] T025 Run full test suite with uv run pytest

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational.
- **User Story 2 (Phase 4)**: Depends on User Story 1 trial plan output.
- **User Story 3 (Phase 5)**: Depends on User Story 1 trial ids and Foundational artifact IO.
- **Polish (Phase 6)**: Depends on all desired user stories.

## Parallel Opportunities

- T010 can run while CLI skeleton work continues.
- T011 and T012 can be authored in parallel.
- T015 and T016 can be authored in parallel.
- T019 and T020 can be authored in parallel.

## Implementation Strategy

1. Complete Setup and Foundational tasks.
2. Deliver US1 as the MVP: deterministic local planning.
3. Add US2 dry-run safety preview.
4. Add US3 fixture-based ranking.
5. Validate the quickstart and test suite.
