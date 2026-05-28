# Tasks: Public Alpha Release and Results Narrative

**Input**: Design documents from `specs/072-public-alpha-release/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required for release-check/public docs guards and full project verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Make Spec 072 active and establish release target metadata.

- [x] T001 Update `.specify/feature.json` to point at `specs/072-public-alpha-release`.
- [x] T002 Update `AGENTS.md` active SpecKit pointer to `specs/072-public-alpha-release/plan.md`.
- [x] T003 Bump package version to `0.56.0` in `pyproject.toml`, `src/vllm_optimizer/__init__.py`, `uv.lock`, README badge, and `docs/PROJECT_STATUS.md`.
- [x] T004 Add `0.56.0 - public alpha` release notes placeholder to `CHANGELOG.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add public-facing repository gates before story-specific docs.

- [x] T005 Add `LICENSE` with MIT license text unless the user requests a different license before implementation.
- [x] T006 Add `CONTRIBUTING.md` with local setup, test, SpecKit, docs/version/commit, and GX10 safety expectations.
- [x] T007 Add `SECURITY.md` with vulnerability reporting guidance and scope boundaries for local SSH/GX10 automation.
- [x] T008 Extend `tests/unit/test_release_docs.py` to assert README links to license, contributing, security, public release, and results docs.
- [x] T009 Extend `src/vllm_optimizer/release_check.py` and `tests/unit/test_release_check.py` so release-check validates required public files for a public alpha.

**Checkpoint**: Public repository hygiene files exist and are guarded by tests.

---

## Phase 3: User Story 1 - Publishable Project Basics (Priority: P1)

**Goal**: A public visitor can understand, install, and safely evaluate the project.

**Independent Test**: Read README and setup docs from a fresh checkout; run no-GX10 quickstart commands.

- [x] T010 [US1] Rewrite the README intro and Quickstart sections to label the project as public alpha and link to setup, results, release checklist, safety, contribution, security, and roadmap docs.
- [x] T011 [US1] Update `docs/SETUP.md` with a public no-GX10 quickstart, optional GX10 live path, local config redaction guidance, and cache hygiene.
- [x] T012 [US1] Create `docs/PUBLIC_RELEASE.md` from `specs/072-public-alpha-release/contracts/public-release-checklist.md`.
- [x] T013 [US1] Update `docs/PROJECT_STATUS.md` with public alpha status, latest disk cleanup state, and current release scope.
- [x] T014 [US1] Run `uv run vllm-optimizer --version` and verify it prints `0.56.0`.

**Checkpoint**: Public basics are understandable without private context.

---

## Phase 4: User Story 2 - Results Presentation (Priority: P2)

**Goal**: Public readers understand the benchmark results and why single-user and concurrent gains differ.

**Independent Test**: Open `docs/RESULTS.md` and verify every headline result includes context, delta, explanation, and provenance.

- [x] T015 [P] [US2] Create a small results source table in `docs/RESULTS.md` using artifact values from `docs/PROJECT_STATUS.md`, Qwen C8 profile metadata, and model baseline summaries.
- [x] T016 [US2] Add a `How To Read Tokens Per Second` section explaining C1, C8 aggregate throughput, and C8 per-request average.
- [x] T017 [US2] Add a `Why The Results Look Like This` section explaining batching, concurrency, scheduler pressure, model/backend constraints, and why single-user gains were modest.
- [x] T018 [US2] Add `Reproduction And Provenance` links to source artifacts such as `artifacts/benchmarks/qwen-baseline/summary.json`, `artifacts/sweeps/qwen-concurrency-saturation-c8/live/ranking.json`, and `artifacts/models/*/baseline/summary.json`.
- [x] T019 [US2] Add release-doc tests that assert `docs/RESULTS.md` contains C8 aggregate wording, per-request explanation, and all required model names.

**Checkpoint**: Results story is honest, traceable, and hard to misread.

---

## Phase 5: User Story 3 - Fresh-Clone Release Verification (Priority: P3)

**Goal**: Maintainers can validate the public alpha from a clean-checkout perspective.

**Independent Test**: Follow `docs/PUBLIC_RELEASE.md` and confirm the release evidence is captured.

- [x] T020 [US3] Add a fresh-checkout verification section to `docs/PUBLIC_RELEASE.md` with exact commands and expected outcomes.
- [x] T021 [US3] Add known limitations covering GX10 specificity, optional live SSH runs, experimental cockpit maturity, model cache cleanup, and non-PyPI packaging status.
- [x] T022 [US3] Run full `uv run pytest` or the local `.venv` equivalent and record the result in the changelog or release checklist.
- [x] T023 [US3] Run `uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md` or the local `.venv` equivalent and verify `overall_status: pass`.
- [x] T024 [US3] Confirm `git status --short` is clean before the public alpha release commit.

**Checkpoint**: Release evidence exists and public alpha is ready for publication decision.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Close the SpecKit feature cleanly and prepare the final handoff.

- [x] T025 Update `specs/072-public-alpha-release/spec.md` status to `Completed`.
- [x] T026 Update `specs/072-public-alpha-release/tasks.md` checkboxes as tasks complete.
- [x] T027 Run focused tests for release docs and release-check.
- [x] T028 Run full tests and release-check after all docs/code updates.
- [x] T029 Commit the public alpha release readiness work.
- [x] T030 Present publication options: keep as public alpha branch, merge locally, push/create PR, or tag release.

## Dependencies & Execution Order

- Phase 1 must complete before implementation because it changes active SpecKit metadata and version target.
- Phase 2 blocks public release because license, security, contributing, and release-check guards are foundational.
- US1 can complete independently once Phase 2 is done.
- US2 can complete independently once result sources are confirmed.
- US3 should run after US1 and US2 so verification covers final public docs.
- Final polish runs after all desired user stories are complete.

## Suggested MVP Scope

The MVP for public alpha publishability is Phase 1, Phase 2, and User Story 1. User Story 2 is strongly recommended before any announcement because the performance numbers need context.
