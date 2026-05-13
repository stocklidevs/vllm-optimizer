# Changelog

## 0.6.0 - 2026-05-13

- Added read-only vLLM flag discovery from the GX10 profile executable.
- Added Qwen safe flag policy and catalog generation for performance-relevant
  vLLM serve flags.
- Added parser, mock/live capture workflow, and SpecKit feature docs for flag
  cataloging.

## 0.5.0 - 2026-05-13

- Added expanded safe Qwen sweep configuration around the current 0.90/32768
  winner.
- Added local plan/preview tests for the expanded six-candidate,
  eighteen-trial repeated sweep.
- Added SpecKit feature docs for expanded Qwen sweep evaluation.

## 0.4.0 - 2026-05-13

- Added local run comparison reporting for baseline, sweep, and repeated sweep
  artifacts.
- Added JSON and Markdown report outputs with recommendations, baseline deltas,
  stability notes, failure counts, and artifact links.
- Added SpecKit feature docs for run comparison reporting.

## 0.3.0 - 2026-05-13

- Added deterministic Qwen parameter sweep planning, dry-run preview, live
  sequential sweep execution, and objective ranking.
- Added repeated top-two sweep stability analysis with candidate-level
  aggregation, spread metrics, failure-rate tracking, and baseline deltas.
- Added sample sweep configs for the small Qwen sweep and repeated top-two
  comparison.
- Added SpecKit feature docs for parameter sweep and repeated stability
  analysis.

## 0.2.0 - 2026-05-13

- Added read-only GX10 discovery over SSH.
- Added Qwen3 Coder Next serve profile and dry-run serve rendering.
- Added safe Qwen smoke serve lifecycle with cleanup verification.
- Added Qwen baseline benchmark with fixed prompts and summary metrics.
- Added CLI version output and README badges.

## 0.1.0 - 2026-05-13

- Initialized SpecKit project.
- Added deterministic experiment planning, dry-run action previews, fixture
  ranking, and artifact helpers.
