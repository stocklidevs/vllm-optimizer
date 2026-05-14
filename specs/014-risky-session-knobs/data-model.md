# Data Model: Risky Session Knobs

## Risky Knob Rule

- `name`: Internal snake_case parameter name.
- `cli`: vLLM CLI flag name.
- `type`: Expected value type.
- `allowed`: Optional allowed values.
- `risk_tier`: `safe-session`, `risky-session`, or blocked.

## Risky Sweep Plan

- Existing sweep fields.
- `allow_risky_session_flags`: Whether the plan preview was explicitly allowed.
- `risk_tiers`: Mapping of parameter names to risk tiers.
- `has_risky_session_flags`: Boolean.

## Risky Sweep Preview

- Existing preview fields.
- `blocked`: True when risky-session flags exist without allowance.
- `blocked_reasons`: Reasons for blocked risk tiers or invalid values.

## Risky Sweep Result

- Existing sweep live result rows and ranking report.
- Risky parameters remain in candidate overrides for traceability.
