# Feature Specification: Public Branch Cleanup

**Feature Branch**: `codex/public-release-cleanup`

**Created**: 2026-05-27

**Status**: Completed

**Input**: User asked to create a cleanup branch and complete the public-release
hygiene suggestions up to the point where the branch is ready to push publicly,
without actually pushing it.

## User Story 1 - Public Branch Readiness (Priority: P1)

As the maintainer, I want a dedicated cleanup branch with CI, publication
instructions, private-reference guards, and passing local gates, so that I can
decide when to push a public branch with confidence.

**Acceptance Scenarios**:

1. **Given** the cleanup branch is checked out, **When** a maintainer reads the
   publication checklist, **Then** the remaining local and GitHub gates are
   explicit and the stop line before public push is clear.
2. **Given** the repository is inspected for public release, **When** release
   docs and checks run, **Then** required public files, CI workflow, and version
   metadata are validated.
3. **Given** npm is used for UI QA tooling, **When** the publication gate runs,
   **Then** pinned installation and vulnerability audit are part of the process.

## Requirements

- **FR-001**: The branch MUST add a GitHub Actions workflow that runs pytest and
  release-check.
- **FR-002**: The branch MUST run `npm ci` and `npm audit --audit-level=high`
  for pinned UI QA dependencies.
- **FR-003**: The branch MUST document the exact stop line before pushing a
  public branch.
- **FR-004**: The branch MUST keep private SSH targets, local static paths, keys,
  and private network names out of committed public files.
- **FR-005**: The branch MUST leave live GX10 behavior unchanged; only ignored
  local config should contain real connection details.

## Success Criteria

- Full pytest passes.
- Release-check passes.
- npm install and vulnerability audit pass.
- The cleanup branch is committed and ready for maintainer review before push.
