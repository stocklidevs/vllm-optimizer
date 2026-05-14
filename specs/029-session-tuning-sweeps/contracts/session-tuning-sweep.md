# Contract: Session Tuning Sweep

## Plan

```powershell
uv run vllm-optimizer session-tuning-sweep-plan `
  --sweep config/session-tuning-sweeps/qwen-runtime-env-sweep.json `
  --out artifacts/session-tuning-sweeps/qwen-runtime-env/plan.json
```

## Preview

```powershell
uv run vllm-optimizer session-tuning-sweep-preview `
  --plan artifacts/session-tuning-sweeps/qwen-runtime-env/plan.json `
  --out artifacts/session-tuning-sweeps/qwen-runtime-env/preview.json
```

## Output Contract

- Plan contains `candidates`, `trials`, `profile_path`, `prompts_path`, and `repetitions`.
- Every trial includes a session tuning preview and benchmark plan.
- Preview contains `blocked`, `blocked_reasons`, and non-executing trial summaries.
