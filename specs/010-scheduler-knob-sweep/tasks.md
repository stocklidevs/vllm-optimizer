# Tasks: Scheduler Knob Sweep

## Phase 1: Spec and Optional Flag Rendering

- [x] T001 Create SpecKit artifacts in specs/010-scheduler-knob-sweep
- [x] T002 Add optional serve flag validation/rendering in src/vllm_optimizer/serve_profiles.py
- [x] T003 Add optional flag render/reject tests in tests/unit/test_serve_profiles.py

## Phase 2: Sweep Support

- [x] T004 Extend sweep safe parameters to approved optional flags in src/vllm_optimizer/sweep.py
- [x] T005 Add scheduler sweep config in config/sweeps/qwen-scheduler-safe.json
- [x] T006 Add scheduler sweep plan tests in tests/unit/test_sweep.py
- [x] T007 Add scheduler sweep CLI preview tests in tests/integration/test_cli_sweep.py

## Phase 3: Docs and Validation

- [x] T008 Update README.md with scheduler sweep commands
- [x] T009 Run uv run pytest and fix regressions
- [x] T010 Generate scheduler plan and preview locally
