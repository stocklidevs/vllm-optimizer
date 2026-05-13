# CLI Contract: Qwen Smoke Serve

## `vllm-optimizer smoke-serve-plan`

Inputs:
- `--profile <path>`
- `--out <path>`

Behavior:
- Renders lifecycle plan only.
- Does not open SSH.

## `vllm-optimizer smoke-serve`

Inputs:
- `--config <path>`
- `--profile <path>`
- `--out <directory>`
- `--timeout-seconds <int>` optional, default 900

Behavior:
- Runs live session-mutating smoke workflow over SSH.
- Refuses unsafe preflight state.
- Starts one managed vLLM process.
- Polls readiness.
- Sends one tiny request.
- Attempts cleanup.
- Writes redacted artifacts.
