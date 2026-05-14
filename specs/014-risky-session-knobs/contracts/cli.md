# CLI Contract: Risky Session Knobs

## Plan risky-session sweep

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-risky-session-small.json --out artifacts/sweeps/qwen-risky-session-small/plan.json
```

## Preview with explicit allowance

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-risky-session-small.json --out artifacts/sweeps/qwen-risky-session-small/plan.json --allow-risky-session-flags
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-risky-session-small/plan.json --out artifacts/sweeps/qwen-risky-session-small/preview.json
```

## Run live with explicit allowance

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-risky-session-small/plan.json --out artifacts/sweeps/qwen-risky-session-small/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Expected behavior:
- Preview is blocked unless risky allowance is recorded in the plan.
- Live run refuses risky plans unless `--allow-risky-session-flags` is supplied.
- Unknown or blocked flags are rejected during sweep definition loading.
