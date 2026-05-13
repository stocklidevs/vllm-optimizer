# Data Model: Qwen Baseline Benchmark

## PromptSet

Fields:
- `prompt_set_id`
- `cases`

## PromptCase

Fields:
- `case_id`
- `messages`
- `max_tokens`
- `temperature`

## BenchmarkPlan

Fields:
- `profile_id`
- `prompt_set_id`
- `serve_plan`
- `request_sequence`
- `artifact_paths`

## RequestMetric

Fields:
- `case_id`
- `status`
- `duration_ms`
- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `tokens_per_second`

## BaselineSummary

Fields:
- `success_count`
- `failure_count`
- `mean_latency_ms`
- `total_tokens`
- `aggregate_tokens_per_second`
