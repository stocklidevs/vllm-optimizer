# Feature Specification: Objective Command Center Cockpit

**Status**: Completed

**Created**: 2026-05-24

## User Story

As a cockpit user, I want the web interface to start with my optimization
objective instead of low-level knob families so I can run and understand the
optimizer without learning every internal pipeline phase first.

## Requirements

- The cockpit must replace the default layout with an objective-first command
  center.
- The first screen must make these choices clear:
  - model/profile,
  - optimization objective,
  - selected tuning recipe,
  - primary start/review action,
  - live progress,
  - current recommendation.
- Micro-tweaks and knob-family details must remain available, but they must be
  hidden behind an advanced/disclosure surface by default.
- Pipeline internals such as Plan, Preview, Run, Report, Confirm, and Promote
  must be presented as an automated progress narrative instead of the main
  navigation model.
- Reports must read as a decision story:
  - baseline,
  - winner,
  - improvement,
  - stability/risk,
  - next safe action.
- Existing deterministic artifacts, controller endpoints, report parsing, and
  promotion gates must remain unchanged.
- The runtime cockpit must remain dependency-free; no npm application stack is
  introduced by this feature.
- Version, documentation, tests, and release metadata must be updated and the
  work committed.

## Acceptance Criteria

- `web-cockpit` renders a modern objective command center instead of the old
  left-rail/right-rail/tab-heavy mission-control layout.
- The primary page contains one clear `Start Optimization` or report-review
  action with progress feedback.
- Advanced tuning recipe details are collapsed by default and can be expanded
  to inspect tuning areas, knobs, command hints, sources, runs, and promotion
  gates.
- Model/profile and objective selections remain visible near the start of the
  workflow.
- Existing active controller hooks still call the local cockpit server when
  served dynamically and still degrade safely in static HTML.
- Focused cockpit tests, release check, and the full test suite pass.
