# Quickstart: Multi-Model Registry and Smoke Workflow

## Inspect the Maintained Baselines

Read `docs/PROJECT_STATUS.md` and review the "Model Baseline Tracker" section.

## Preview a New Model Smoke Check

After implementation, the intended dry-run path is:

```powershell
uv run vllm-optimizer model-catalog --catalog config/model-catalog.json
uv run vllm-optimizer model-smoke-plan --model gemma-4-e4b-it --catalog config/model-catalog.json --out artifacts/models/gemma-4-e4b-it/smoke-plan.json
```

## Run a Live Smoke Check

Live execution remains gated and session-scoped:

```powershell
uv run vllm-optimizer model-smoke-run --model gemma-4-e4b-it --catalog config/model-catalog.json --config config/local.gx10.json --out artifacts/models/gemma-4-e4b-it/live --confirm-live-run
```

## Interpret Status

- `measured`: the model has local GX10 performance artifacts.
- `recipe-captured`: the serve recipe exists but performance is not measured.
- `candidate`: upstream model is validated, local smoke is pending.
- `deferred`: not part of local vLLM smoke execution.
