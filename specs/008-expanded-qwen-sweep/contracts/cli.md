# CLI Contract: Expanded Qwen Sweep

This feature uses existing commands:

## Plan

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-expanded-safe.json --out artifacts/sweeps/qwen-expanded-safe/plan.json
```

Expected:
- `candidate_count` is 6.
- `trial_count` is 18.
- `repetitions` is 3.

## Preview

```powershell
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-expanded-safe/plan.json --out artifacts/sweeps/qwen-expanded-safe/preview.json
```

Expected:
- `blocked` is false.
- `will_execute` is false.

## Optional Live Run

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-expanded-safe/plan.json --out artifacts/sweeps/qwen-expanded-safe/live --timeout-seconds 1200 --continue-on-failure
```
