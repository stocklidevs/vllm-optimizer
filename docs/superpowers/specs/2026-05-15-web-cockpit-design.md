# vLLM Optimizer Web Cockpit Design

## Direction

Use a hybrid cockpit: read-only by default, with visible but disabled controller
affordances that show where plan, preview, run, report, confirm, and promotion
actions will live later. The first implementation must not launch live commands
from the browser.

## Layout

The first screen is a mission-control dashboard:

- Left rail: knob group families and selectable optimization groups.
- Center workspace: tab-style sections for Overview, Knobs, Pipeline, and
  Reports.
- Right rail: execution status, safety gates, artifact availability, and future
  action controls.

The visual language should feel high-tech and operational: dark cockpit surface,
bright cyan/green status accents, dense but legible metrics, restrained
animation-free static HTML, and no decorative blobs or marketing layout.

## Data Sources

The cockpit consumes existing deterministic artifacts:

- Knob group catalog from `knob-groups`.
- Pipeline control manifest from `pipeline-control`.
- Execution status from `execution-status`.
- Canonical report from `canonical-report`.

Missing optional artifacts should render as empty states, not errors. The knob
catalog is required because it defines the dashboard's primary navigation.

## Safety Model

This spec is read-only. Buttons for Plan, Preview, Run, Confirm, and Promote
are visible but disabled. The UI must show required gates from manifests, such
as `--allow-risky-session-flags`, `--allow-session-tuning`, and
`--allow-promotion`, so the future controller mode is clear without being live.

## Implementation Shape

Avoid npm for this spec. Generate one standalone HTML file from Python with
inline CSS and no network assets. This keeps the first cockpit deterministic and
removes package supply-chain concerns. If a future spec introduces npm, package
versions must be pinned and installation must use `npm ci` after vulnerability
review.

## Testing

Unit tests should verify the rendered shell includes the required regions,
artifact values, disabled action controls, and safety gates. CLI tests should
verify a standalone HTML cockpit can be generated from fixture artifacts.
