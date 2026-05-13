# Data Model: vLLM Optimization Lab

## ExperimentDefinition

Represents the operator-authored optimization or measurement request.

Fields:
- `experiment_id`: stable identifier used for artifact paths
- `objective`: objective family, primary metric, direction, constraints, and
  tie-breakers
- `model`: model id, model path label, vLLM version, tokenizer label
- `workload`: prompt corpus id, request mix, concurrency values, seeds
- `parameter_space`: named vLLM parameters mapped to allowed values
- `target`: host label and execution mode
- `metadata`: operator notes and optional environment facts

Validation:
- Must include an objective family.
- Must include at least one parameter with at least one value.
- Must include at least one seed.
- Must default to dry-run mode for remote execution.

## TrialPlan

Represents the deterministic ordered set of concrete trial configurations.

Fields:
- `experiment_id`
- `created_at`
- `source_hash`
- `trials`

Relationships:
- Contains many `Trial` records.
- References one `ExperimentDefinition`.

## Trial

Represents one concrete configuration to test.

Fields:
- `trial_id`
- `ordinal`
- `seed`
- `parameters`
- `workload`
- `model`
- `objective_family`

Validation:
- Trial ids must be stable for the same experiment definition.
- Ordinals must be contiguous and start at 1.

## RemoteAction

Represents a planned command or lifecycle action.

Fields:
- `action_id`
- `trial_id`
- `kind`
- `classification`
- `command`
- `allowed`
- `expected_side_effects`
- `cleanup`

Validation:
- Classification must be `read-only`, `session-mutating`, or
  `persistent-mutating`.
- Live execution is not available in this feature.
- Commands outside the allowlist must be marked blocked.

## TrialArtifact

Represents raw data captured or supplied for one trial.

Fields:
- `trial_id`
- `artifact_type`
- `path`
- `sha256`
- `created_at`
- `source`

Relationships:
- Belongs to one `Trial`.
- May feed one or more objective scores.

## ObjectiveScore

Represents a computed score for one trial under one objective.

Fields:
- `trial_id`
- `objective_family`
- `primary_metric`
- `primary_value`
- `direction`
- `tie_break_values`
- `rank`
- `valid`
- `exclusion_reason`

## RecommendationReport

Represents the ranked output for an experiment.

Fields:
- `experiment_id`
- `objective`
- `ranked_trials`
- `excluded_trials`
- `artifact_refs`
- `generated_at`
