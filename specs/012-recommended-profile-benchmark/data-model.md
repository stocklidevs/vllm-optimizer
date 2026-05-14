# Data Model: Recommended Profile Benchmark

## Recommended Benchmark Plan

- `profile_id`: Recommended profile identifier.
- `prompt_set_id`: Prompt corpus identifier.
- `request_sequence`: Prompt case ids, max tokens, and temperatures.
- `metrics`: Expected metric names.
- `serve_plan`: Existing managed vLLM serve plan.

Validation:
- Recommended profile must parse as a serve profile.
- Prompt set must be non-empty.

## Recommended Benchmark Result

- `summary`: Success count, failure count, mean latency, total tokens, and
  aggregate tokens per second.
- `artifact_paths`: Plan, prompts, responses, metrics, summary, server log,
  cleanup, and redaction artifacts.

Validation:
- Summary must include numeric latency and throughput when success count is
  greater than zero.

## Default Decision Report

- `decision`: `keep`, `reject`, or `inconclusive`.
- `reason`: Human-readable explanation.
- `baseline`: Original baseline metrics.
- `recommended`: Recommended benchmark metrics.
- `deltas`: Absolute and percent deltas for latency and throughput.
- `provenance`: Profile id, candidate id, source sweep id, source trial ids,
  profile path, and optional source ranking path.
- `markdown`: Human-readable report.

Validation:
- Required input summaries must be present.
- Recommended profile provenance should be included when available.

## Default Decision

- `keep`: Recommended benchmark succeeded and is not worse than baseline on
  both latency and throughput.
- `reject`: Recommended benchmark failed or is worse than baseline on both
  latency and throughput.
- `inconclusive`: Metrics are missing or mixed enough to require more evidence.
