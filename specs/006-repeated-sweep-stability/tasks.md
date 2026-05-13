# Tasks: Repeated Sweep Stability

**Input**: Design documents from `/specs/006-repeated-sweep-stability/`

## Phase 1: Setup

- [x] T001 Add narrowed repeated sweep config in config/sweeps/qwen-top2-repeated.json

## Phase 2: Repeated Planning

- [x] T002 [P] Add repeated plan tests in tests/unit/test_sweep.py
- [x] T003 Implement repetitions, candidate ids, and repeated trial ids in src/vllm_optimizer/sweep.py

## Phase 3: Aggregate Ranking

- [x] T004 [P] Add aggregate ranking tests in tests/unit/test_sweep.py
- [x] T005 Implement candidate aggregation and stability-aware ranking in src/vllm_optimizer/sweep.py
- [x] T006 Add CLI integration coverage for repeated ranking in tests/integration/test_cli_sweep.py

## Phase 4: Documentation and Validation

- [x] T007 Update README.md with repeated sweep workflow
- [x] T008 Run uv run pytest and fix regressions
- [x] T009 Run narrowed live repeated sweep on GX10

## Dependencies

- T001 before T002-T003.
- T003 before T004-T006.
- T008 before T009.
