# Quickstart: Expanded Qwen Sweep

Generate and preview locally:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-expanded-safe.json --out artifacts/sweeps/qwen-expanded-safe/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-expanded-safe/plan.json --out artifacts/sweeps/qwen-expanded-safe/preview.json
```

Run live only after reviewing the preview:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-expanded-safe/plan.json --out artifacts/sweeps/qwen-expanded-safe/live --timeout-seconds 1200 --continue-on-failure
```

Generate a comparison report after live ranking exists:

```powershell
uv run vllm-optimizer report --baseline artifacts/benchmarks/qwen-baseline/summary.json --repeated-ranking artifacts/sweeps/qwen-expanded-safe/live/ranking.json --out artifacts/reports/qwen-expanded-comparison.json --markdown-out artifacts/reports/qwen-expanded-comparison.md
```
