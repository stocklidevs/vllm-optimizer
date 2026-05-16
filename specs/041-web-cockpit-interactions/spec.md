# Feature Specification: Web Cockpit Interactions

**Feature Branch**: `041-web-cockpit-interactions`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Continue the web cockpit by making the static page easier to navigate and inspect without enabling live browser-triggered actions.

## User Scenarios and Testing

### Primary User Story

As the optimizer operator, I want the cockpit to behave like a real app surface with tabs, family filters, and search so I can quickly narrow knob groups and move between overview, knobs, pipeline, reports, and provenance.

### Acceptance Scenarios

1. **Given** many knob groups exist, **when** I type in the cockpit search box, **then** non-matching knob cards are hidden and the visible count updates.
2. **Given** knob families exist, **when** I choose a family filter, **then** only groups in that family remain visible.
3. **Given** the cockpit has multiple sections, **when** I choose a tab, **then** the selected section becomes active without leaving the page.
4. **Given** no groups match the filter/search, **when** the filter is applied, **then** an empty state is shown.

## Requirements

- **FR-001**: The cockpit MUST include client-side tab controls for overview, knobs, pipeline, reports, and provenance.
- **FR-002**: The cockpit MUST include a search field for knob groups.
- **FR-003**: The cockpit MUST include family filter buttons generated from catalog families.
- **FR-004**: Search and family filters MUST update visible knob cards and visible counts.
- **FR-005**: Filtering MUST be local-only static JavaScript with no npm, no network dependencies, and no live CLI execution.
- **FR-006**: Future controller action buttons MUST remain disabled.

## Non-Goals

- Live command execution from the browser.
- Server-side routing or dev server setup.
- npm framework adoption.

## Success Criteria

- Unit tests verify interactive markup and script hooks.
- CLI integration still generates standalone HTML.
- Full pytest suite remains green.
