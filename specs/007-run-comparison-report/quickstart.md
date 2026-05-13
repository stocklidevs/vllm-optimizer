# Quickstart: Run Comparison Report

Generate a comparison report from current artifacts:

```powershell
uv run vllm-optimizer report --baseline artifacts/benchmarks/qwen-baseline/summary.json --sweep-ranking artifacts/sweeps/qwen-small/live/ranking.json --repeated-ranking artifacts/sweeps/qwen-top2-repeated/live/ranking.json --out artifacts/reports/qwen-comparison.json --markdown-out artifacts/reports/qwen-comparison.md
```

Generate a report from only the repeated ranking:

```powershell
uv run vllm-optimizer report --repeated-ranking artifacts/sweeps/qwen-top2-repeated/live/ranking.json --out artifacts/reports/qwen-repeated-only.json
```
