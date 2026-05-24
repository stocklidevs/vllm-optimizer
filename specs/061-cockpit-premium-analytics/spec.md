# Feature Specification: Cockpit Premium Analytics

**Status**: Completed

**Created**: 2026-05-24

## User Story

As a cockpit user, I want the first viewport to feel like a first-class
optimization cockpit that immediately tells me what improved, what is running,
what is safe, and what I should do next.

## Design Direction

- The cockpit should feel high-tech and premium without sacrificing clarity:
  dark graphite, subtle carbon-fiber/scanline texture, brushed-metal rails,
  restrained glass layers, crisp cyan/green/amber status lighting, and dense
  but readable operational data.
- Dashboard literature and current UI references favor fast scanning,
  outcome-first KPI hierarchy, actionable next steps, limited primary metrics,
  and charts that answer a decision question instead of decorating the page.
- The web cockpit remains a deterministic controller and reporting surface over
  canonical CLI artifacts. It must not recompute or override optimizer
  recommendations.

## Requirements

- Add an overview decision strip that summarizes:
  - selected tuning area,
  - current recommended candidate,
  - improvement versus baseline when available,
  - safety/report decision,
  - next safe action.
- Add a performance evidence panel with graphical views for:
  - baseline versus winner throughput,
  - latency versus throughput,
  - stability/failure context,
  - failure heatmap across candidates.
- Improve the cockpit visual system with premium textures, tighter hierarchy,
  reduced visual redundancy, and responsive behavior.
- Preserve the existing pipeline controls, report continuation path, safety
  gates, and artifact-driven data flow.
- Update tests so the new decision and evidence surfaces are protected.
- Update version, documentation, and changelog, then commit the completed work.

## Acceptance Criteria

- The overview renders useful decision/evidence content when a canonical report
  is loaded.
- The overview renders clear empty states when no report is loaded.
- The existing cockpit controller, reset, report, and tuning-area tests still
  pass.
- Browser validation covers desktop and mobile layouts with no relevant console
  errors.
- Release checks pass with SpecKit status completed before commit.
