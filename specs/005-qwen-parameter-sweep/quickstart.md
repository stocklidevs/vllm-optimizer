# Quickstart: Qwen Parameter Sweep

Generate a local sweep plan:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-small-sweep.json --out artifacts/sweeps/qwen-small/plan.json
```

Preview the sweep without contacting the GX10:

```powershell
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-small/plan.json --out artifacts/sweeps/qwen-small/preview.json
```

Rank fixture or completed results:

```powershell
uv run vllm-optimizer sweep-rank --plan artifacts/sweeps/qwen-small/plan.json --results artifacts/sweeps/qwen-small/results.jsonl --out artifacts/sweeps/qwen-small/ranking.json
```

Run the live sweep only after the preview is reviewed:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-small/plan.json --out artifacts/sweeps/qwen-small/live --timeout-seconds 1200 --continue-on-failure
```
