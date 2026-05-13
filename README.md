# vLLM Optimizer

[![version](https://img.shields.io/badge/version-0.2.0-blue.svg)](pyproject.toml)
[![python](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](pyproject.toml)
[![tests](https://img.shields.io/badge/tests-pytest-green.svg)](tests)
[![SpecKit](https://img.shields.io/badge/SpecKit-enabled-purple.svg)](.specify)

Deterministic optimization lab for vLLM experiments on a remote GX10.

The project is spec-driven with SpecKit and currently supports:

- Deterministic trial-plan generation from JSON experiment definitions.
- Dry-run remote action previews.
- Read-only GX10 discovery over SSH.
- Qwen3 Coder Next serve-profile rendering.
- Safe smoke serve lifecycle with preflight checks, readiness polling, one
  request, artifact capture, and cleanup.
- A small Qwen baseline benchmark with fixed prompts and summary metrics.

Persistent Linux/NVIDIA tuning and parameter optimization are intentionally not
implemented yet. Those will be separate specs with explicit safety gates.

## Quickstart

```powershell
uv sync
uv run vllm-optimizer --version
uv run pytest
```

## Local Demo

```powershell
uv run vllm-optimizer plan --experiment tests/fixtures/experiments/throughput.json --out artifacts/demo/trial-plan.json
uv run vllm-optimizer dry-run --plan artifacts/demo/trial-plan.json --out artifacts/demo/dry-run.json --allow-blocked-preview
uv run vllm-optimizer rank --plan artifacts/demo/trial-plan.json --results tests/fixtures/results/throughput.jsonl --out artifacts/demo/report.json
uv run vllm-optimizer discover --config tests/fixtures/discovery/local.gx10.mock.json --executor mock --mock-results tests/fixtures/discovery/mock_outputs.json --out artifacts/discovery/mock
uv run vllm-optimizer serve-plan --profile config/profiles/qwen3-coder-next-awq.json --out artifacts/demo/qwen-serve-plan.json
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-baseline/plan.json
```

## GX10 Workflows

Create an ignored local config from the example and set the real SSH
destination/redaction values:

```powershell
Copy-Item config/gx10.example.json config/local.gx10.json
```

Read-only discovery:

```powershell
uv run vllm-optimizer discover --config config/local.gx10.json --executor ssh --out artifacts/discovery/gx10-live
```

Smoke serve:

```powershell
uv run vllm-optimizer smoke-serve-plan --profile config/profiles/qwen3-coder-next-awq.json --out artifacts/smoke/qwen/plan.json
uv run vllm-optimizer smoke-serve --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --out artifacts/smoke/qwen --timeout-seconds 1200
```

Baseline benchmark:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-baseline --timeout-seconds 1200
```

## Safety

- Local secrets belong in ignored files such as `config/local.gx10.json`.
- Live SSH commands use batch-mode authentication.
- Discovery probes are read-only.
- Smoke and benchmark commands are session-mutating and include preflight
  checks plus cleanup verification.
- Generated artifacts under `artifacts/` are ignored by git.

## SpecKit

Project governance and feature design live under `.specify/` and `specs/`.
Current feature specs:

- `specs/001-vllm-optimization-lab/spec.md`
- `specs/002-gx10-readonly-discovery/spec.md`
- `specs/003-qwen-smoke-serve/spec.md`
- `specs/004-qwen-baseline-benchmark/spec.md`
