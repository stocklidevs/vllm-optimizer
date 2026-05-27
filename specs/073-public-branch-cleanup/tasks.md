# Tasks: Public Branch Cleanup

**Input**: Design documents from `specs/073-public-branch-cleanup/`

- [x] T001 Create `codex/public-release-cleanup` branch from the current public
  alpha state.
- [x] T002 Add `.github/workflows/ci.yml` for pytest, release-check, npm ci,
  and npm audit.
- [x] T003 Add `docs/PUBLICATION_CHECKLIST.md` with local gates, GitHub gates,
  and the explicit stop line before public push.
- [x] T004 Link the publication checklist from README and public release docs.
- [x] T005 Extend release-check required public files to include CI and the
  publication checklist.
- [x] T006 Bump version and changelog for the cleanup release metadata.
- [x] T007 Run focused release docs/version tests.
- [x] T008 Run full pytest.
- [x] T009 Run release-check.
- [x] T010 Run `npm ci`.
- [x] T011 Run `npm audit --audit-level=high`.
- [x] T012 Commit the cleanup branch work.
