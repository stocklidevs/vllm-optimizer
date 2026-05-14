# Research: Risky Winner Confirmation

## Decision: Use repeated A/B report as the promotion gate

**Rationale**: The risky sweep winner is promising but came from a short sweep. The existing repeated A/B report already handles aggregate latency, throughput, failure rate, spread, and a noise band.

**Alternatives considered**: Promote directly from the risky ranking. Rejected because it would let a single sweep ranking change the default profile without independent confirmation.

## Decision: Store compact confirmation provenance inside the promoted profile

**Rationale**: The default profile should explain why it changed without embedding every raw summary. Compact provenance preserves the report path, decision, labels, repetition counts, aggregate metrics, and deltas.

**Alternatives considered**: Store only the A/B report path. Rejected because the profile would lose quick local context when artifacts are moved or archived.

## Decision: Keep live benchmark artifacts ignored

**Rationale**: Benchmark outputs are machine-local evidence and can be large or environment-specific. The committed code and docs describe how to reproduce them, while git stores only durable configuration and promotion decisions.

**Alternatives considered**: Commit all benchmark summaries. Rejected because previous specs consistently keep `artifacts/` ignored.
