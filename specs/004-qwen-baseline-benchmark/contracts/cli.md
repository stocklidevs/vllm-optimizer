# CLI Contract: Qwen Baseline Benchmark

## `vllm-optimizer benchmark-plan`

Inputs:
- `--profile <path>`
- `--prompts <path>`
- `--out <path>`

Behavior:
- Renders baseline benchmark plan only.
- Does not open SSH.

## `vllm-optimizer benchmark-run`

Inputs:
- `--config <path>`
- `--profile <path>`
- `--prompts <path>`
- `--out <directory>`
- `--timeout-seconds <int>` optional, default 1200

Behavior:
- Starts Qwen through safe lifecycle wrapper.
- Runs fixed prompts sequentially.
- Saves metrics and artifacts.
- Cleans up.
