# CLI Contract: Promote Winner Profile

## Preview promotion

```powershell
uv run vllm-optimizer promote-preview --ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --objective balanced --out artifacts/promotions/qwen-scheduler-safe-preview.json
```

Expected behavior:
- Reads a local ranking artifact only.
- Selects the top candidate for the requested objective.
- Writes a JSON preview with eligibility, metrics, proposed profile, and
  provenance.
- Exits non-zero when the objective or selected candidate cannot be promoted.

## Generate recommended profile

```powershell
uv run vllm-optimizer promote-profile --ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-recommended.json --summary-out artifacts/promotions/qwen3-coder-next-awq-recommended.md
```

Expected behavior:
- Refuses to overwrite existing outputs unless `--force` is supplied.
- Writes a recommended profile JSON and Markdown summary.
- Performs no GX10 SSH action and starts no vLLM process.

## Options

- `--ranking <path>`: Required ranking artifact.
- `--objective <name>`: Objective to promote. Defaults to `balanced`.
- `--out <path>`: Preview JSON path for `promote-preview`.
- `--profile-out <path>`: Recommended profile JSON path for `promote-profile`.
- `--summary-out <path>`: Markdown summary path for `promote-profile`.
- `--profile-id <id>`: Optional generated profile id.
- `--force`: Allow replacing existing outputs.
