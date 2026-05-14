# CLI Contract: Scheduler Knob Sweep

Existing commands are used:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-scheduler-safe.json --out artifacts/sweeps/qwen-scheduler-safe/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-scheduler-safe/plan.json --out artifacts/sweeps/qwen-scheduler-safe/preview.json
```

Expected:
- Plan includes optional flags in trial profiles and command lines.
- Preview is local-only and unblocked.
- Unknown optional flags fail during plan generation.
