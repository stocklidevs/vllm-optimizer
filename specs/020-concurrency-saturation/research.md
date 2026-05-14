# Research: Concurrency Saturation

## Decision: Use a concurrency ladder of 1, 2, 3, 4, 6, and 8

**Rationale**: This brackets the already-measured concurrency 3 winner while probing lower latency points and higher saturation pressure without exploding live runtime.

**Alternatives considered**: Testing every value 1 through 8 was rejected because it doubles live work for little extra signal. Jumping directly to high concurrency was rejected because it would miss the knee of the curve.

## Decision: Keep candidate matrix near the known winner

**Rationale**: The current best concurrent profile uses `gpu_memory_utilization=0.92`, `block_size=16`, `max_num_batched_tokens=4096`, and `max_num_seqs=16`. The next useful question is saturation, so the matrix should vary only batch/seq/gpu pressure around that point.

**Alternatives considered**: Reopening FP8 or block-size exploration was rejected for this spec because recent live evidence showed FP8 is not competitive and block size already has a known concurrent winner.

## Decision: Report recommendation by throughput, then stability, latency, and lower concurrency

**Rationale**: For serving concurrency, aggregate throughput is the goal, but failed or unstable candidates should not win. Lower concurrency wins ties to preserve responsiveness when throughput is effectively equal.

**Alternatives considered**: Balanced score from individual sweep ranking was rejected as the cross-level comparator because it normalizes within each ranking, not across concurrency levels.
