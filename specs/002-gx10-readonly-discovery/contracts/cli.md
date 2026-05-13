# CLI Contract: GX10 Read-Only Discovery

## `vllm-optimizer discover`

Run read-only discovery for a configured target.

Inputs:
- `--config <path>`: local JSON discovery config
- `--out <directory>`: artifact output directory
- `--executor mock|ssh`: mock uses recorded outputs; ssh runs read-only probes
- `--mock-results <path>`: JSON fixture outputs required for mock execution

Behavior:
- Loads the local config.
- Validates the fixed read-only probe catalog.
- Executes connectivity first.
- Skips remaining probes if connectivity fails.
- Redacts configured values before writing artifacts.
- Writes `raw-probes.json`, `summary.json`, and `redaction-report.json`.

Exit codes:
- `0`: discovery completed, possibly with optional probe failures
- `2`: invalid config or safety validation failure
- `3`: connectivity failed

Non-goals:
- No vLLM start/stop.
- No package installation or system tuning.
