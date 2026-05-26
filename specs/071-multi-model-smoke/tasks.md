# Tasks: Multi-Model Registry and Smoke Workflow

- [x] T001 Create active SpecKit feature and quality checklist in `specs/071-multi-model-smoke/`.
- [x] T002 Validate candidate model identities and baseline assumptions from upstream sources.
- [x] T003 Record the model baseline tracker in `docs/PROJECT_STATUS.md`.
- [ ] T004 [P] Add model catalog loading tests in `tests/unit/test_model_catalog.py`.
- [ ] T005 [P] Add serve-profile rendering tests for Gemma 4 E4B IT and candidate profiles in `tests/unit/test_serve_profiles.py`.
- [ ] T006 [P] Add smoke-plan tests for model-aware plain chat and optional tool probes in `tests/unit/test_smoke.py`.
- [ ] T007 Implement model catalog parsing in `src/vllm_optimizer/model_catalog.py`.
- [ ] T008 Add `config/model-catalog.json` and local candidate profile files under `config/profiles/`.
- [ ] T009 Extend serve profile rendering for chat templates and optional parser/reasoning fields in `src/vllm_optimizer/serve_profiles.py`.
- [ ] T010 Extend smoke planning/results for model-aware readiness categories in `src/vllm_optimizer/smoke.py`.
- [ ] T011 Wire model catalog commands into `src/vllm_optimizer/cli.py`.
- [ ] T012 Surface model readiness and smoke recommendations in `src/vllm_optimizer/web_cockpit.py`.
- [ ] T013 Update README and setup documentation with multi-model smoke workflow commands.
- [ ] T014 Run focused tests, release check, and cockpit smoke rendering validation.
- [ ] T015 Update version, changelog, SpecKit status, and commit the completed feature.
