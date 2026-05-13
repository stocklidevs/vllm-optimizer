# Data Model: Repeated Sweep Stability

## SweepDefinition Additions

- `repetitions`: Positive integer. Defaults to one for existing sweep configs.

Validation:
- Must be an integer greater than or equal to one.
- Generated total trial count must respect `max_trials` as a candidate limit,
  not a repetition limit.

## Candidate

- `candidate_id`: Deterministic identifier for one unique override set.
- `order`: Candidate order.
- `overrides`: Parameter values for this candidate.
- `repetitions`: Number of repeated trials.

## RepeatedTrial

- `trial_id`: Deterministic identifier for one candidate repetition.
- `candidate_id`: Parent candidate identifier.
- `candidate_order`: Candidate order.
- `repetition_index`: Zero-based repetition number.
- `profile`: Trial profile variant.
- `artifact_dir`: Repetition-specific artifact path.

## CandidateAggregate

- `candidate_id`
- `overrides`
- `success_count`
- `failure_count`
- `failure_rate`
- `mean_latency_ms`
- `latency_spread_ms`
- `mean_tokens_per_second`
- `tokens_per_second_spread`
- `baseline_delta`
- `source_trials`

## StabilityRanking

- `objective`
- `ranked_candidates`
- `excluded_candidates`
- `baseline_summary_path`
