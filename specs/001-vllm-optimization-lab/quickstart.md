# Quickstart: vLLM Optimization Lab

This quickstart demonstrates the first useful increment without GX10 access.

## 1. Install development dependencies

```powershell
uv sync
```

## 2. Generate a deterministic plan

```powershell
uv run vllm-optimizer plan --experiment tests/fixtures/experiments/throughput.json --out artifacts/demo/trial-plan.json
```

Expected result:
- `artifacts/demo/trial-plan.json` exists.
- Running the command again produces the same trial ids in the same order.

## 3. Preview remote actions

```powershell
uv run vllm-optimizer dry-run --plan artifacts/demo/trial-plan.json --out artifacts/demo/dry-run.json --allow-blocked-preview
```

Expected result:
- `artifacts/demo/dry-run.json` lists planned probe, lifecycle, benchmark,
  artifact, and cleanup actions.
- No SSH connection is opened.

## 4. Rank fixture results

```powershell
uv run vllm-optimizer rank --plan artifacts/demo/trial-plan.json --results tests/fixtures/results/throughput.jsonl --out artifacts/demo/report.json
```

Expected result:
- `artifacts/demo/report.json` ranks valid trials for the throughput objective.
- Invalid or missing trial results are listed with exclusion reasons.

## 5. Run tests

```powershell
uv run pytest
```
