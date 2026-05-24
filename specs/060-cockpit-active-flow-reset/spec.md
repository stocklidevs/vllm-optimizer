# Feature Specification: Cockpit Active Flow Reset

**Status**: Implementing

**Created**: 2026-05-24

## User Story

As a cockpit user, I want a fresh Start Optimization click to clear stale
progress and completed stages from a previous run, and I want report review to
show obvious continuation options.

## Requirements

- Playwright must be installed as a pinned dev dependency and audited before
  browser validation.
- A new optimization started from a dashboard that already has a report loaded
  must reset visible progress and pipeline stage state immediately.
- While a new run is active, the Next Action panel must say the optimization is
  running instead of continuing to advertise the stale report.
- When the run completes, the Next Action panel must move to Load Report and
  re-enable the action button.
- The Reports tab must expose a clear continuation path from report evidence to
  confirmation and promotion gates.
- Tab-jump actions with `data-refresh-tab="false"` must switch tabs without a
  reload.

## Acceptance Criteria

- Unit tests cover the reset and report-continuation hooks.
- Playwright validation covers:
  - report-loaded startup state,
  - Start Optimization reset,
  - completed run transition to Load Report,
  - Review Report navigation,
  - report continuation options.
- Version and documentation are updated, and the work is committed.
