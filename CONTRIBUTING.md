# Contributing

vLLM Optimizer is in public alpha. Contributions are welcome, but the project
still treats deterministic artifacts, explicit safety gates, and SpecKit docs as
part of the product rather than paperwork.

## Local Setup

```powershell
uv sync
uv run vllm-optimizer --version
uv run pytest
```

If your shell cannot update `.venv\Scripts\vllm-optimizer.exe` because another
process is holding it, stop the running cockpit or Python process and retry.

## Development Flow

1. Read `AGENTS.md` and the active SpecKit plan before changing behavior.
2. Add or update tests for code changes.
3. Keep CLI artifacts deterministic and machine-readable.
4. Update documentation when commands, artifacts, or safety boundaries change.
5. Bump the version and changelog for release-facing work.
6. Run the focused tests, full test suite, and `release-check` before handoff.

Recommended verification:

```powershell
uv run pytest
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

## SpecKit Expectations

Feature work should have a spec, plan, tasks, and completion status under
`specs/`. The active feature is recorded in `.specify/feature.json`. Before a
release commit, the active SpecKit tasks should be complete and the spec/plan
status should no longer be Draft or Implementing.

## GX10 Safety

Live runs can start remote vLLM processes and download large model files. Keep
these rules visible:

- Never commit `config/local.gx10.json`, SSH keys, passwords, tokens, or local
  machine paths that reveal private credentials.
- Run one model at a time unless a spec explicitly expands the safety boundary.
- Use the committed `HF_HOME=$HOME/.cache/huggingface-vllm-optimizer` model
  cache pattern for live model comparisons.
- Clean optimizer-owned model caches after each model block when the next run
  does not reuse the same model.
- Do not add persistent Linux, NVIDIA, kernel, boot, service, firmware, Docker,
  or credential mutations without a dedicated safety and rollback spec.

## Pull Request Checklist

- Tests pass locally.
- Release-check passes when the change affects release artifacts.
- Docs and examples match the implemented CLI behavior.
- New artifacts are deterministic or explicitly marked as live-run evidence.
- Safety gates stay explicit for risky-session, session tuning, live GX10 runs,
  and promotion.
