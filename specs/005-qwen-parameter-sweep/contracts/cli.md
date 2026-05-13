# CLI Contract: Qwen Parameter Sweep

## `vllm-optimizer sweep-plan`

Generate a deterministic local sweep plan without contacting the GX10.

Required arguments:
- `--sweep <path>`: Sweep definition JSON.
- `--out <path>`: Output JSON path.

Behavior:
- Validates the sweep definition and safe parameter allowlist.
- Loads the baseline profile and prompt set.
- Generates stable trial ids, rendered serve commands, and artifact paths.
- Writes a JSON plan and prints the output path.
- Exits `2` for invalid sweep definitions.

## `vllm-optimizer sweep-preview`

Render a dry-run preview from a sweep plan.

Required arguments:
- `--plan <path>`: Sweep plan JSON.
- `--out <path>`: Output JSON path.

Behavior:
- Performs no SSH commands.
- Lists all trials, changed parameters, classifications, artifacts, metrics,
  and cleanup.
- Writes a JSON preview and prints the output path.
- Exits `2` when blocked trials exist.

## `vllm-optimizer sweep-rank`

Rank completed or fixture sweep results for one or more objectives.

Required arguments:
- `--plan <path>`: Sweep plan JSON.
- `--results <path>`: Trial result JSON or JSONL.
- `--out <path>`: Ranking report JSON.

Behavior:
- Produces throughput, latency, and balanced rankings by default.
- Links each ranked row back to source artifacts.
- Excludes incomplete trials with documented reasons.
- Exits `2` when no rankable trials exist.

## `vllm-optimizer sweep-run`

Run a small approved live sweep sequentially.

Required arguments:
- `--config <path>`: Ignored local GX10 config.
- `--plan <path>`: Sweep plan JSON.
- `--out <path>`: Artifact root.

Optional arguments:
- `--timeout-seconds <int>`: Per-trial timeout.
- `--continue-on-failure`: Continue after safe individual trial failures.

Behavior:
- Starts from a preflight check for each trial.
- Runs the existing baseline benchmark lifecycle using the trial profile.
- Saves per-trial artifacts and aggregate results.
- Attempts cleanup after every started trial.
- Exits `2` when any trial fails unless continuing is explicitly allowed.
