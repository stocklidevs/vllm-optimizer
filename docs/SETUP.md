# vLLM Optimizer Setup Guide

This guide covers public alpha setup, safe verification, and the first commands
to run before connecting to a live GX10.

## Public No-GX10 Quickstart

These commands validate the project without SSH access, model downloads, or live
vLLM execution:

```powershell
uv sync
uv run vllm-optimizer --version
uv run pytest
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

Expected result: version `0.56.3`, passing tests, and a release-check report
with `overall_status: pass`.

## Local Environment

Requirements:

- Python 3.11 or newer
- `uv`
- Git
- configured SSH access for optional live GX10 runs

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
Keep credentials and host-specific paths out of committed files. Before sharing
logs or reports, redact SSH usernames, private host addresses when needed, local
absolute paths, tokens, passwords, and private model-cache paths.

The current GX10 target has used:

```text
user@host.example
```

The Qwen profile expects the remote vLLM executable path recorded in the profile
configuration. If that path changes, update the local profile or config before
running live sweeps.

The multi-model workflow starts from `config/model-catalog.json`. Catalog
entries are local vLLM candidates only and point at committed serve profiles for
Qwen, Gemma, GLM, Qwen 27B variants, and DeepSeek. New models should pass a
model-aware smoke check before benchmark or sweep results are compared.

Model profiles may export session-scoped environment variables before starting
vLLM. The committed new-model profiles use `HF_HOME=$HOME/.cache/huggingface-vllm-optimizer`
so live smoke and benchmark runs avoid root-owned Hugging Face cache locks on
the GX10 without changing system ownership or deleting existing cache data.

## Optional GX10 Live Path

Once local verification passes and the local config exists, start with previews
and read-only discovery. Only run live commands after the generated command
plan and artifact targets look correct.

The public alpha assumes one model at a time. It does not manage Docker cleanup,
root-owned cache deletion, or persistent system tuning.

## Model Cache Hygiene

Large vLLM checkpoints can make the 916G formatted GX10 root filesystem look
small very quickly. Run one catalog model at a time, stop vLLM before switching
models, and remove the optimizer-owned cache for the completed model unless the
next command immediately reuses it.

Check the live cache footprint:

```powershell
ssh user@host.example df -h /
ssh user@host.example du -sh '$HOME/.cache/huggingface' '$HOME/.cache/huggingface-vllm-optimizer' '/.cache/huggingface'
```

The committed multi-model profiles use:

```text
HF_HOME=$HOME/.cache/huggingface-vllm-optimizer
```

After a one-model block is done, remove only the matching optimizer-owned model
directory or clear the dedicated optimizer cache if no follow-on run needs it:

```powershell
ssh user@host.example rm -rf '$HOME/.cache/huggingface-vllm-optimizer/hub/models--OWNER--MODEL' '$HOME/.cache/huggingface-vllm-optimizer/xet'
```

After the latest manual cleanup, the GX10 root filesystem reported 916G total,
64G used, 805G available, and 8% usage. The largest remaining top-level
directories were `/home` at 21G, `/usr` at 16G, `/var` at 4.6G, `/opt` at 2.4G,
and `/.cache` under 1G.

Older root-owned model caches require sudo on the GX10. The optimizer does not
delete them automatically, and any future Docker or root-cache cleanup should
stay an explicit maintenance action rather than a hidden optimizer behavior.

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

For a new model, preview the model smoke lifecycle, then run the live check only
with the explicit gate:

```powershell
uv run vllm-optimizer model-catalog --catalog config/model-catalog.json --out artifacts/models/catalog.json
uv run vllm-optimizer model-smoke-plan --catalog config/model-catalog.json --model gemma-4-e4b-it --out artifacts/models/gemma-4-e4b-it/smoke-plan.json
uv run vllm-optimizer model-smoke-run --catalog config/model-catalog.json --model gemma-4-e4b-it --config config/local.gx10.json --out artifacts/models/gemma-4-e4b-it/live --timeout-seconds 1200 --confirm-live-run
```

After smoke passes, run the conservative baseline and safe-profile sweep for
that one model before moving to the next model. The safe-profile sweep files are
under `config/sweeps/*-safe-profiles.json`; GLM and DeepSeek require the
explicit risky-session gate because their safe profiles pin `moe_backend`.

For one active user's interactive feel, use the single-user recipe instead of a
high-concurrency saturation recipe:

```powershell
uv run vllm-optimizer cockpit-launch --sweep config/sweeps/qwen-single-user-interactive.json --out-dir artifacts/controller/qwen-single-user
```

That recipe uses the concurrency-one interactive prompt set and ranks the
`single_user` objective by latency/responsiveness before aggregate throughput.

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
