# Tasks: Run Comparison Report

## Phase 1: Spec and Module Setup

- [x] T001 Create SpecKit artifacts in specs/007-run-comparison-report
- [x] T002 Create report module in src/vllm_optimizer/report.py

## Phase 2: Reporting Logic

- [x] T003 [P] Add report unit tests in tests/unit/test_report.py
- [x] T004 Implement artifact parsing and candidate normalization in src/vllm_optimizer/report.py
- [x] T005 Implement recommendation and stability note generation in src/vllm_optimizer/report.py
- [x] T006 Implement Markdown rendering in src/vllm_optimizer/report.py

## Phase 3: CLI and Docs

- [x] T007 [P] Add report CLI integration tests in tests/integration/test_cli_report.py
- [x] T008 Add report command to src/vllm_optimizer/cli.py
- [x] T009 Update README.md with report command

## Phase 4: Validation

- [x] T010 Run uv run pytest and fix regressions
