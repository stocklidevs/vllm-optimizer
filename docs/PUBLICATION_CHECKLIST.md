# Public Publication Checklist

This checklist starts after the repository is already in public-alpha shape.
Stop at the final line if the goal is to prepare a branch but not publish it
yet.

## Definition Of Public OK

The repository is public OK when a stranger can clone it, run the local
verification path, understand the GX10 safety boundary, inspect the benchmark
results without private context, and see no committed private infrastructure
details.

## Local Gates

- [ ] Confirm the branch is the intended publication branch.
- [ ] Confirm `git status --short` is clean before final verification.
- [ ] Run the public docs and private-reference regression tests:

```powershell
uv run pytest tests/unit/test_release_docs.py
```

- [ ] Run the Python verification gate:

```powershell
uv sync
uv sync --group dev
uv run pytest
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

- [ ] Run the pinned npm dependency gate for the UI QA helper:

```powershell
npm ci
npm audit --audit-level=high
```

## GitHub Gates

- [ ] Push the cleanup branch to a private or review remote first.
- [ ] Confirm GitHub renders README and docs correctly.
- [ ] Confirm CI passes on the pushed branch.
- [ ] Confirm repository settings include a clear description, screenshot-rich
  README rendering, and topics such as `vllm`, `llm-inference`,
  `benchmarking`, `optimizer`, and `spec-kit`.
- [ ] Confirm issue templates render for bug reports and model validation
  reports.
- [ ] Confirm security reporting is enabled or the fallback contact path in
  `SECURITY.md` is acceptable.

## Publish Line

Stop here until the maintainer explicitly says: push it on a public branch.

After approval:

1. Merge or fast-forward the cleanup branch into `main`.
2. Push `main` to the public remote.
3. Tag the public alpha, for example `v0.56.7-alpha`.
4. Create the GitHub release notes from `CHANGELOG.md`,
   `docs/RELEASE_NOTES_DRAFT.md`, and `docs/RESULTS.md`.
