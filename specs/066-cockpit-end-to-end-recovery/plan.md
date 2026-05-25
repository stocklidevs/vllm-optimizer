# Implementation Plan: Cockpit End-to-End Recovery

**Status**: Completed

## Summary

Repair the active cockpit flow so a user can go from completed run artifacts to
one-click report review, select a candidate, and exercise gated promotion
against a local profile artifact. Align the one-command launcher with the
known high-throughput Qwen C8 concurrency sweep.

## Architecture

- Keep the CLI and artifacts as the source of truth.
- Add optional candidate selection to promotion helpers and CLI commands.
- Add an explicit `allow_promotion` gate to the cockpit server and launcher.
- Add a controller `promote` action that writes only local artifacts under the
  active cockpit output directory.
- Render candidate selection from canonical report candidates.
- Collapse report generation and review into one cockpit action that opens the
  Reports tab after generation.
- Remove duplicate primary action/progress presentation from the dashboard.

## Verification

- Red/green tests for one-click report review, candidate selection, gated
  promotion, selected-candidate promotion helpers, CLI candidate id support,
  and default launcher sweep selection.
- Focused cockpit/promotion/server/launcher/CLI test pack.
- Full test suite and release check.
- Browser validation against the active localhost cockpit.
