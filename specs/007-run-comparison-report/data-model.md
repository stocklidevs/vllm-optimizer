# Data Model: Run Comparison Report

## ReportInputSet

- `baseline_summary`: Optional path.
- `sweep_ranking`: Optional path.
- `repeated_ranking`: Optional path.
- `generated_from`: List of present paths.
- `missing_inputs`: List of omitted optional inputs.

## CandidateSnapshot

- `candidate_id`: Candidate or trial identifier.
- `source`: `repeated` or `sweep`.
- `objective`: Objective that ranked the candidate.
- `rank`: Rank under the objective.
- `overrides`: Parameter values when available.
- `metrics`: Mean latency, throughput, failure rate, spread, and counts.
- `baseline_delta`: Baseline comparison when available.
- `artifact_paths`: Source artifact references.
- `stability_note`: Human-readable stability summary when available.

## Recommendation

- `candidate_id`
- `source`
- `objective`
- `reason`
- `tradeoffs`
- `metrics`
- `artifact_paths`

## ComparisonReport

- `inputs`
- `baseline`
- `recommendation`
- `candidates`
- `notes`
- `markdown`
