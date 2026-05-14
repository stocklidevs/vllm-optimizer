# Quickstart: Promote Winner Profile

Preview the current scheduler winner:

```powershell
uv run vllm-optimizer promote-preview --ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --objective balanced --out artifacts/promotions/qwen-scheduler-safe-preview.json
```

Generate a recommended profile:

```powershell
uv run vllm-optimizer promote-profile --ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-recommended.json --summary-out artifacts/promotions/qwen3-coder-next-awq-recommended.md
```

Use the recommended profile for a future serve plan:

```powershell
uv run vllm-optimizer serve-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --out artifacts/promotions/recommended-serve-plan.json
```
