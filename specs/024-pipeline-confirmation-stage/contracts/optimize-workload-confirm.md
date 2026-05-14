# Contract: optimize-workload confirm

```powershell
uv run vllm-optimizer optimize-workload --mode confirm --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/optimizer-runs/qwen-c8 --current-profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --prompts config/prompts/qwen-coding-interactive-concurrency-8.json --candidate-profile-out config/profiles/qwen3-coder-next-awq-concurrent-candidate.json --confirmed-profile-out config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --original-label current --recommended-label candidate --confirmation-repetitions 5 --allow-promotion
```

## Inputs

- `--mode confirm`
- `--sweep`
- `--out`
- `--current-profile`
- `--prompts`
- `--candidate-profile-out`
- `--confirmed-profile-out`
- `--original-label`
- `--recommended-label`
- `--confirmation-repetitions`
- `--allow-promotion`

## Expected Existing Artifacts

- Pipeline ranking at `<out>/live/ranking.json`
- Original summaries under `<out>/confirmation/current-r*/summary.json`
- Recommended summaries under `<out>/confirmation/candidate-r*/summary.json`

## Outputs

- Candidate profile
- `<out>/confirmation/confirmation-report.json`
- `<out>/confirmation/confirmation-report.md`
- Confirmed profile and promotion summary only when promotion is explicitly allowed and approved
