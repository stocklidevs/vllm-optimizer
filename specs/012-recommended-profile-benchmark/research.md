# Research: Recommended Profile Benchmark

## Decision: Reuse existing benchmark lifecycle

Rationale: The promoted profile should be tested under the same managed vLLM
serve and prompt execution lifecycle already used for baseline benchmarks.

Alternatives considered: Adding a custom recommended benchmark runner was
rejected because it would duplicate remote safety and cleanup behavior.

## Decision: Dedicated default decision report

Rationale: Existing comparison reports rank sweep candidates. This feature has
a narrower question: should the promoted profile remain the default starting
point after a standalone benchmark?

Alternatives considered: Extending the broad comparison report was rejected for
now because the default decision has different inputs and wording.

## Decision: Conservative keep/reject/inconclusive outcome

Rationale: A default profile should not be kept if it fails prompts or is worse
on both latency and throughput. Mixed signals should be inconclusive rather than
overstated.

Alternatives considered: Always keeping any promoted profile was rejected
because the standalone benchmark is meant to challenge the promotion.
