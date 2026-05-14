# Research: Workload Leaderboard

## Decision: Use labeled ranking inputs

**Rationale**: Labeled inputs keep the report flexible and avoid hard-coding the current workload set.

**Alternatives considered**: A fixed Qwen-only command. Rejected because the same report pattern should work for future models and workload labels.

## Decision: Treat missing promotion as watch/evidence

**Rationale**: Several workload winners are useful evidence but were not materially strong enough for promotion. The report should preserve those findings without overstating them.

**Alternatives considered**: Promote every workload winner. Rejected because promotion requires repeated A/B confirmation.

## Decision: Detect known failure signatures from server logs

**Rationale**: The FP8 failures were not arbitrary benchmark failures; they exposed a missing system dependency. Surfacing that as a next action makes the report operationally useful.

**Alternatives considered**: Only count failures. Rejected because counts alone hide the root cause.
