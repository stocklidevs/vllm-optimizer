# Feature Specification: Public Alpha Release and Results Narrative

**Feature Branch**: `072-public-alpha-release`

**Created**: 2026-05-27

**Status**: Completed

**Input**: User asked to bring the project to a state that is publishable to the public and to present the optimizer results with an explanation of why the measured results occurred.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publishable Project Basics (Priority: P1)

As a public visitor or potential contributor, I want the repository to clearly explain what the project is, how it is licensed, how to install it, how to run a safe local smoke check, and what is experimental, so that I can evaluate or try the tool without relying on private conversation history.

**Why this priority**: A public repository without licensing, safety boundaries, setup instructions, and clear status is not truly publishable.

**Independent Test**: Can be tested by reading the repository from a fresh checkout and confirming that a new user can identify the license, project status, installation path, safety boundaries, and first commands without GX10 credentials.

**Acceptance Scenarios**:

1. **Given** a public reader opens the repository, **When** they read the README, **Then** they can tell that this is an experimental public alpha for deterministic vLLM optimization and can find setup, safety, results, and contribution links.
2. **Given** a public reader wants to reuse the project, **When** they inspect the repository root, **Then** licensing and security/contribution expectations are explicit.
3. **Given** a public reader does not have a GX10, **When** they follow the quickstart, **Then** they can run local tests, artifact generation, and dry-run commands without remote access.

---

### User Story 2 - Results Presentation (Priority: P2)

As a technical audience member, I want a concise results report that separates single-user performance from aggregate concurrent throughput and explains why the optimizer produced modest single-user gains but large concurrency gains, so that I can understand the value without misreading tokens/sec.

**Why this priority**: The headline result can be misunderstood. Public release needs an honest narrative that explains what improved, what did not, and why.

**Independent Test**: Can be tested by reviewing a generated public results document and verifying that every reported number links back to recorded artifacts and explains the measurement context.

**Acceptance Scenarios**:

1. **Given** the results report is opened, **When** a reader compares Qwen C1 and C8 results, **Then** the report states that C8 tokens/sec is aggregate throughput across concurrent requests, not per-user streaming speed.
2. **Given** a reader reviews the model comparison, **When** they inspect Gemma, GLM, Qwen3.6, Qwen3.5, and DeepSeek rows, **Then** they can see baseline, optimized result, delta, and promotion recommendation.
3. **Given** a reader asks why results differ, **When** they read the explanation, **Then** they see that scheduler batching and concurrency unlocked aggregate throughput, while single-user throughput remained bounded by model/backend/request shape.

---

### User Story 3 - Fresh-Clone Release Verification (Priority: P3)

As a maintainer, I want a repeatable release checklist that validates the public alpha from a clean checkout perspective, so that release confidence does not depend on a dirty local environment or private machine state.

**Why this priority**: The repository already has passing tests, but public readiness requires a clean-install and documentation-oriented verification pass.

**Independent Test**: Can be tested by running the release checklist and confirming it records test results, release-check status, docs presence, and known limitations.

**Acceptance Scenarios**:

1. **Given** the release checklist is run, **When** checks complete, **Then** it records full tests, release-check, version consistency, public docs presence, and fresh-clone instructions.
2. **Given** the project has GX10-specific features, **When** the checklist describes live runs, **Then** it clearly marks them as optional and gated by local config and SSH access.

### Edge Cases

- A public reader assumes the 98 tokens/sec C8 result is per user instead of aggregate throughput.
- A public reader lacks GX10, private network, vLLM, or NVIDIA hardware.
- A public user tries to run live commands without creating a local ignored config.
- A benchmark result exists but the source artifact is missing or stale.
- A dependency install or test run works locally but fails from a clean clone because files are ignored or undocumented.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST include an explicit open-source license file before public release.
- **FR-002**: The repository MUST include public-facing contribution and security guidance.
- **FR-003**: The README MUST clearly label the project as an experimental public alpha and link to setup, safety, results, and roadmap documentation.
- **FR-004**: Public setup documentation MUST include a no-GX10 local path and a gated GX10 live path.
- **FR-005**: Public documentation MUST explain that live GX10 runs are session-scoped, SSH-gated, and require local ignored config.
- **FR-006**: Public documentation MUST include cache hygiene guidance for one-model-at-a-time live work.
- **FR-007**: A public results report MUST summarize Qwen C1, Qwen C8, Gemma, GLM, Qwen3.6, Qwen3.5, and DeepSeek measurements.
- **FR-008**: The results report MUST distinguish single-user tokens/sec from aggregate concurrent tokens/sec.
- **FR-009**: The results report MUST link every headline result to local artifact paths or committed documentation that records the source measurement.
- **FR-010**: The release checklist MUST validate version consistency, full tests, release-check, public docs presence, and clean-checkout guidance.
- **FR-011**: The project version, changelog, SpecKit active pointers, and release docs MUST be updated before the public alpha commit.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Objective family is public release readiness and benchmark interpretation, not a new vLLM optimization sweep.
- **ER-002**: Reproducibility inputs include benchmark artifact paths, model identities, prompt/concurrency context, vLLM serve profiles, version, and git commit.
- **ER-003**: Raw artifacts retained include benchmark summaries, sweep rankings, model smoke summaries, release-check output, and public results report.
- **ER-004**: GX10 actions for this feature are read-only unless an explicit follow-up live validation is requested; release preparation itself must not mutate the GX10.
- **ER-005**: Dry-run expectations are local documentation, tests, release-check, and clean-checkout verification before any public publication action.

### Key Entities *(include if feature involves data)*

- **Public Release Checklist**: A maintainer-facing checklist of required public-readiness gates, evidence, and outcomes.
- **Benchmark Result Summary**: A public-facing row or section that records model, workload, baseline, optimized result, delta, context, and artifact provenance.
- **Results Narrative**: The explanatory document that states what improved, what did not, and why the optimizer found those outcomes.
- **Public Safety Boundary**: Documentation that tells external users which operations are local, remote session-mutating, promotion-gated, or out of scope.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A fresh reader can identify license, alpha status, setup, safety, and results documents from the README in under five minutes.
- **SC-002**: Full local pytest suite and `release-check` pass before the public alpha release commit.
- **SC-003**: The public results report includes at least seven measured result rows and explains C8 aggregate throughput versus per-user average.
- **SC-004**: Every headline performance number in the public results report has a source artifact or documentation path.
- **SC-005**: No public quickstart step requires GX10 SSH access unless it is explicitly labeled as an optional live-run path.

## Assumptions

- The first public release should be labeled public alpha rather than stable.
- The project will be published as source on GitHub before PyPI or packaged binary distribution.
- MIT is the default license choice unless the user requests a different license before implementation.
- Existing local tests and release-check remain the core verification gates.
- Live GX10 benchmark reruns are not required for this release unless artifact provenance is missing.
