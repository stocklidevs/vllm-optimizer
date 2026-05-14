# Contract: Session Tuning

## Preview

```powershell
uv run vllm-optimizer session-tuning-preview `
  --profile config/session-tuning/qwen-runtime-env.json `
  --catalog artifacts/system-tuning/gx10-live/catalog.json `
  --out artifacts/session-tuning/qwen-runtime-env/preview.json
```

## Benchmark Plan

```powershell
uv run vllm-optimizer benchmark-plan `
  --profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json `
  --prompts config/prompts/qwen-coding-interactive-concurrency-8.json `
  --session-tuning config/session-tuning/qwen-runtime-env.json `
  --allow-session-tuning `
  --out artifacts/benchmarks/tuned/plan.json
```

## Safety Rules

- Allowed: shell environment exports and `ulimit -n`.
- Rejected: persistent files, sysctl writes, CPU governor writes, THP writes, NVIDIA power/clock writes.
- Live benchmark execution requires `--allow-session-tuning`.
