# Research: A/B Benchmark Confirmation

## Decision: Aggregate existing benchmark summaries

Rationale: The benchmark runner already writes normalized `summary.json`
artifacts. Aggregating those summaries avoids duplicating live benchmark logic.

Alternatives considered: Creating a new remote A/B runner was rejected because
it would duplicate remote lifecycle safety.

## Decision: Population spread for stability

Rationale: The project already uses population standard deviation for repeated
sweep stability. Using the same spread measure keeps reports consistent.

Alternatives considered: Sample standard deviation was unnecessary for a small
fixed repetition set and would diverge from existing sweep reporting.

## Decision: Conservative decision threshold

Rationale: A default profile should switch only when recommended is materially
better on both latency and throughput without higher failure rate. Mixed or
small differences remain inconclusive.

Alternatives considered: Switching on any one-metric improvement was rejected
because it can chase noise.
