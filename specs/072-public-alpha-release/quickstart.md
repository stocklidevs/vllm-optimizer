# Quickstart: Public Alpha Release and Results Narrative

## No-GX10 Public Smoke

From a fresh checkout:

```powershell
uv sync
uv run vllm-optimizer --version
uv run pytest
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

Expected outcome:

- Version prints the public alpha version.
- Full tests pass.
- Release check reports `overall_status: pass`.

## Read Public Docs

Check that these files exist and are linked from the README:

```text
LICENSE
CONTRIBUTING.md
SECURITY.md
docs/SETUP.md
docs/PROJECT_STATUS.md
docs/PUBLIC_RELEASE.md
docs/RESULTS.md
CHANGELOG.md
```

## Optional GX10 Live Path

Live runs remain optional. They require:

- Tailscale SSH access.
- Ignored local config such as `config/local.gx10.json`.
- Explicit live-run gates.
- One-model-at-a-time cache cleanup.

Public users without a GX10 should stop at local smoke and report generation.
