# Data Model: Concurrency Saturation

## Saturation Input

- `concurrency`: Positive integer label from the CLI input.
- `ranking_path`: Path to a sweep ranking artifact.

Validation:

- Concurrency must be a positive integer.
- Ranking path must exist and contain a balanced objective winner.

## Saturation Level Summary

- `concurrency`: Concurrency level.
- `ranking_path`: Source artifact path.
- `sweep_id`: Source sweep id.
- `winner`: Compact winner candidate.
- `metrics`: Mean latency, aggregate tokens/sec, failure count/rate, success count.
- `overrides`: Serve parameter overrides for the winner.

Validation:

- Metrics must include numeric latency and throughput to be eligible for recommendation.
- Failed candidates may appear in source rankings but do not become winners.

## Saturation Recommendation

- `concurrency`: Recommended concurrency level.
- `candidate_id`: Recommended winner candidate.
- `metrics`: Recommendation metrics.
- `reason`: Deterministic explanation of the selection.

Tie breakers:

1. Highest aggregate tokens/sec.
2. Lowest failure rate.
3. Lowest mean latency.
4. Lowest concurrency.
5. Candidate id.
