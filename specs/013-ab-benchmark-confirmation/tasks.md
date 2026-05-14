# Tasks: A/B Benchmark Confirmation

**Input**: Design documents from `/specs/013-ab-benchmark-confirmation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required for aggregation, decision logic, malformed inputs, CLI behavior, and live quickstart validation.

## Phase 1: Setup

- [x] T001 Create A/B confirmation module in src/vllm_optimizer/ab_confirmation.py
- [x] T002 [P] Document CLI contract in specs/013-ab-benchmark-confirmation/contracts/cli.md

## Phase 2: Foundational

- [x] T003 Define AbConfirmationError and input dataclass in src/vllm_optimizer/ab_confirmation.py
- [x] T004 Implement summary loading and aggregate metrics in src/vllm_optimizer/ab_confirmation.py
- [x] T005 Implement keep/switch/inconclusive decision logic in src/vllm_optimizer/ab_confirmation.py

## Phase 3: User Story 1 - Define A/B Confirmation Plan (Priority: P1)

- [x] T006 [P] [US1] Add CLI help/argument integration coverage in tests/integration/test_cli_ab_confirmation.py
- [x] T007 [US1] Add ab-report CLI command in src/vllm_optimizer/cli.py

## Phase 4: User Story 2 - Aggregate Repeated A/B Results (Priority: P2)

- [x] T008 [P] [US2] Add aggregate unit tests in tests/unit/test_ab_confirmation.py
- [x] T009 [P] [US2] Add ab-report CLI write test in tests/integration/test_cli_ab_confirmation.py
- [x] T010 [US2] Implement build_ab_confirmation_report and Markdown rendering in src/vllm_optimizer/ab_confirmation.py

## Phase 5: User Story 3 - Decide Default Profile (Priority: P3)

- [x] T011 [P] [US3] Add keep/switch/inconclusive/failure decision tests in tests/unit/test_ab_confirmation.py
- [x] T012 [US3] Add missing/malformed summary tests in tests/unit/test_ab_confirmation.py
- [x] T013 [US3] Run three original and three recommended live benchmark repetitions through benchmark-run
- [x] T014 [US3] Generate live A/B confirmation report artifacts with ab-report

## Phase 6: Polish

- [x] T015 [P] Update README.md with A/B confirmation workflow
- [x] T016 Update version to next minor release in pyproject.toml, src/vllm_optimizer/__init__.py, README.md, and uv.lock
- [x] T017 Run uv run pytest and fix regressions
- [x] T018 Commit Spec 013 changes
