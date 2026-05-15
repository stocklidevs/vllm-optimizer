# Research: Canonical Reporting Artifacts

## Decision: Canonical Report as Shared Contract

Use one canonical report shape that includes source metadata, recommendation, objective summaries, candidate summaries, chart-ready datasets, and provenance.

**Rationale**: The future web UI needs a stable input contract and should not duplicate ranking or recommendation logic.

**Alternatives considered**:

- Keep only specialized reports: rejected because the web UI would need many adapters and inconsistent field names.
- Build web reporting logic first: rejected because it weakens CLI automation and reproducibility.

## Decision: Local-Only Report Generation

Generate reports only from existing artifacts, without live GX10 access.

**Rationale**: Reporting should be safe, repeatable, and usable after a run has completed.

**Alternatives considered**:

- Query remote machine during reporting: rejected because it creates unnecessary coupling and non-determinism.

## Decision: Baseline-Aware Recommendation Status

The report should distinguish `recommended-winner`, `keep-baseline`, `requires-confirmation`, and `no-recommendation`.

**Rationale**: The recent session tuning sweep showed that baseline can legitimately win. The report must explain that outcome instead of always celebrating the top ranked row as a new recommendation.

**Alternatives considered**:

- Always recommend rank 1: rejected because rank 1 can be the baseline/no-tuning candidate.
