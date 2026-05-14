# Quickstart: Concurrency Saturation

Generate plans and previews:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-concurrency-saturation-c1.json --out artifacts/sweeps/qwen-concurrency-saturation-c1/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-concurrency-saturation-c1/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c1/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-concurrency-saturation-c2.json --out artifacts/sweeps/qwen-concurrency-saturation-c2/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-concurrency-saturation-c2/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c2/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-concurrency-saturation-c3.json --out artifacts/sweeps/qwen-concurrency-saturation-c3/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-concurrency-saturation-c3/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c3/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-concurrency-saturation-c4.json --out artifacts/sweeps/qwen-concurrency-saturation-c4/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-concurrency-saturation-c4/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c4/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-concurrency-saturation-c6.json --out artifacts/sweeps/qwen-concurrency-saturation-c6/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-concurrency-saturation-c6/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c6/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/sweeps/qwen-concurrency-saturation-c8/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-concurrency-saturation-c8/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c8/preview.json
```

Run a live level when ready:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-concurrency-saturation-c4/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c4/live --timeout-seconds 1200 --continue-on-failure
```

Generate the saturation report after rankings exist:

```powershell
uv run vllm-optimizer saturation-report --ranking 1=artifacts/sweeps/qwen-concurrency-saturation-c1/live/ranking.json 2=artifacts/sweeps/qwen-concurrency-saturation-c2/live/ranking.json 3=artifacts/sweeps/qwen-concurrency-saturation-c3/live/ranking.json 4=artifacts/sweeps/qwen-concurrency-saturation-c4/live/ranking.json 6=artifacts/sweeps/qwen-concurrency-saturation-c6/live/ranking.json 8=artifacts/sweeps/qwen-concurrency-saturation-c8/live/ranking.json --out artifacts/reports/qwen-concurrency-saturation.json --markdown-out artifacts/reports/qwen-concurrency-saturation.md
```
