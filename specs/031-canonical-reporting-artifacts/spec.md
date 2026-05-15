# Feature Specification: Canonical Reporting Artifacts

**Feature Branch**: `031-canonical-reporting-artifacts`

**Created**: 2026-05-15

**Status**: Draft

**Input**: User description: "Future product direction is a polished web interface where users select knob groups to tune, receive execution feedback, and review graphical reports. Reporting should be added as a hybrid layer: canonical deterministic reports first, then a web interface that reads and renders those same reports beautifully."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Produce a Canonical Run Report (Priority: P1)

As an optimizer user, I want every completed sweep or pipeline stage to produce a stable report that explains the winner, the decision, the measured metrics, and the artifact provenance so that results can be reviewed without manually opening many raw files.

**Why this priority**: This creates the source of truth that both automation and the future web interface can rely on.

**Independent Test**: Can be tested by giving the system an existing completed run directory and verifying that it produces a report with a recommendation, metrics, provenance, and links to source artifacts.

**Acceptance Scenarios**:

1. **Given** a completed sweep with ranked candidates, **When** the user generates a report, **Then** the report identifies the winning candidate, objective, score, throughput, latency, spread, failure rate, and source artifact paths.
2. **Given** a completed run where baseline wins, **When** the user generates a report, **Then** the report clearly recommends keeping the baseline and explains why tuned candidates were not selected.
3. **Given** a completed run with failed trials, **When** the user generates a report, **Then** the report includes failure counts and excludes invalid candidates from recommendations.

---

### User Story 2 - Feed the Future Web Interface (Priority: P2)

As a future web interface, I need reporting data in a stable machine-readable shape so that dashboards, charts, progress views, and comparison screens can render the same decisions produced by the automation layer.

**Why this priority**: This keeps the web UI focused on interaction and visualization instead of duplicating optimizer decision logic.

**Independent Test**: Can be tested by validating the generated report data against the documented report fields and confirming that all required chart and summary inputs are present.

**Acceptance Scenarios**:

1. **Given** a canonical report, **When** a UI reads it, **Then** it can display the selected knob group, run status, candidate rankings, objective scores, metric trends, and recommendation without reading raw benchmark internals.
2. **Given** two reports from different knob families, **When** a UI reads them, **Then** it can compare their recommendations and metric summaries using the same data contract.

---

### User Story 3 - Review Human-Friendly Decisions (Priority: P3)

As a user reviewing optimizer history, I want a readable decision summary so that I can understand what happened, what won, what did not win, and what the next safe action should be.

**Why this priority**: Human-readable reporting builds trust in automated optimization before the web dashboard exists.

**Independent Test**: Can be tested by opening the generated readable report and verifying that a user can identify the recommendation and supporting evidence in under two minutes.

**Acceptance Scenarios**:

1. **Given** a completed session tuning sweep where no tuning wins, **When** the user reads the report, **Then** it states that no session tuning is recommended and gives supporting metrics.
2. **Given** a completed sweep with a non-baseline winner, **When** the user reads the report, **Then** it states whether confirmation or promotion is required before using the winner.

---

### Edge Cases

- A report source directory is missing expected ranking or summary artifacts.
- A run has zero successful candidates.
- A ranking file exists but objectives disagree about the winner.
- A candidate has high throughput but unacceptable failure rate or instability.
- The same report is regenerated from unchanged inputs.
- A future web interface needs chart data even when no candidate is recommended.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a canonical machine-readable report for completed optimizer runs that includes recommendation, status, objectives, candidate metrics, failure counts, and provenance.
- **FR-002**: System MUST generate a human-readable report from the same source data so users can review decisions before a web interface exists.
- **FR-003**: Reports MUST identify the source run family, such as parameter sweep, session tuning sweep, confirmation run, or full pipeline run.
- **FR-004**: Reports MUST include enough data for a future web interface to render candidate ranking tables, objective comparison charts, latency and throughput summaries, stability indicators, and recommendation panels without re-implementing decision logic.
- **FR-005**: Reports MUST preserve links or paths to raw artifacts used to make the decision.
- **FR-006**: Reports MUST distinguish between "recommended winner", "keep current baseline", "requires confirmation", and "no recommendation possible".
- **FR-007**: Reports MUST explain why a candidate won or why the baseline remained preferred using measured metrics and safety constraints.
- **FR-008**: Reports MUST be deterministic when regenerated from unchanged inputs.
- **FR-009**: Reports MUST clearly mark incomplete, failed, or excluded trials and must not recommend candidates that fail the run's validity criteria.
- **FR-010**: The reporting layer MUST be the shared source of truth for future web dashboards; the web interface should read report artifacts rather than independently recomputing optimizer decisions.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST report the objective family being measured for each source run.
- **ER-002**: Feature MUST identify reproducibility inputs required to regenerate or audit the run.
- **ER-003**: Feature MUST retain references to raw plan, result, ranking, summary, and decision artifacts used by the report.
- **ER-004**: Feature MUST identify whether reported GX10 actions were read-only, session-mutating, or persistent-mutating.
- **ER-005**: Feature MUST support report generation from existing artifacts without requiring a new live remote run.

### Key Entities *(include if feature involves data)*

- **Canonical Report**: The stable report record containing source metadata, recommendation, objective summaries, candidate rankings, safety status, and artifact provenance.
- **Readable Report**: A human-friendly decision summary generated from the canonical report.
- **Report Source**: The completed run, sweep, confirmation, or pipeline directory used as report input.
- **Recommendation**: The decision outcome, including winner identity, baseline preference, confirmation requirement, or inability to recommend.
- **Chart Dataset**: Normalized metric series and comparison values intended for future web visualizations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can identify the recommendation, winning profile or baseline decision, and top supporting metrics from a readable report in under two minutes.
- **SC-002**: Regenerating a report from unchanged input artifacts produces identical recommendation data and candidate ordering in 100% of repeated attempts.
- **SC-003**: Reports expose all fields required to render at least five future dashboard views: run summary, candidate ranking, objective comparison, metric spread, and artifact provenance.
- **SC-004**: Reports prevent invalid recommendations by marking failed or incomplete candidates as non-recommendable in 100% of cases covered by tests.
- **SC-005**: Existing completed sweep and session tuning artifacts can be reported without starting a new GX10 session.

## Assumptions

- The next product direction is a hybrid architecture: canonical reports are generated first, and the future web interface consumes those reports.
- The web interface is not part of this feature; this feature prepares the reporting contract and user-facing report artifacts that the web UI will later render.
- Report generation should cover recent optimizer artifact families first, especially sweeps, session tuning sweeps, and pipeline outputs.
- Existing artifact retention rules remain in place; reports reference artifacts rather than embedding all raw measurements.
