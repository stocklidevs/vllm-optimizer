# Contract: optimize-workload

```powershell
uv run vllm-optimizer optimize-workload --mode preview --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/optimizer-runs/qwen-c8
```

## Arguments

- `--mode`: one of `plan`, `preview`, `run`, `report`
- `--sweep`: sweep definition path
- `--out`: pipeline output directory
- `--config`: remote config path, required for `run`
- `--timeout-seconds`: live run timeout, default `1200`
- `--continue-on-failure`: pass-through for live sweep run
- `--allow-risky-session-flags`: explicit risky-session allowance

## Outputs

- Always writes `pipeline-plan.json`.
- Writes `pipeline-summary.json` for completed stages.
- Preview mode writes `sweep-plan.json` and `sweep-preview.json`.
- Run mode writes live artifacts under `live/`.
- Report mode writes `report.json` and `report.md`.

## Non-Goals

- No automatic profile promotion.
- No multi-sweep search policy generation.
- No persistent Linux/NVIDIA tuning.
