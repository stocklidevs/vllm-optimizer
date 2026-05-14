# Tasks: Promote Winner Profile

**Input**: Design documents from `/specs/011-promote-winner-profile/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required for artifact parsing, deterministic candidate selection,
profile rendering, overwrite safety, and CLI behavior.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish promotion module and fixture paths.

- [x] T001 Create promotion module skeleton in src/vllm_optimizer/promotion.py
- [x] T002 [P] Add promotion CLI contract docs in specs/011-promote-winner-profile/contracts/cli.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared selection and profile-construction logic used by all user stories.

- [x] T003 Define PromotionError, request defaults, and ranking validation helpers in src/vllm_optimizer/promotion.py
- [x] T004 Add deterministic candidate selection from objective rankings in src/vllm_optimizer/promotion.py
- [x] T005 Add profile reconstruction from selected ranking candidate in src/vllm_optimizer/promotion.py

---

## Phase 3: User Story 1 - Preview Recommended Candidate (Priority: P1) MVP

**Goal**: Preview one promotion candidate from a ranking artifact without writing a profile.

**Independent Test**: Run promotion preview against a fixture/live ranking artifact and verify selected candidate, metrics, source trials, proposed profile, and provenance are present.

### Tests for User Story 1

- [x] T006 [P] [US1] Add unit tests for deterministic preview selection in tests/unit/test_promotion.py
- [x] T007 [P] [US1] Add CLI preview integration test in tests/integration/test_cli_promotion.py

### Implementation for User Story 1

- [x] T008 [US1] Implement build_promotion_preview in src/vllm_optimizer/promotion.py
- [x] T009 [US1] Add promote-preview CLI command in src/vllm_optimizer/cli.py

**Checkpoint**: Preview works independently and writes no recommended profile.

---

## Phase 4: User Story 2 - Generate Recommended Profile (Priority: P2)

**Goal**: Generate a reusable recommended profile and Markdown summary from the selected candidate.

**Independent Test**: Run promotion generation against a ranking fixture and verify profile settings, optional flags, embedded provenance, summary content, and overwrite behavior.

### Tests for User Story 2

- [x] T010 [P] [US2] Add unit tests for profile and Markdown generation in tests/unit/test_promotion.py
- [x] T011 [P] [US2] Add CLI profile generation integration test in tests/integration/test_cli_promotion.py

### Implementation for User Story 2

- [x] T012 [US2] Implement write_promoted_profile and render_promotion_summary in src/vllm_optimizer/promotion.py
- [x] T013 [US2] Add promote-profile CLI command with --force overwrite guard in src/vllm_optimizer/cli.py
- [x] T014 [US2] Generate checked-in recommended Qwen profile in config/profiles/qwen3-coder-next-awq-recommended.json

**Checkpoint**: Preview and profile generation both work independently.

---

## Phase 5: User Story 3 - Reject Unsafe or Incomplete Promotion (Priority: P3)

**Goal**: Refuse failed, missing, or ambiguous ranking data before writing outputs.

**Independent Test**: Provide malformed or incomplete ranking artifacts and verify commands fail with no output profile.

### Tests for User Story 3

- [x] T015 [P] [US3] Add invalid objective/candidate/failure unit tests in tests/unit/test_promotion.py
- [x] T016 [P] [US3] Add CLI no-overwrite and no-partial-write integration tests in tests/integration/test_cli_promotion.py

### Implementation for User Story 3

- [x] T017 [US3] Harden promotion validation and no-partial-write behavior in src/vllm_optimizer/promotion.py
- [x] T018 [US3] Ensure CLI maps PromotionError to exit code 2 in src/vllm_optimizer/cli.py

**Checkpoint**: Unsafe promotions fail closed.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, quickstart validation, and full regression testing.

- [x] T019 [P] Update README.md with promotion commands and recommended profile usage
- [x] T020 Run quickstart promotion preview/profile commands locally
- [x] T021 Run uv run pytest and fix regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational.
- **User Story 2 (Phase 4)**: Depends on User Story 1 selection/preview logic.
- **User Story 3 (Phase 5)**: Depends on User Story 1 and User Story 2 write paths.
- **Polish (Phase 6)**: Depends on all desired user stories.

### Parallel Opportunities

- T002 can run independently once docs exist.
- T006 and T007 can be written in parallel.
- T010 and T011 can be written in parallel.
- T015 and T016 can be written in parallel.
- T019 can run while implementation tests are being finalized.

## Implementation Strategy

1. Build the preview path first as the MVP.
2. Reuse preview output for profile generation.
3. Add fail-closed validation before creating checked-in recommended profile.
4. Validate with local quickstart commands and the full pytest suite.
