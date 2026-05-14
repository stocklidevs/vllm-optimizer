# Contract: `optimize-workload --mode full`

## Command

```powershell
uv run vllm-optimizer optimize-workload `
  --mode full `
  --sweep config/sweeps/qwen-concurrency-saturation-c8.json `
  --out artifacts/optimizer-runs/qwen-c8-full `
  --config config/local.gx10.json `
  --current-profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json `
  --prompts config/prompts/qwen-coding-interactive-concurrency-8.json `
  --candidate-profile-out artifacts/optimizer-runs/qwen-c8-full/candidate-profile.json `
  --confirmed-profile-out artifacts/optimizer-runs/qwen-c8-full/confirmed-profile.json `
  --confirmation-repetitions 5 `
  --original-label current-concurrent `
  --recommended-label candidate `
  --continue-on-failure `
  --allow-risky-session-flags
```

## Required Inputs

- `--sweep`
- `--out`
- `--config`
- `--current-profile`
- `--prompts`
- `--candidate-profile-out`
- `--confirmed-profile-out`

## Optional Inputs

- `--confirmation-repetitions`, default `3`
- `--original-label`, default `current`
- `--recommended-label`, default `candidate`
- `--allow-promotion`, default disabled
- Existing run safety controls such as `--continue-on-failure`, `--timeout-seconds`, and `--allow-risky-session-flags`

## Output Contract

- `pipeline-summary.json` includes completed stages:
  - `plan`
  - `preview`
  - `run`
  - `report`
  - `confirmation-benchmarks`
  - `confirm`
- `confirmation/current-rN/summary.json` exists for each repetition.
- `confirmation/candidate-rN/summary.json` exists for each repetition.
- `confirmation/confirmation-report.json` exists after confirmation.
- Candidate profile is written before candidate confirmation benchmarks.
- Confirmed profile is written only when `--allow-promotion` is passed and the decision is `switch-to-recommended`.
