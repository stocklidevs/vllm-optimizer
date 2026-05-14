# Data Model: Promote Winner Profile

## Promotion Request

- `ranking_path`: Path to ranking artifact.
- `objective`: Objective name, defaulting to `balanced`.
- `profile_out`: Optional path for generated recommended profile.
- `summary_out`: Optional path for Markdown promotion summary.
- `profile_id`: Identifier to use in the generated profile.
- `allow_overwrite`: Whether existing outputs can be replaced.

Validation:
- Ranking path must exist and contain a JSON object.
- Objective must be present in the ranking artifact.
- Existing output paths require explicit overwrite permission.

## Promotion Preview

- `eligible`: Boolean decision.
- `objective`: Requested objective.
- `rank`: Selected candidate rank for that objective.
- `candidate_id`: Selected candidate id.
- `sweep_id`: Source sweep id.
- `metrics`: Ranking metrics for the selected candidate.
- `baseline_delta`: Optional baseline delta from ranking.
- `overrides`: Candidate parameter overrides.
- `source_trials`: Source trial ids and statuses.
- `proposed_profile`: Profile object that would be written.
- `provenance`: Traceability fields for audit.

Validation:
- Exactly one top-ranked candidate must be selected.
- Candidate aggregate must exist and have at least one successful repetition.
- Candidate source trials must be present.

## Recommended Profile

- Existing serve profile fields: model, served model name, host, port, model
  length, GPU memory utilization, tool parser, performance mode, and approved
  optional flags.
- `profile_id`: Recommended profile identifier.
- `promotion`: Embedded provenance, including ranking path, objective,
  candidate id, source trial ids, source metrics, source sweep id, and generated
  timestamp.

Validation:
- Profile must pass serve-profile validation.
- Optional flags must be approved by existing serve-profile rules.

## Promotion Summary

- Markdown record of objective, selected candidate, metrics, settings, source
  trials, and output profile path.

Validation:
- Summary must mention ranking artifact, objective, candidate id, and source
  trial ids.
