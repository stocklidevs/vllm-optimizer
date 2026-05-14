# CLI Contract: Workload-Aware Sweeps

## Generate Plans And Previews

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-interactive.json --out artifacts/sweeps/qwen-high-impact-interactive/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-interactive/plan.json --out artifacts/sweeps/qwen-high-impact-interactive/preview.json

uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-long.json --out artifacts/sweeps/qwen-high-impact-long/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-long/plan.json --out artifacts/sweeps/qwen-high-impact-long/preview.json

uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-tool-json.json --out artifacts/sweeps/qwen-high-impact-tool-json/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-tool-json/plan.json --out artifacts/sweeps/qwen-high-impact-tool-json/preview.json
```

## Run Live

Live runs remain explicit and session-mutating:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-high-impact-interactive/plan.json --out artifacts/sweeps/qwen-high-impact-interactive/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Repeat the live command for the long and tool/JSON plans after reviewing their previews.
