# Research: Qwen Smoke Serve

## Decision: Use a shell wrapper for live lifecycle

**Rationale**: A single remote bash script can start vLLM, capture PID/logs,
poll readiness locally on the GX10, send one request, and clean up in a trap.
This keeps process ownership clear.

**Alternatives considered**: Multiple SSH calls were rejected because cleanup
is harder if the controller disconnects between steps.

## Decision: Refuse before start on occupied port or existing vLLM process

**Rationale**: Smoke serve must not disrupt an existing server. Preflight checks
run before the serve command and fail closed.

**Alternatives considered**: Reusing an existing server was deferred to a later
feature.

## Decision: Local artifacts only

**Rationale**: The remote command streams JSON/log content back to the
controller, which writes redacted local artifacts. This avoids leaving test
state on the GX10 beyond transient process activity.

**Alternatives considered**: Remote artifact directories were deferred until
longer benchmarks need them.
