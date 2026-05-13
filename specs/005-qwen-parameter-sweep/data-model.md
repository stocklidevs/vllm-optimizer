# Data Model: Qwen Parameter Sweep

## SweepDefinition

- `sweep_id`: Stable name for the sweep.
- `profile`: Path to the baseline serve profile.
- `prompts`: Path to the prompt set.
- `baseline_summary`: Optional path to a baseline summary for deltas.
- `seed`: Integer used for reproducibility metadata.
- `max_trials`: Upper bound for generated trials.
- `objectives`: Ordered objective names to report.
- `parameters`: Map of allowed parameter names to candidate values.

Validation:
- `sweep_id`, `profile`, `prompts`, `parameters`, and `objectives` are
  required.
- `max_trials` must be positive when provided.
- Parameter names must be in the safe session-level allowlist.
- Candidate values must match the expected type and safety bounds.

## SweepTrial

- `trial_id`: Deterministic identifier derived from sweep id, order, and
  parameter overrides.
- `order`: Zero-based execution order.
- `profile_id`: Baseline profile id with trial suffix.
- `overrides`: Parameters changed from the baseline.
- `serve_plan`: Rendered vLLM serve command for the trial.
- `artifact_dir`: Planned artifact directory for the trial.
- `classification`: Always session-mutating for live execution.

Validation:
- Trial ordering must be stable for repeated generation.
- Rendered commands may only include known vLLM serve options.

## SweepPreview

- `sweep_id`: Source sweep identifier.
- `mode`: Dry-run.
- `will_execute`: Always false.
- `trial_count`: Number of generated trials.
- `blocked`: Whether any trial is unsafe.
- `blocked_reasons`: Safety errors by trial or parameter.
- `trials`: Preview rows for all generated trials.

## TrialResult

- `trial_id`: Related trial.
- `status`: Completed, failed, skipped, or blocked.
- `summary`: Benchmark summary when available.
- `baseline_delta`: Difference from baseline metrics when available.
- `artifacts`: Paths to raw responses, metrics, logs, cleanup, and summary.
- `failure_reason`: Required when status is not completed.

## SweepRanking

- `sweep_id`: Source sweep identifier.
- `objective`: throughput, latency, or balanced.
- `ranked_trials`: Ordered recommendation rows.
- `constraints`: Metrics required for inclusion.
- `tie_breakers`: Deterministic tie-breaking fields.
- `source_artifacts`: Links to trial results and baseline summary.
