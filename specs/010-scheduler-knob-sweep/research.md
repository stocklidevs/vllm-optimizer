# Research: Scheduler Knob Sweep

## Decision: Explicit Optional Flag Allowlist

Rationale: The flag catalog provides categories, but command rendering should
still use a narrow checked-in allowlist with type validation.

Alternatives considered: Allowing any safe-policy flag automatically was
deferred because each flag may need value-specific validation.

## Decision: Keep Scheduler Sweep Small

Rationale: Scheduler knobs can interact strongly. The first sweep should test a
small number of plausible scheduler configurations before expanding.

Alternatives considered: Full Cartesian search over all safe flags was rejected
because it would create too many live trials.

## Decision: Reuse Existing Sweep Runner

Rationale: Optional flags are still session-level vLLM serve arguments, so the
existing lifecycle and cleanup path remains appropriate.

Alternatives considered: A separate scheduler runner was rejected as duplicate
automation.
