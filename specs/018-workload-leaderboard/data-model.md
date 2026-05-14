# Data Model: Workload Leaderboard

## Workload Summary

- `label`: Human-readable workload label.
- `ranking_path`: Source ranking artifact.
- `sweep_id`: Source sweep id.
- `winner`: Top balanced candidate summary.
- `baseline`: Baseline candidate summary, usually order `0`.
- `baseline_delta`: Winner versus baseline latency and throughput deltas.
- `failed_candidates`: Failed candidate summaries.
- `promoted_profile`: Optional promoted profile summary.
- `recommendation`: Status and action.

## Failed Candidate Finding

- `workload`: Workload label.
- `candidate_id`: Failed candidate.
- `overrides`: Candidate parameter overrides.
- `failure_summary`: Likely cause.

## Workload Leaderboard Report

- `workloads`: Workload summaries.
- `promoted_profiles`: Profiles referenced by workloads.
- `failed_candidate_findings`: Flattened failure findings.
- `next_actions`: Ordered action list.
