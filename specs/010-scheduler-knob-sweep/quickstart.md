# Quickstart: Scheduler Knob Sweep

Generate and preview locally:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-scheduler-safe.json --out artifacts/sweeps/qwen-scheduler-safe/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-scheduler-safe/plan.json --out artifacts/sweeps/qwen-scheduler-safe/preview.json
```

Run live after preview review:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-scheduler-safe/plan.json --out artifacts/sweeps/qwen-scheduler-safe/live --timeout-seconds 1200 --continue-on-failure
```
