# Contract: Session Tuning Sweep Run

## Run

```powershell
uv run vllm-optimizer session-tuning-sweep-run `
  --config config/local.gx10.json `
  --plan artifacts/session-tuning-sweeps/qwen-runtime-env/plan.json `
  --out artifacts/session-tuning-sweeps/qwen-runtime-env/live `
  --allow-session-tuning `
  --continue-on-failure `
  --timeout-seconds 1200
```

## Rank

```powershell
uv run vllm-optimizer session-tuning-sweep-rank `
  --plan artifacts/session-tuning-sweeps/qwen-runtime-env/plan.json `
  --results artifacts/session-tuning-sweeps/qwen-runtime-env/live/results.jsonl `
  --out artifacts/session-tuning-sweeps/qwen-runtime-env/live/ranking.json
```

## Output Contract

- Run writes `results.jsonl`.
- Each row includes `trial_id`, `candidate_id`, `session_tuning_profile_id`, `status`, `summary`, and `artifact_paths`.
- Rank writes objectives: `throughput`, `latency`, `balanced`.
