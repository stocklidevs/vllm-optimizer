# Implementation Plan: Cockpit Premium Analytics

**Status**: Completed

## Summary

Upgrade the static cockpit into an outcome-first analytics surface: top-level
decision context, report-backed evidence charts, and a premium graphite visual
system that still reads clearly during end-to-end operations.

## Architecture

- Keep `render_web_cockpit` serverless/static and artifact-driven.
- Add small report-summary helpers that only derive display values from the
  canonical report and manifest.
- Render decision/evidence panels in the overview before operational details.
- Extend existing report metric rows for overview charts.
- Update CSS tokens and component classes for the premium cockpit skin.
- Keep JavaScript interaction hooks unchanged except where selectors need new
  passive UI updates.

## Verification

- Unit tests for overview decision/evidence rendering.
- Focused cockpit/release/version tests.
- Full pytest suite.
- Playwright validation against generated cockpit HTML on desktop and mobile.
