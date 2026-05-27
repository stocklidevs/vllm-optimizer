# Public Release Checklist

Release label: `0.56.3 public alpha`

This checklist defines the minimum evidence needed before publishing the
repository or announcing the alpha. It is intentionally practical: a new reader
should be able to clone the project, understand the safety boundary, and run the
local verification path without a GX10.

## Required Public Files

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `docs/SETUP.md`
- `docs/PROJECT_STATUS.md`
- `docs/RESULTS.md`
- `docs/PUBLIC_RELEASE.md`
- `docs/PUBLICATION_CHECKLIST.md`
- `.github/workflows/ci.yml`
- `specs/000-project-roadmap-autonomy/spec.md`

## Fresh-Checkout Verification

From a clean checkout:

```powershell
uv sync
uv run vllm-optimizer --version
uv run pytest
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

Expected outcomes:

- `vllm-optimizer --version` prints `0.56.3`.
- `pytest` passes.
- `release-check` writes JSON and Markdown reports with `overall_status:
  pass`.
- No live GX10 connection is required.

## Release Evidence

Recorded on 2026-05-27:

- Focused release docs/version tests: `12 passed`.
- Full test suite: `287 passed`.
- Version check: `0.56.3`.
- Release-check: `overall_status: pass` in
  `artifacts/catalog/release-check.json`.
- Pinned npm dependency install: `npm ci` passed.
- npm vulnerability audit: `npm audit --audit-level=high` found `0`
  vulnerabilities.
- Active SpecKit feature: completed before the release commit.
- Git status: clean after the release commit.

## Safety Boundary

Public alpha users can safely run local planning, previews, report generation,
static cockpit/report views, and release verification without a GX10. Live runs
require an ignored local GX10 config and explicit gates.

The alpha does not automatically promote winners, mutate persistent Linux or
NVIDIA settings, clean Docker images, delete root-owned model caches, or manage
credentials.

## Known Limitations

- The best live evidence comes from one Asus GX10 and should be treated as
  machine-specific.
- The cockpit is useful for end-to-end local operation, but the CLI artifacts
  remain the source of truth.
- The package is not yet published to PyPI.
- Live model comparisons can download large checkpoints; run one model at a
  time and clean optimizer-owned caches after each model block.
- Tool-use optimization needs more model-specific validation before it should
  be presented as generally solved.

## Publication Options

1. Keep this work as a public alpha branch for review.
2. Merge it into `main` and publish the repository as alpha.
3. Push a pull request and request review before public release.
4. Tag `v0.56.3-alpha` after the final release-check passes.
