# Quickstart: Risky Session Knobs

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-risky-session-small.json --out artifacts/sweeps/qwen-risky-session-small/plan.json --allow-risky-session-flags
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-risky-session-small/plan.json --out artifacts/sweeps/qwen-risky-session-small/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-risky-session-small/plan.json --out artifacts/sweeps/qwen-risky-session-small/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```
