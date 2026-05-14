# Data Model: A/B Benchmark Confirmation

## A/B Confirmation Input

- `original_label`: Label for the original profile group.
- `recommended_label`: Label for the recommended profile group.
- `original_summaries`: Summary paths for original repetitions.
- `recommended_summaries`: Summary paths for recommended repetitions.
- `prompt_set_id`: Shared prompt set label.
- `noise_percent`: Percent threshold treated as noise.

Validation:
- Each group must contain at least one summary.
- Summary paths must exist and contain required metrics.

## Profile Aggregate

- `label`: Group label.
- `source_summary_paths`: Summary artifact paths.
- `repetition_count`: Number of summaries.
- `success_count`: Sum of successful prompt counts.
- `failure_count`: Sum of failed prompt counts.
- `failure_rate`: Failed prompts divided by all prompts.
- `mean_latency_ms`: Mean of per-repetition mean latencies.
- `latency_spread_ms`: Population spread of per-repetition mean latencies.
- `mean_tokens_per_second`: Mean of per-repetition aggregate throughput.
- `tokens_per_second_spread`: Population spread of per-repetition throughput.

## A/B Decision Report

- `decision`: `keep-original`, `switch-to-recommended`, or `inconclusive`.
- `reason`: Human-readable rationale.
- `aggregates`: Original and recommended aggregate metrics.
- `deltas`: Recommended minus original deltas.
- `inputs`: Prompt set, thresholds, source summary paths.
- `markdown`: Human-readable report.
