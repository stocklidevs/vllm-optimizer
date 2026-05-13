# Quickstart: Repeated Sweep Stability

Generate the narrowed top-two repeated plan:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-top2-repeated.json --out artifacts/sweeps/qwen-top2-repeated/plan.json
```

Preview without contacting the GX10:

```powershell
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-top2-repeated/plan.json --out artifacts/sweeps/qwen-top2-repeated/preview.json
```

Run the live repeated sweep:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-top2-repeated/plan.json --out artifacts/sweeps/qwen-top2-repeated/live --timeout-seconds 1200 --continue-on-failure
```

Review aggregate rankings:

```powershell
Get-Content artifacts/sweeps/qwen-top2-repeated/live/ranking.json
```
