# vLLM Optimizer

Deterministic optimization lab for vLLM experiments.

The first increment is deliberately local and safe:

- Generate deterministic trial plans from JSON experiment definitions.
- Preview GX10 remote actions in dry-run mode without opening SSH.
- Rank fixture benchmark results for throughput and latency objectives.
- Preserve artifacts as JSON and JSONL files for inspection and future replay.

Live SSH execution and persistent Linux/NVIDIA tuning are intentionally out of
scope until the dry-run contracts, safety gates, and artifact model are proven.

## Quickstart

```powershell
uv sync
uv run vllm-optimizer plan --experiment tests/fixtures/experiments/throughput.json --out artifacts/demo/trial-plan.json
uv run vllm-optimizer dry-run --plan artifacts/demo/trial-plan.json --out artifacts/demo/dry-run.json --allow-blocked-preview
uv run vllm-optimizer rank --plan artifacts/demo/trial-plan.json --results tests/fixtures/results/throughput.jsonl --out artifacts/demo/report.json
uv run pytest
```

## SpecKit

Project governance and feature design live under `.specify/` and `specs/`.
Start with:

- `specs/001-vllm-optimization-lab/spec.md`
- `specs/001-vllm-optimization-lab/plan.md`
- `specs/001-vllm-optimization-lab/tasks.md`
