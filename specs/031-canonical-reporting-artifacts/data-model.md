# Data Model: Canonical Reporting Artifacts

## Canonical Report

- `schema_version`: Version of the report contract.
- `generated_at`: UTC generation timestamp.
- `source`: Report source metadata.
- `recommendation`: Decision outcome and rationale.
- `objectives`: Objective summaries keyed by objective name.
- `candidates`: Candidate summaries keyed by candidate identity.
- `chart_datasets`: Normalized arrays for dashboard views.
- `provenance`: Source artifact paths and generation inputs.
- `markdown`: Optional human-readable content when stored in JSON.

## Report Source

- `family`: Source family such as `sweep`, `session-tuning-sweep`, `pipeline`, or `confirmation`.
- `label`: Human label for the run.
- `plan_path`: Optional plan artifact path.
- `ranking_path`: Ranking artifact path.
- `results_path`: Optional results artifact path.
- `summary_path`: Optional run summary path.
- `action_scope`: `local-only`, `read-only`, `session-mutating`, or `persistent-mutating`.

## Recommendation

- `status`: `recommended-winner`, `keep-baseline`, `requires-confirmation`, or `no-recommendation`.
- `candidate_id`: Winning or baseline candidate when available.
- `objective`: Objective that drove the decision.
- `summary`: One-sentence user-facing decision.
- `rationale`: Supporting evidence and safety notes.
- `next_actions`: Ordered follow-up actions.

## Candidate Summary

- `candidate_id`: Stable candidate identifier.
- `label`: Human label when available.
- `is_baseline`: Whether the candidate represents the current/default/no-tuning baseline.
- `recommendable`: Whether the candidate is eligible for recommendation.
- `metrics`: Throughput, latency, failure, and spread metrics.
- `objectives`: Rank and score per objective.
- `artifact_paths`: Candidate-level provenance links.
- `exclusion_reason`: Reason the candidate cannot be recommended.

## Chart Dataset

- `name`: Dataset name for UI selection.
- `kind`: Expected visualization family, such as `ranking`, `bar`, or `scatter`.
- `x`: X-axis key.
- `y`: Y-axis key.
- `rows`: Normalized data rows.
