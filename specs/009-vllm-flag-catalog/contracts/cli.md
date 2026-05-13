# CLI Contract: vLLM Flag Catalog

## `vllm-optimizer flag-catalog`

Generate a catalog from local help/version files.

Arguments:
- `--policy <path>`: Policy JSON.
- `--help-file <path>`: Captured full `vllm serve --help` text.
- `--version-file <path>`: Optional version text.
- `--out <path>`: Catalog JSON output.

## `vllm-optimizer flag-catalog-capture`

Capture vLLM version/help over read-only SSH and write artifacts.

Arguments:
- `--config <path>`: GX10 discovery config.
- `--profile <path>`: Serve profile containing `vllm_executable`.
- `--policy <path>`: Policy JSON.
- `--out <dir>`: Artifact directory.
- `--executor mock|ssh`: Execution mode.
- `--mock-results <path>`: Required for mock mode.

Behavior:
- Does not start vLLM.
- Writes version, help, catalog, and redaction artifacts.
- Exits `2` on invalid policy/help or failed capture.
