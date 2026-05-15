# Contract: Canonical Report CLI

## Command

```powershell
uv run vllm-optimizer canonical-report --family session-tuning-sweep --label qwen-runtime-env --ranking artifacts/session-tuning-sweeps/qwen-runtime-env/live/ranking.json --summary artifacts/session-tuning-sweeps/qwen-runtime-env/live/summary.json --out artifacts/reports/qwen-runtime-env/canonical-report.json --markdown-out artifacts/reports/qwen-runtime-env/report.md --baseline-candidate-order 0
```

## Inputs

- `--family`: Source family. Initial supported values: `sweep`, `session-tuning-sweep`.
- `--label`: Human-readable report label.
- `--ranking`: Required ranking JSON artifact.
- `--plan`: Optional plan JSON artifact.
- `--results`: Optional JSONL result artifact.
- `--summary`: Optional summary JSON artifact.
- `--out`: Required canonical JSON output path.
- `--markdown-out`: Optional readable Markdown output path.
- `--baseline-candidate-order`: Optional candidate order that represents baseline/current behavior. Defaults to `0`.

## JSON Output Requirements

The report MUST include:

- `schema_version`
- `source`
- `recommendation`
- `objectives`
- `candidates`
- `chart_datasets`
- `provenance`
- `markdown`

## Exit Codes

- `0`: Report generated and a recommendation status was produced.
- `2`: Inputs are missing, malformed, or contain no rankable candidates.
