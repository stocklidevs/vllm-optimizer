# Contract: saturation-report

Generate a local report from ranked sweep artifacts labeled by concurrency level.

```powershell
uv run vllm-optimizer saturation-report --ranking 1=artifacts/sweeps/qwen-concurrency-saturation-c1/live/ranking.json 2=artifacts/sweeps/qwen-concurrency-saturation-c2/live/ranking.json --out artifacts/reports/qwen-concurrency-saturation.json --markdown-out artifacts/reports/qwen-concurrency-saturation.md
```

## Inputs

- `--ranking`: One or more `CONCURRENCY=PATH` pairs.
- `--out`: JSON output path.
- `--markdown-out`: Optional Markdown output path.

## JSON Output

- `generated_at`
- `levels`
- `recommendation`
- `next_actions`
- `markdown`

## Errors

- No rankings provided.
- Malformed concurrency label.
- Missing ranking path.
- Ranking lacks balanced objective rows.
