# Feature Specification: Tuning Area Selection and Labels

**Status**: Draft

**Created**: 2026-05-18

## User Story

As a cockpit user, I want tuning choices to use clear user-facing names and to
be selectable, so I can understand what knobs are being tuned without reading
internal sweep filenames.

## Requirements

- Replace user-facing "Knob Groups" language in the cockpit with "Tuning Areas"
  where it describes a selectable optimization area.
- Keep internal catalog and manifest compatibility with existing `group` fields.
- Generate friendlier labels for known sweep families, especially FP8 reruns and
  concurrency saturation sweeps.
- Add catalog metadata that lists the actual knobs or concepts tuned by each
  area.
- Make left-rail tuning areas clickable in the cockpit.
- Clicking a tuning area must visually select it and update:
  - selected tuning area card
  - knobs tuned list
  - active command shell command/context when a matching manifest command is
    available
- Avoid implying that words like "rerun" are knobs.
- Preserve deterministic static HTML behavior and active server controller
  behavior.

## Out of Scope

- Renaming existing JSON config files.
- Changing optimizer execution semantics.
- Adding package manager or frontend build dependencies.
- Dynamic regeneration of a new manifest from the browser selection.

## Acceptance Criteria

- Unit tests prove FP8 rerun files display as FP8 KV Cache tuning areas and do
  not expose "Rerun" in labels.
- Unit tests prove concurrency saturation files display request-count labels and
  include meaningful knob metadata.
- Unit tests prove the cockpit renders selectable tuning-area buttons and
  updates selected-area UI through client-side hooks.
- Existing tests continue to pass.

