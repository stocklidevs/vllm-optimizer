# Research: Repeated Sweep Stability

## Decision: Model Repetitions as Trial Metadata

Rationale: Repetitions are executions of the same candidate, so the plan should
preserve both a candidate id and a repeated trial id. This keeps artifacts
traceable while allowing aggregate reports by candidate.

Alternatives considered: Duplicating candidates without a candidate id was
rejected because aggregate grouping would be fragile.

## Decision: Use Simple Spread Metrics First

Rationale: Mean and population spread are easy to inspect and enough for the
first "is this probably noise?" pass with three repetitions.

Alternatives considered: Formal statistical tests were deferred until larger
sample sizes exist.

## Decision: Stability as Tie-Breaker

Rationale: The primary objective should still be throughput or latency, but
failure rate and spread should decide close comparisons.

Alternatives considered: Penalizing score heavily for spread was deferred
because the right penalty weight needs more real data.
