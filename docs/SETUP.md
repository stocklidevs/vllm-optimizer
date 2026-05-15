# vLLM Optimizer Setup Guide

This guide covers local setup, safe verification, and the first commands to run
before connecting to the GX10.

## Local Environment

Requirements:

- Python 3.11 or newer
- `uv`
- Git
- Tailscale SSH access for live GX10 runs

Install and verify locally:

```powershell
uv sync
uv run vllm-optimizer --version
uv run pytest
```

Generate release metadata without touching the GX10:

```powershell
uv run vllm-optimizer artifact-contracts --out artifacts/catalog/artifact-contracts.json --markdown-out artifacts/catalog/artifact-contracts.md
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

## GX10 Local Config

Live runs expect a local, ignored target config such as `config/local.gx10.json`.
Keep credentials and host-specific paths out of committed files.

The current GX10 target has used:

```text
altsens@100.84.106.41
```

The Qwen profile expects the remote vLLM executable path recorded in the profile
configuration. If that path changes, update the local profile or config before
running live sweeps.

## Safe First Workflow

Start with local planning and previews:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-prefix-prefill-tool-json.json --out artifacts/sweeps/qwen-prefix-prefill-tool-json/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-prefix-prefill-tool-json/plan.json --out artifacts/sweeps/qwen-prefix-prefill-tool-json/preview.json
```

For risky-session sweeps, keep the explicit gate visible:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-kv-cache-memory-tradeoff.json --out artifacts/sweeps/qwen-kv-cache-memory-tradeoff/plan.json --allow-risky-session-flags
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-kv-cache-memory-tradeoff/plan.json --out artifacts/sweeps/qwen-kv-cache-memory-tradeoff/preview.json --allow-risky-session-flags
```

Run live only after the preview looks right:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-prefix-prefill-tool-json/plan.json --out artifacts/sweeps/qwen-prefix-prefill-tool-json/live --timeout-seconds 1200 --continue-on-failure
```

Promotion stays gated. Use `--allow-promotion` only after repeated confirmation
supports the change and you intentionally want to write the promoted profile.

## Reporting

The deterministic reporting path is:

```powershell
uv run vllm-optimizer canonical-report --family sweep --label qwen-prefix-prefill-tool-json --ranking artifacts/sweeps/qwen-prefix-prefill-tool-json/live/ranking.json --out artifacts/reports/qwen-prefix-prefill-tool-json/canonical-report.json --markdown-out artifacts/reports/qwen-prefix-prefill-tool-json/report.md
uv run vllm-optimizer report-viewer --report artifacts/reports/qwen-prefix-prefill-tool-json/canonical-report.json --out artifacts/reports/qwen-prefix-prefill-tool-json/viewer.html
```

The CLI artifacts remain the source of truth. Web views and future controllers
should consume those artifacts rather than recomputing optimizer decisions.
