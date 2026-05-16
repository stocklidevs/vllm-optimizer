# Feature Specification: Cockpit Report Visuals

**Feature Branch**: `042-cockpit-report-visuals`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Continue the web cockpit roadmap by making canonical report data visually useful inside the Reports tab.

## User Scenarios and Testing

### Primary User Story

As the optimizer operator, I want the cockpit Reports tab to show recommendation, throughput, latency, failure, and candidate comparison visuals so I can quickly understand why a configuration is winning.

### Acceptance Scenarios

1. **Given** a canonical report has candidate metrics, **when** the cockpit is generated, **then** the Reports tab shows throughput and latency bars for candidates.
2. **Given** candidate failures are present, **when** the report renders, **then** the cockpit shows failure rates and failed candidates clearly.
3. **Given** recommendation data exists, **when** the Reports tab renders, **then** the status, objective, candidate, rationale, and next actions are visible.
4. **Given** no canonical report is provided, **when** the cockpit renders, **then** the existing empty state remains.

## Requirements

- **FR-001**: Render a recommendation panel from canonical report recommendation fields.
- **FR-002**: Render candidate metric bars for throughput and latency.
- **FR-003**: Render a failure summary with failure rate and recommendable status.
- **FR-004**: Render rationale and next action lists when available.
- **FR-005**: Keep the feature static/read-only with no live browser-triggered execution.

## Non-Goals

- Interactive chart libraries.
- Recomputing rankings in the browser.
- Live report polling.

## Success Criteria

- Unit tests cover report visual markup.
- CLI integration remains green.
- Full pytest suite remains green.
