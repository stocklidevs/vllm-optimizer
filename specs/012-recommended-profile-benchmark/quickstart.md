# Quickstart: Recommended Profile Benchmark

Plan the recommended profile benchmark:

```powershell
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-recommended/plan.json
```

Run the recommended profile benchmark on the GX10:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-recommended --timeout-seconds 1200
```

Generate the default decision report:

```powershell
uv run vllm-optimizer recommended-report --baseline artifacts/benchmarks/qwen-baseline/summary.json --recommended artifacts/benchmarks/qwen-recommended/summary.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --source-ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --out artifacts/reports/qwen-recommended-default.json --markdown-out artifacts/reports/qwen-recommended-default.md
```
