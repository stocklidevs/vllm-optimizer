# Implementation Plan: End-to-End Cockpit Dashboard

**Status**: Completed

## Summary

Make the cockpit dashboard useful for end-to-end operations by replacing
duplicated status panels with an operational flow map, and by aligning primary
actions with the controller capabilities that actually exist today.

## Architecture

- Add a reusable primary-action button renderer that can produce either:
  - a controller-backed action button, or
  - a tab-navigation action for review/manual gates.
- Keep Start Optimization and Load Report as real controller actions.
- Convert report-ready `confirm` and `promote` states into review/gate actions
  instead of unsupported controller calls.
- Add an overview flow map that summarizes completed, current, and gated stages.
- Update release docs and active SpecKit metadata.

## Verification

- Focused unit tests for cockpit rendering and active server integration.
- Full pytest suite.
- Browser smoke validation of the generated dashboard.
