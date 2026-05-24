# Implementation Plan: Objective Command Center Cockpit

**Status**: Completed

## Summary

Rebuild the cockpit page around an objective-first command center. The old
phase/knob-driven UI becomes an advanced inspection layer while the default
experience focuses on model, objective, safe start action, progress, and
decision reporting.

## Architecture

- Keep the existing `web_cockpit.py` artifact reader and controller contract.
- Replace the top-level render composition with a new dependency-free static
  HTML command-center shell.
- Preserve existing helper functions for metrics, commands, reports, runs, and
  promotion details where they remain useful, but move them behind disclosure
  sections.
- Add new objective command center CSS and JS while keeping controller,
  polling, tab-jump, target, profile, and tuning-area selection hooks intact.
- Update tests away from old left/right rail and tab assumptions toward the new
  objective-first information architecture.

## Verification

- Focused unit tests for the command center, advanced recipe disclosure,
  controller hooks, progress reset, report visuals, and target/profile
  selection.
- Static HTML smoke generation through the CLI test surface.
- Rendered browser validation at desktop and mobile widths.
- Release check.
- Full pytest suite.
