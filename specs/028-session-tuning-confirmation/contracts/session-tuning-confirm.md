# Contract: `session-tuning-confirm`

## Command

```powershell
uv run vllm-optimizer session-tuning-confirm `
  --config config/local.gx10.json `
  --profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json `
  --prompts config/prompts/qwen-coding-interactive-concurrency-8.json `
  --session-tuning config/session-tuning/qwen-runtime-env.json `
  --allow-session-tuning `
  --repetitions 5 `
  --current-label current-c8 `
  --tuned-label runtime-env `
  --out artifacts/session-tuning/qwen-runtime-env-confirmation `
  --timeout-seconds 1200
```

## Output Contract

- `current-r1/summary.json` through `current-rN/summary.json`
- `tuned-r1/summary.json` through `tuned-rN/summary.json`
- `confirmation-report.json`
- `confirmation-report.md`
- `summary.json`

## Safety Contract

- Requires `--allow-session-tuning`.
- Applies session tuning only to tuned repetitions.
- Does not promote profiles or persist system changes.
