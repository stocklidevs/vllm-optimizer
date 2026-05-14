# CLI Contract: Recommended Profile Benchmark

## Generate benchmark plan

```powershell
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-recommended/plan.json
```

Expected behavior:
- Local-only dry-run plan.
- Uses existing prompt set and recommended profile.
- Starts no remote process.

## Run live benchmark

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-recommended --timeout-seconds 1200
```

Expected behavior:
- Uses existing managed benchmark lifecycle.
- Writes summary, metrics, responses, server log, cleanup, redaction, prompts,
  and plan artifacts.

## Generate default decision report

```powershell
uv run vllm-optimizer recommended-report --baseline artifacts/benchmarks/qwen-baseline/summary.json --recommended artifacts/benchmarks/qwen-recommended/summary.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --source-ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --out artifacts/reports/qwen-recommended-default.json --markdown-out artifacts/reports/qwen-recommended-default.md
```

Expected behavior:
- Local-only report generation.
- Fails before writing output if required inputs are missing or malformed.
- Includes keep/reject/inconclusive decision and provenance.
