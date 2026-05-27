# Research: Public Alpha Release and Results Narrative

## Decision: Release Label

Use "public alpha" rather than stable release.

**Rationale**: The project has strong deterministic CLI foundations, tests, and live validation, but it is still GX10-specific and the cockpit is young.

**Alternatives considered**:

- Stable release: rejected because live remote assumptions and public contributor workflows still need hardening.
- Private-only continuation: rejected because the repository can be useful publicly if expectations are honest.

## Decision: License Default

Use MIT unless the user requests a different license before implementation.

**Rationale**: MIT is simple, common for developer tooling, and friendly to public experimentation.

**Alternatives considered**:

- Apache-2.0: stronger patent language, but heavier than needed for a first alpha.
- No license: rejected because it makes public reuse ambiguous.

## Decision: Results Narrative Shape

Create a dedicated `docs/RESULTS.md` that separates single-user throughput, aggregate concurrency throughput, and model-comparison baselines.

**Rationale**: The C8 result is valuable but easy to misread. A separate results document can explain that 98 tokens/sec is aggregate C8 throughput, not 98 tokens/sec per user.

**Alternatives considered**:

- Put all results in README: rejected because README would become too dense.
- Keep results only in `docs/PROJECT_STATUS.md`: rejected because public readers need a focused narrative.

## Decision: Public Release Checklist

Create `docs/PUBLIC_RELEASE.md` as the release gate and add doc tests for required public files.

**Rationale**: Public readiness needs more than tests. It needs license, security, setup, results, known limitations, and clean-checkout instructions.

**Alternatives considered**:

- Rely only on `release-check`: rejected because it currently validates internal release metadata, not all public-facing repository hygiene.
