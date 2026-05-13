# Quickstart: Qwen Smoke Serve

## Dry-run plan

```powershell
uv run vllm-optimizer smoke-serve-plan --profile config/profiles/qwen3-coder-next-awq.json --out artifacts/smoke/qwen/plan.json
```

## Live smoke

```powershell
uv run vllm-optimizer smoke-serve --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --out artifacts/smoke/qwen --timeout-seconds 900
```

## Tests

```powershell
uv run pytest
```
