# Research: Risky Session Knobs

## Decision: Risk-tier rules in serve profile module

Rationale: Serve command rendering is where CLI flag names and value types are
already centralized. Adding risk tier metadata there keeps sweep validation and
rendering aligned.

Alternatives considered: A separate risk catalog was rejected for now because it
would duplicate flag names and type rules.

## Decision: Plan/preview allowed, live run requires opt-in

Rationale: Operators need to inspect risky flags before running them, but live
execution should require an explicit command-line acknowledgement.

Alternatives considered: Rejecting risky flags at plan time was rejected because
it prevents useful dry-run previews.

## Decision: First live sweep limited to block size and eager mode

Rationale: These are session-local and impactful. `kv-cache-dtype` can affect
numerical behavior more broadly, so it is left for a follow-up if this pass is
stable.
