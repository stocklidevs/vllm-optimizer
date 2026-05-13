# Tasks: vLLM Flag Catalog

## Phase 1: Spec and Policy

- [x] T001 Create SpecKit artifacts in specs/009-vllm-flag-catalog
- [x] T002 Add Qwen safe policy in config/vllm-flags/qwen-safe-policy.json
- [x] T003 Add fixture help text in tests/fixtures/vllm/serve-help.txt

## Phase 2: Parser and Classifier

- [x] T004 Add parser/classifier tests in tests/unit/test_flag_catalog.py
- [x] T005 Implement parser and classifier in src/vllm_optimizer/flag_catalog.py

## Phase 3: CLI and Capture

- [x] T006 Add CLI tests in tests/integration/test_cli_flag_catalog.py
- [x] T007 Add flag-catalog and flag-catalog-capture commands in src/vllm_optimizer/cli.py
- [x] T008 Implement read-only capture artifact writing in src/vllm_optimizer/flag_catalog.py

## Phase 4: Validation and Live Read-Only Capture

- [x] T009 Update README.md with flag catalog commands
- [x] T010 Run uv run pytest and fix regressions
- [x] T011 Run approved read-only GX10 flag catalog capture
