# Data Model: Risky Winner Confirmation

## Confirmation Report

- `decision.status`: One of `switch-to-recommended`, `keep-original`, or `inconclusive`.
- `decision.reason`: Human-readable explanation.
- `inputs.original_label`: Control profile label.
- `inputs.recommended_label`: Candidate profile label.
- `aggregates.original`: Repetition count, failure rate, latency, throughput, and spread for the control.
- `aggregates.recommended`: Repetition count, failure rate, latency, throughput, and spread for the candidate.
- `deltas`: Candidate minus control metric deltas.

## Confirmed Promotion

- `ranking_path`: Source sweep ranking used to reconstruct the promoted profile.
- `objective`: Ranking objective.
- `candidate_id`: Selected risky sweep candidate.
- `overrides`: Promoted parameter overrides.
- `confirmation`: Compact copy of the A/B confirmation decision and aggregate evidence.

## Risky Winner Profile

- Base vLLM model and serve identity from the original Qwen profile.
- Safe scheduler flags from the current recommended profile.
- Risky-session flags from the risky sweep winner, such as block size.
- Promotion provenance linking back to the risky-session ranking.
