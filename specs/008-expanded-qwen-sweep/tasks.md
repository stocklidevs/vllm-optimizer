# Tasks: Expanded Qwen Sweep

## Phase 1: Spec and Config

- [x] T001 Create SpecKit artifacts in specs/008-expanded-qwen-sweep
- [x] T002 Add expanded sweep config in config/sweeps/qwen-expanded-safe.json

## Phase 2: Tests and Docs

- [x] T003 Add expanded sweep plan tests in tests/unit/test_sweep.py
- [x] T004 Add expanded sweep CLI plan/preview integration test in tests/integration/test_cli_sweep.py
- [x] T005 Update README.md with expanded sweep commands

## Phase 3: Validation and Optional Live Run

- [x] T006 Run uv run pytest and fix regressions
- [x] T007 Generate expanded plan and preview locally
- [x] T008 Run live expanded sweep on GX10 when approved
- [x] T009 Generate expanded comparison report after live run
