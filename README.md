# vLLM Optimizer

[![version](https://img.shields.io/badge/version-0.13.0-blue.svg)](pyproject.toml)
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
- Deterministic small Qwen parameter sweeps with dry-run previews and local
  ranking for throughput, latency, and balanced objectives.
- Repeated top-two sweep stability analysis with per-candidate aggregates,
  spread metrics, baseline deltas, and stability-aware rankings.
- Local comparison reports that summarize baseline, sweep, and repeated sweep
  artifacts into JSON and Markdown recommendations.
- Expanded safe Qwen sweep configuration for testing nearby GPU utilization
  and performance-mode candidates around the current winner.
- Read-only vLLM flag discovery and safe performance knob cataloging from the
  installed GX10 vLLM help output.
- Scheduler and prefill knob sweep support for approved vLLM serve flags such
  as batched tokens, sequence count, chunked prefill, and prefix caching.
- Local promotion of ranked sweep winners into reusable recommended serve
  profiles with provenance.
- Recommended-profile benchmark validation with a default decision report.
- Repeated A/B confirmation reports for original vs recommended profiles.
- Risk-tiered risky-session vLLM sweeps with explicit preview/run opt-in.
- Guarded risky-winner promotion that requires repeated A/B confirmation before
  the default recommended profile is updated.
- Workload-aware prompt sets and explicit high-impact sweep candidates for
  interactive coding, long coding, and tool/JSON workloads.

Persistent Linux/NVIDIA tuning is intentionally not implemented yet. It will be
handled by separate specs with explicit safety gates.

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
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-small-sweep.json --out artifacts/sweeps/qwen-small/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-small/plan.json --out artifacts/sweeps/qwen-small/preview.json
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

Parameter sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-small-sweep.json --out artifacts/sweeps/qwen-small/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-small/plan.json --out artifacts/sweeps/qwen-small/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-small/plan.json --out artifacts/sweeps/qwen-small/live --timeout-seconds 1200 --continue-on-failure
```

Repeated top-two stability sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-top2-repeated.json --out artifacts/sweeps/qwen-top2-repeated/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-top2-repeated/plan.json --out artifacts/sweeps/qwen-top2-repeated/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-top2-repeated/plan.json --out artifacts/sweeps/qwen-top2-repeated/live --timeout-seconds 1200 --continue-on-failure
```

Expanded safe Qwen sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-expanded-safe.json --out artifacts/sweeps/qwen-expanded-safe/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-expanded-safe/plan.json --out artifacts/sweeps/qwen-expanded-safe/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-expanded-safe/plan.json --out artifacts/sweeps/qwen-expanded-safe/live --timeout-seconds 1200 --continue-on-failure
```

Scheduler knob sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-scheduler-safe.json --out artifacts/sweeps/qwen-scheduler-safe/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-scheduler-safe/plan.json --out artifacts/sweeps/qwen-scheduler-safe/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-scheduler-safe/plan.json --out artifacts/sweeps/qwen-scheduler-safe/live --timeout-seconds 1200 --continue-on-failure
```

Latest GX10 scheduler sweep result:

```text
Best balanced candidate: gpu_memory_utilization=0.90, max_model_len=32768,
max_num_batched_tokens=4096, max_num_seqs=16, enable_chunked_prefill=true,
enable_prefix_caching=false, performance_mode=interactivity

Mean latency: 1004.0 ms
Throughput: 48.16 tokens/sec
Failures: 0/3 repetitions
```

Rank completed or fixture sweep results:

```powershell
uv run vllm-optimizer sweep-rank --plan artifacts/sweeps/qwen-small/plan.json --results artifacts/sweeps/qwen-small/live/results.jsonl --out artifacts/sweeps/qwen-small/ranking.json
```

Comparison report:

```powershell
uv run vllm-optimizer report --baseline artifacts/benchmarks/qwen-baseline/summary.json --sweep-ranking artifacts/sweeps/qwen-small/live/ranking.json --repeated-ranking artifacts/sweeps/qwen-top2-repeated/live/ranking.json --out artifacts/reports/qwen-comparison.json --markdown-out artifacts/reports/qwen-comparison.md
```

vLLM flag catalog:

```powershell
uv run vllm-optimizer flag-catalog --policy config/vllm-flags/qwen-safe-policy.json --help-file tests/fixtures/vllm/serve-help.txt --out artifacts/vllm-flags/fixture/catalog.json
uv run vllm-optimizer flag-catalog-capture --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --policy config/vllm-flags/qwen-safe-policy.json --out artifacts/vllm-flags/gx10-qwen --executor ssh
```

Promote a ranked winner to a recommended profile:

```powershell
uv run vllm-optimizer promote-preview --ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --objective balanced --out artifacts/promotions/qwen-scheduler-safe-preview.json
uv run vllm-optimizer promote-profile --ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-recommended.json --summary-out artifacts/promotions/qwen3-coder-next-awq-recommended.md
uv run vllm-optimizer serve-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --out artifacts/promotions/recommended-serve-plan.json
```

Validate the recommended profile as a default candidate:

```powershell
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-recommended/plan.json
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-recommended --timeout-seconds 1200
uv run vllm-optimizer recommended-report --baseline artifacts/benchmarks/qwen-baseline/summary.json --recommended artifacts/benchmarks/qwen-recommended/summary.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --source-ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --out artifacts/reports/qwen-recommended-default.json --markdown-out artifacts/reports/qwen-recommended-default.md
```

Repeated A/B confirmation:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r3 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r3 --timeout-seconds 1200
uv run vllm-optimizer ab-report --original-label original --recommended-label recommended --original-summaries artifacts/benchmarks/qwen-ab/original-r1/summary.json artifacts/benchmarks/qwen-ab/original-r2/summary.json artifacts/benchmarks/qwen-ab/original-r3/summary.json --recommended-summaries artifacts/benchmarks/qwen-ab/recommended-r1/summary.json artifacts/benchmarks/qwen-ab/recommended-r2/summary.json artifacts/benchmarks/qwen-ab/recommended-r3/summary.json --prompt-set-id qwen-baseline-v1 --out artifacts/reports/qwen-ab-confirmation.json --markdown-out artifacts/reports/qwen-ab-confirmation.md
```

Risky-session knob sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-risky-session-small.json --out artifacts/sweeps/qwen-risky-session-small/plan.json --allow-risky-session-flags
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-risky-session-small/plan.json --out artifacts/sweeps/qwen-risky-session-small/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-risky-session-small/plan.json --out artifacts/sweeps/qwen-risky-session-small/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Risky winner confirmation and guarded promotion:

```powershell
uv run vllm-optimizer promote-profile --ranking artifacts/sweeps/qwen-risky-session-small/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-risky-winner.json --summary-out artifacts/promotions/qwen3-coder-next-awq-risky-winner.md --profile-id qwen3-coder-next-awq-risky-winner
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r3 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r3 --timeout-seconds 1200
uv run vllm-optimizer ab-report --original-label current-recommended --recommended-label risky-winner --original-summaries artifacts/benchmarks/qwen-risky-ab/current-r1/summary.json artifacts/benchmarks/qwen-risky-ab/current-r2/summary.json artifacts/benchmarks/qwen-risky-ab/current-r3/summary.json --recommended-summaries artifacts/benchmarks/qwen-risky-ab/risky-r1/summary.json artifacts/benchmarks/qwen-risky-ab/risky-r2/summary.json artifacts/benchmarks/qwen-risky-ab/risky-r3/summary.json --prompt-set-id qwen-baseline-v1 --out artifacts/reports/qwen-risky-winner-confirmation.json --markdown-out artifacts/reports/qwen-risky-winner-confirmation.md
uv run vllm-optimizer promote-confirmed-profile --confirmation-report artifacts/reports/qwen-risky-winner-confirmation.json --ranking artifacts/sweeps/qwen-risky-session-small/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-recommended.json --summary-out artifacts/promotions/qwen3-coder-next-awq-recommended-risky-confirmed.md --profile-id qwen3-coder-next-awq-recommended --expected-recommended-label risky-winner --force
```

Latest GX10 risky winner confirmation:

```text
Decision: switch-to-recommended
Current recommended mean latency: 1008.444 ms
Risky winner mean latency: 992.667 ms
Latency delta: -15.778 ms (-1.565%)
Current recommended throughput: 47.948 tokens/sec
Risky winner throughput: 48.717 tokens/sec
Throughput delta: +0.770 tokens/sec (+1.605%)
Failures: 0/9 requests for each profile
Confirmed default flag addition: block_size=16
```

Workload-aware high-impact sweeps:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-interactive.json --out artifacts/sweeps/qwen-high-impact-interactive/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-interactive/plan.json --out artifacts/sweeps/qwen-high-impact-interactive/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-long.json --out artifacts/sweeps/qwen-high-impact-long/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-long/plan.json --out artifacts/sweeps/qwen-high-impact-long/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-tool-json.json --out artifacts/sweeps/qwen-high-impact-tool-json/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-tool-json/plan.json --out artifacts/sweeps/qwen-high-impact-tool-json/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-high-impact-interactive/plan.json --out artifacts/sweeps/qwen-high-impact-interactive/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

## Safety

- Local secrets belong in ignored files such as `config/local.gx10.json`.
- Live SSH commands use batch-mode authentication.
- Discovery probes are read-only.
- Smoke and benchmark commands are session-mutating and include preflight
  checks plus cleanup verification.
- Sweep live execution is sequential and session-mutating only.
- Promotion commands are local-only and do not contact the GX10.
- Confirmed promotion refuses to update the default profile unless the repeated
  A/B report approves switching to the candidate.
- Risky-session sweeps are blocked by default and require explicit preview/run
  opt-in; persistent/system flags remain blocked.
- Generated artifacts under `artifacts/` are ignored by git.

## SpecKit

Project governance and feature design live under `.specify/` and `specs/`.
Current feature specs:

- `specs/001-vllm-optimization-lab/spec.md`
- `specs/002-gx10-readonly-discovery/spec.md`
- `specs/003-qwen-smoke-serve/spec.md`
- `specs/004-qwen-baseline-benchmark/spec.md`
- `specs/005-qwen-parameter-sweep/spec.md`
- `specs/006-repeated-sweep-stability/spec.md`
- `specs/007-run-comparison-report/spec.md`
- `specs/008-expanded-qwen-sweep/spec.md`
- `specs/009-vllm-flag-catalog/spec.md`
- `specs/010-scheduler-knob-sweep/spec.md`
- `specs/011-promote-winner-profile/spec.md`
- `specs/012-recommended-profile-benchmark/spec.md`
- `specs/013-ab-benchmark-confirmation/spec.md`
- `specs/014-risky-session-knobs/spec.md`
- `specs/015-risky-winner-confirmation/spec.md`
- `specs/016-workload-aware-sweeps/spec.md`
