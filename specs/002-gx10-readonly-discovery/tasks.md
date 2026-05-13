# Tasks: GX10 Read-Only Discovery

**Input**: Design documents from `/specs/002-gx10-readonly-discovery/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required for config validation, read-only safety, mock execution,
parsing, redaction, and CLI behavior.

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Add mock discovery config fixture in tests/fixtures/discovery/local.gx10.mock.json
- [x] T002 Add mock probe output fixture in tests/fixtures/discovery/mock_outputs.json
- [x] T003 Add discovery modules in src/vllm_optimizer/discovery.py, src/vllm_optimizer/redaction.py, and src/vllm_optimizer/ssh.py

---

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T004 Implement discovery config loading and validation in src/vllm_optimizer/discovery.py
- [x] T005 Implement fixed read-only probe catalog in src/vllm_optimizer/discovery.py
- [x] T006 Implement redaction helper in src/vllm_optimizer/redaction.py
- [x] T007 Implement mock executor interface in src/vllm_optimizer/ssh.py
- [x] T008 [P] Add config and probe safety tests in tests/unit/test_discovery.py
- [x] T009 [P] Add redaction tests in tests/unit/test_redaction.py

---

## Phase 3: User Story 1 - Verify GX10 Connectivity Safely (Priority: P1)

**Goal**: Run connectivity first and skip all remaining probes on connectivity failure.

**Independent Test**: Use mock success and failure fixtures without contacting the GX10.

- [x] T010 [P] [US1] Add connectivity flow tests in tests/unit/test_discovery_flow.py
- [x] T011 [US1] Implement connectivity-first discovery flow in src/vllm_optimizer/discovery.py

---

## Phase 4: User Story 2 - Collect Host and Accelerator Facts (Priority: P2)

**Goal**: Normalize host, OS, GPU, CUDA, Python, and vLLM facts from mock outputs.

**Independent Test**: Feed recorded mock outputs and verify normalized summary fields.

- [x] T012 [P] [US2] Add parser tests in tests/unit/test_discovery_parsing.py
- [x] T013 [US2] Implement normalized fact parsing in src/vllm_optimizer/discovery.py

---

## Phase 5: User Story 3 - Save Redacted Discovery Artifacts (Priority: P3)

**Goal**: Save redacted raw and normalized discovery artifacts.

**Independent Test**: Run CLI mock discovery and assert artifacts exist and contain no configured secrets.

- [x] T014 [P] [US3] Add CLI mock discovery integration test in tests/integration/test_cli_discover.py
- [x] T015 [US3] Wire discover CLI command in src/vllm_optimizer/cli.py
- [x] T016 [US3] Save raw, summary, and redaction report artifacts in src/vllm_optimizer/discovery.py

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T017 Update README.md with mock discovery workflow and live-connection boundary
- [x] T018 Run quickstart mock discovery command
- [x] T019 Run full test suite with uv run pytest
- [x] T020 Add batch-mode SSH executor for fixed read-only probes in src/vllm_optimizer/ssh.py
- [x] T021 Add SSH executor command construction test in tests/unit/test_ssh.py
- [x] T022 Run live read-only discovery against GX10 after key-based SSH is confirmed
- [x] T023 Add Qwen3 Coder Next serve profile in config/profiles/qwen3-coder-next-awq.json
- [x] T024 Add dry-run serve-plan renderer in src/vllm_optimizer/serve_profiles.py
- [x] T025 Add serve-plan tests in tests/unit/test_serve_profiles.py and tests/integration/test_cli_serve_plan.py

## Dependencies & Execution Order

- Setup and Foundational phases block all stories.
- US1 must complete before US2 and US3.
- US2 and US3 can proceed after US1.
- Polish depends on all stories.

## Implementation Strategy

1. Build config/probe/redaction/mock executor foundations.
2. Implement connectivity-first flow.
3. Implement parsers and artifact writing.
4. Wire CLI and validate with tests.
5. Stop before any real SSH connection.
