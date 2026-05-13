# Tasks: Qwen Parameter Sweep

**Input**: Design documents from `/specs/005-qwen-parameter-sweep/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required for deterministic search generation, command rendering,
artifact parsing, scoring, and remote safety gates.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the first bounded sweep fixture and module shell.

- [x] T001 Add sample sweep definition in config/sweeps/qwen-small-sweep.json
- [x] T002 Create sweep module shell in src/vllm_optimizer/sweep.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared validation, safe parameter metadata, and CLI surfaces.

- [x] T003 [P] Define safe sweep parameter allowlist and validation behavior in src/vllm_optimizer/sweep.py
- [x] T004 [P] Add CLI parser entries for sweep-plan, sweep-preview, sweep-rank, and sweep-run in src/vllm_optimizer/cli.py

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Generate a Deterministic Sweep Plan (Priority: P1) MVP

**Goal**: Generate repeatable safe trial plans from a sweep definition.

**Independent Test**: Generate the same sweep twice and verify trial ids, order, overrides, and artifact paths match.

### Tests for User Story 1

- [x] T005 [P] [US1] Add deterministic plan and validation tests in tests/unit/test_sweep.py
- [x] T006 [P] [US1] Add sweep-plan CLI integration test in tests/integration/test_cli_sweep.py

### Implementation for User Story 1

- [x] T007 [US1] Implement SweepDefinition loading and validation in src/vllm_optimizer/sweep.py
- [x] T008 [US1] Implement deterministic trial generation and profile override rendering in src/vllm_optimizer/sweep.py
- [x] T009 [US1] Implement sweep-plan CLI handler in src/vllm_optimizer/cli.py

**Checkpoint**: User Story 1 is locally functional without GX10 access.

---

## Phase 4: User Story 2 - Preview Trial Execution and Safety (Priority: P2)

**Goal**: Render a dry-run preview of all trials, artifacts, classifications, blocked reasons, and cleanup behavior.

**Independent Test**: Render a preview from a plan and verify it performs no SSH and reports all trials.

### Tests for User Story 2

- [x] T010 [P] [US2] Add sweep preview unit tests in tests/unit/test_sweep.py
- [x] T011 [P] [US2] Add sweep-preview CLI integration test in tests/integration/test_cli_sweep.py

### Implementation for User Story 2

- [x] T012 [US2] Implement sweep preview generation and blocked-plan reporting in src/vllm_optimizer/sweep.py
- [x] T013 [US2] Implement sweep-preview CLI handler in src/vllm_optimizer/cli.py

**Checkpoint**: User Stories 1 and 2 are independently testable without SSH.

---

## Phase 5: User Story 3 - Run and Rank a Small Sweep (Priority: P3)

**Goal**: Rank fixture or live sweep results, and provide a sequential live runner through existing benchmark lifecycle.

**Independent Test**: Rank fixture rows and verify failed trials are excluded with reasons and successful trials link to artifacts.

### Tests for User Story 3

- [x] T014 [P] [US3] Add sweep ranking and baseline delta tests in tests/unit/test_sweep.py
- [x] T015 [P] [US3] Add sweep-rank CLI integration test in tests/integration/test_cli_sweep.py

### Implementation for User Story 3

- [x] T016 [US3] Implement sweep result normalization and objective scoring in src/vllm_optimizer/sweep.py
- [x] T017 [US3] Implement sweep-rank CLI handler in src/vllm_optimizer/cli.py
- [x] T018 [US3] Implement sequential sweep-run orchestration through run_baseline_benchmark in src/vllm_optimizer/sweep.py
- [x] T019 [US3] Implement sweep-run CLI handler in src/vllm_optimizer/cli.py

**Checkpoint**: Ranking works locally; live run is available only through explicit GX10 config.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation.

- [x] T020 [P] Update README.md with sweep commands and safety notes
- [x] T021 [P] Update specs/005-qwen-parameter-sweep/quickstart.md if implementation details differ
- [x] T022 Run uv run pytest and fix regressions

---

## Dependencies & Execution Order

- Phase 1 before Phase 2.
- Phase 2 before all user stories.
- US1 before US2 because preview consumes the generated plan.
- US1 before US3 because ranking and live execution consume the generated plan.
- Polish after desired user stories.

## Parallel Opportunities

- T003 and T004 can be implemented in parallel.
- T005 and T006 can be written in parallel.
- T010 and T011 can be written in parallel.
- T014 and T015 can be written in parallel.
- T020 and T021 can be completed in parallel.

## Implementation Strategy

Deliver the MVP by completing US1 first, then add local preview, then local
ranking and live sequential orchestration. Validate with local tests before any
GX10 live sweep is attempted.
