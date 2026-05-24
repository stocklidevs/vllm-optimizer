# Implementation Plan: Model and Objective Selection

**Status**: Completed

## Summary

Add a model/profile and optimization-target foundation to the cockpit. The UI
will make the current model and desired objective visible before any tuning area
is run, while preserving existing deterministic CLI/report behavior.

## Architecture

- Add profile-path plumbing to `web-cockpit`, `cockpit-server`, and
  `cockpit-launch`.
- Build lightweight profile summary dictionaries from existing serve profile
  JSON files.
- Render a model/profile selector and target selector near the top of the
  cockpit.
- Keep target selection as browser-local state for now.
- Add tests for profile rendering and target-selection hooks.

## Verification

- Focused cockpit, launcher, CLI, version, and docs tests.
- Release check.
- Full pytest suite.
