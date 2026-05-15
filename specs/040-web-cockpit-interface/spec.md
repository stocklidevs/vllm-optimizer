# Feature Specification: Web Cockpit Interface

**Feature Branch**: `040-web-cockpit-interface`  
**Created**: 2026-05-15  
**Status**: Draft  
**Input**: Create the first high-tech web interface that combines knob selection, operation progress, and reporting from existing deterministic artifacts.

## User Scenarios and Testing

### Primary User Story

As the optimizer operator, I want one polished cockpit that shows available knob groups, pipeline stages, safety gates, execution progress, and report summaries so I can understand and prepare optimization runs without using several separate static pages.

### Acceptance Scenarios

1. **Given** a knob group catalog exists, **when** I generate the web cockpit, **then** the HTML shows knob families, group cards, safety tiers, and opt-in requirements.
2. **Given** a pipeline control manifest exists, **when** it is included, **then** the cockpit shows ordered stages, remote markers, artifacts, required gates, and disabled future action controls.
3. **Given** execution status and canonical report artifacts exist, **when** they are included, **then** the cockpit shows progress status, trial counts, recommendation status, objective, and candidate summary.
4. **Given** optional artifacts are missing, **when** the cockpit is generated, **then** it still renders useful empty states.

## Requirements

- **FR-001**: The system MUST expose a `web-cockpit` CLI command.
- **FR-002**: The cockpit MUST be generated as standalone static HTML with no npm, no external assets, and no network dependencies.
- **FR-003**: The knob catalog path MUST be required.
- **FR-004**: Pipeline control, execution status, and canonical report paths MUST be optional.
- **FR-005**: The UI MUST use a mission-control layout with knob navigation, main workspace tabs/sections, and a status/action rail.
- **FR-006**: Future action controls MUST be visible but disabled in this spec.
- **FR-007**: Required safety gates MUST be displayed when present in input artifacts.
- **FR-008**: Missing optional artifacts MUST render as empty states rather than failing.

## Non-Goals

- Browser-triggered CLI execution.
- Live polling.
- npm or JavaScript framework setup.
- Editing or promoting profiles from the browser.

## Success Criteria

- Focused unit and CLI tests pass.
- Full pytest suite remains green.
- README documents the cockpit workflow and npm policy.
