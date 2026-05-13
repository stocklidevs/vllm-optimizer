# CLI Contract: vLLM Optimization Lab

The CLI is named `vllm-optimizer`.

## `vllm-optimizer plan`

Generate a deterministic trial plan.

Required inputs:
- `--experiment <path>`: JSON experiment definition
- `--out <path>`: destination JSON file

Behavior:
- Validates the experiment definition.
- Writes a trial plan JSON document.
- Prints the output path.
- Exits non-zero on validation errors.

## `vllm-optimizer dry-run`

Preview remote actions without opening SSH.

Required inputs:
- `--plan <path>`: trial plan JSON
- `--out <path>`: destination command preview JSON

Behavior:
- Renders planned read-only probe, lifecycle, benchmark, artifact, and cleanup
  actions.
- Applies the safety allowlist.
- Marks blocked actions instead of executing anything.
- Exits non-zero when blocked actions exist unless `--allow-blocked-preview`
  is supplied.

## `vllm-optimizer rank`

Rank fixture or captured trial results.

Required inputs:
- `--plan <path>`: trial plan JSON
- `--results <path>`: JSONL metrics where each line includes `trial_id`
- `--out <path>`: destination report JSON

Behavior:
- Scores valid trials for the plan objective.
- Supports throughput and latency ranking in the MVP.
- Excludes missing or malformed trial results with reasons.
- Writes a recommendation report with artifact references.
