# Feature Specification: Guided Mission Control Cockpit UI

**Status**: Draft

**Created**: 2026-05-18

## User Story

As a vLLM optimizer user, I want the cockpit to guide me through the tuning
workflow like mission control, so I can understand what to do next without
guessing what Plan, Preview, Run, Report, Confirm, and Promote mean.

## Scope

- Use the provided cockpit screenshot as inspiration, not a pixel-perfect target.
- Redesign the first viewport around a clear workflow path and a right-side Next
  Action panel.
- Preserve deterministic CLI artifact behavior and existing controller safety
  gates.
- Keep the current Python-generated standalone HTML architecture.
- Avoid npm and external web assets.

## Requirements

- The cockpit must visibly show the six-step workflow:
  Plan, Preview, Run, Report, Confirm, Promote.
- The cockpit must identify the current step, locked/unlocked state, and next
  expected step in plain language.
- The right rail must lead with a Next Action panel explaining:
  current step, button action, safety facts, and follow-up steps.
- The central workspace must include a command shell for the current action.
- The UI must retain secondary tabs for detailed views.
- Controller buttons must continue to call local API endpoints when served and
  fall back to copying commands when opened as static HTML.
- Run and promotion safety gates must remain explicit.
- The layout must remain responsive on desktop and mobile without overlapping
  text or controls.

## Out of Scope

- New package manager dependencies.
- Persistent system changes on the GX10.
- Pixel-perfect recreation of the screenshot.
- Changing controller execution semantics.

## Acceptance Criteria

- Unit tests prove the rendered cockpit includes the mission workflow, next
  action panel, step command shell, and locked safety states.
- Existing cockpit tests continue to pass.
- Browser validation confirms the first viewport renders meaningful content,
  controls respond, no relevant console errors are present, and mobile layout is
  usable.
- README, changelog, version metadata, and SpecKit active pointers are updated.

