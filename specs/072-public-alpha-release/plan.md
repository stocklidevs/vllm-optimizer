# Implementation Plan: Public Alpha Release and Results Narrative

**Branch**: `072-public-alpha-release` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/072-public-alpha-release/spec.md`

## Summary

Prepare vLLM Optimizer for a public alpha source release by adding public repository hygiene, a clean public quickstart, safety/contribution/security documentation, and a results narrative that explains baseline measurements, optimized results, artifact provenance, and the difference between single-user and aggregate concurrent throughput.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Existing standard-library CLI/web modules; no new runtime dependencies planned

**Storage**: Markdown release docs, JSON release-check artifacts, existing benchmark/sweep artifacts

**Testing**: pytest plus the existing `release-check` command

**Target Platform**: Public GitHub source repository, local Windows/Linux development, optional remote GX10 via configured SSH

**Project Type**: Python CLI plus dependency-free local web cockpit

**Performance Goals**: No new optimizer performance target; public results must accurately represent existing measured artifacts

**Constraints**: No persistent GX10 changes; no public docs may require private credentials or local ignored config for the no-GX10 path

**Scale/Scope**: Public alpha readiness for source release, not PyPI packaging or cloud deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic Experiments**: PASS. Results documentation must cite source artifacts and distinguish workload contexts.
- **Complete Traceability**: PASS. Public result rows link to benchmark summaries, sweep rankings, and status docs.
- **Remote Safety and Reversibility**: PASS. Release prep is local/read-only for GX10; public docs keep live actions gated.
- **Objective-Driven Optimization**: PASS. Objective is release readiness and benchmark interpretation, not a new tuning run.
- **Testable, Modular Automation**: PASS. Verification uses full pytest, release-check, docs checks, and clean-checkout instructions.

## Project Structure

### Documentation (this feature)

```text
specs/072-public-alpha-release/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- public-release-checklist.md
|   `-- results-report.md
`-- tasks.md
```

### Source Code (repository root)

```text
README.md
CHANGELOG.md
LICENSE
CONTRIBUTING.md
SECURITY.md
docs/
|-- SETUP.md
|-- PROJECT_STATUS.md
|-- PUBLIC_RELEASE.md
`-- RESULTS.md
tests/
|-- unit/
`-- integration/
src/vllm_optimizer/
```

**Structure Decision**: Keep release readiness mostly in repository-root and `docs/` Markdown files. Add tests only where release-check or public docs validation needs a guard. Avoid new runtime dependencies.

## Experiment and Safety Design

**Objective Family**: Release readiness, public documentation quality, and benchmark interpretation.

**Benchmark Inputs**: Existing benchmark and sweep artifacts for Qwen C1, Qwen C8, Gemma, GLM, Qwen3.6, Qwen3.5, and DeepSeek.

**Remote Actions**: None required. Optional live GX10 reruns remain gated by existing local config and SSH commands.

**Artifacts**: `artifacts/catalog/release-check.json`, `artifacts/catalog/release-check.md`, existing benchmark summaries and sweep rankings, `docs/RESULTS.md`, `docs/PUBLIC_RELEASE.md`.

**Rollback/Cleanup**: No GX10 mutation. Local docs/code changes remain git-reversible. Cache cleanup rules from the roadmap remain in force for any later live rerun.

## Complexity Tracking

No constitution violations.
