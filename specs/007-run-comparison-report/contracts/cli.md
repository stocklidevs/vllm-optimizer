# CLI Contract: Run Comparison Report

## `vllm-optimizer report`

Generate a local comparison report from existing artifacts.

Arguments:
- `--baseline <path>`: Optional baseline summary JSON.
- `--sweep-ranking <path>`: Optional one-shot sweep ranking JSON.
- `--repeated-ranking <path>`: Optional repeated sweep ranking JSON.
- `--out <path>`: Required JSON report output.
- `--markdown-out <path>`: Optional Markdown report output.

Behavior:
- Does not contact the GX10.
- Reads available inputs and records missing optional inputs.
- Prefers repeated ranking for the headline recommendation when available.
- Writes JSON report and optional Markdown report.
- Exits `2` when no ranking input is available or inputs are malformed.
