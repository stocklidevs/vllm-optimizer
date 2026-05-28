# Data Model: Public Alpha Release and Results Narrative

## Public Release Checklist

Fields:

- `release_label`: public-facing version label such as `0.56.0 public alpha`
- `required_files`: license, README, setup, security, contributing, changelog, results
- `verification_commands`: full pytest, release-check, optional clean-checkout smoke
- `known_limitations`: alpha limitations and GX10-specific constraints
- `publication_steps`: local verification, commit, tag/release decision, optional push

Validation rules:

- Required files must be present before release.
- Verification commands must include expected pass criteria.
- GX10 live commands must be marked optional and gated.

## Benchmark Result Summary

Fields:

- `model_or_mode`: model or workload label
- `workload_context`: single-user, C8 aggregate, model safe-profile, or confirmation
- `baseline_tokens_per_second`
- `optimized_tokens_per_second`
- `delta_percent`
- `latency_context`
- `artifact_source`
- `interpretation`

Validation rules:

- Tokens/sec context must be explicit.
- C8 aggregate throughput must not be described as per-user throughput.
- Each headline value must have source provenance.

## Results Narrative

Fields:

- `headline`
- `what_improved`
- `what_did_not_improve`
- `why_it_happened`
- `how_to_reproduce`
- `limitations`

Validation rules:

- Must distinguish single-user and concurrent throughput.
- Must include at least one plain-language explanation of scheduler batching/concurrency effects.
- Must include limitations for model-specific and hardware-specific conclusions.
