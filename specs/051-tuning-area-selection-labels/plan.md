# Implementation Plan: Tuning Area Selection and Labels

## Summary

Improve the cockpit's tuning-area mental model by adding presentation metadata
to the deterministic knob catalog and wiring static client-side selection in
`web_cockpit.py`.

## Architecture

- Extend `knob_catalog.py`:
  - `display_label`
  - `display_family`
  - `knobs_tuned`
  - friendlier descriptions for known families
- Keep existing `id`, `label`, `family`, and `config_path` fields intact.
- Update `web_cockpit.py` to prefer `display_label` and show `knobs_tuned`.
- Convert left-rail mini cards into selectable buttons with data attributes.
- Add lightweight JavaScript state for selected tuning area.

## Data Flow

- Catalog remains the source for selectable areas.
- Pipeline manifest remains the source for executable command hints.
- Browser selection updates static presentation only; it does not regenerate or
  mutate artifacts.

## Verification

- Focused unit tests for catalog labels and cockpit selection hooks.
- Focused CLI/web tests.
- Full pytest suite.
- Browser smoke validation of selecting a tuning area.

