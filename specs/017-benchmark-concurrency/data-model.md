# Data Model: Benchmark Concurrency

## Prompt Set

- `prompt_set_id`: Stable id.
- `concurrency`: Positive integer, default `1`.
- `cases`: Prompt cases sent with a bounded worker count.

## Benchmark Metric

- `duration_ms`: Per-request duration.
- `batch_duration_ms`: Wall-clock duration for the concurrent batch.
- `tokens_per_second`: Per-request token rate.

## Benchmark Summary

- `mean_latency_ms`: Mean per-request latency.
- `aggregate_tokens_per_second`: Total tokens divided by batch duration when present.

## Concurrent Recommended Profile

- Serve profile confirmed for concurrent interactive coding.
- Includes sweep ranking provenance and A/B confirmation provenance.
