# Feature Specification: Run Comparison Report

**Feature Branch**: `007-run-comparison-report`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Add structured run comparison reporting for vLLM optimizer artifacts. The system should read baseline benchmark summaries, one-shot sweep rankings, and repeated sweep stability rankings, then produce concise JSON and Markdown reports that highlight the current best configuration, baseline deltas, stability notes, failure counts, artifact links, and recommendation text. This feature must be local-only and must not contact the GX10 or run benchmarks."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Summarize Existing Runs (Priority: P1)

As the operator, I want to point the tool at existing baseline, sweep, and
repeated sweep artifacts and get one compact comparison report.

**Why this priority**: The optimizer now produces useful artifacts, but the
operator should not need to read large JSON files to understand the current
state.

**Independent Test**: Can be tested with fixture artifact files and no GX10
access.

**Acceptance Scenarios**:

1. **Given** baseline, one-shot sweep, and repeated sweep artifacts, **When**
   the operator generates a report, **Then** the output identifies the best
   configuration, core metrics, baseline deltas, and source artifact paths.
2. **Given** only a repeated sweep ranking, **When** the operator generates a
   report, **Then** the output still summarizes candidates and notes missing
   baseline or one-shot context.

---

### User Story 2 - Produce Markdown and JSON Outputs (Priority: P2)

As the operator, I want both machine-readable and human-readable reports so the
same comparison can be used by scripts and read quickly in a terminal or README.

**Why this priority**: JSON preserves traceability, while Markdown makes the
decision legible without custom tooling.

**Independent Test**: Can be tested by generating both output formats from the
same fixture inputs and verifying consistent winners and metrics.

**Acceptance Scenarios**:

1. **Given** valid comparison inputs, **When** JSON and Markdown outputs are
   requested, **Then** both outputs name the same winner and source artifacts.
2. **Given** missing optional inputs, **When** outputs are generated, **Then**
   both outputs include a clear note rather than failing unnecessarily.

---

### User Story 3 - Explain Recommendations and Stability (Priority: P3)

As the operator, I want the report to explain why a configuration is recommended,
including whether the result appears stable or noisy.

**Why this priority**: Optimization decisions should be auditable and should not
hide variance behind a single "best" label.

**Independent Test**: Can be tested with fixture candidates where one candidate
is faster but has higher spread.

**Acceptance Scenarios**:

1. **Given** repeated sweep stability metrics, **When** the report is generated,
   **Then** it includes stability notes about spread, failure rate, and
   confidence in the recommendation.
2. **Given** a close winner with higher spread, **When** the report is
   generated, **Then** it describes the trade-off between mean performance and
   stability.

### Edge Cases

- Optional baseline, sweep, or repeated ranking paths are missing.
- Input files exist but are malformed or lack expected metrics.
- A ranking contains no successful candidates.
- Candidate artifact links are deeply nested.
- Two objectives select different winners.
- Metrics contain null values because token usage was unavailable.
- Paths include Windows separators.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate reports from local artifact files only.
- **FR-002**: System MUST NOT contact the GX10, start vLLM, or run benchmarks.
- **FR-003**: System MUST accept optional baseline summary, one-shot sweep
  ranking, and repeated sweep ranking inputs.
- **FR-004**: System MUST produce a machine-readable JSON report.
- **FR-005**: System MUST optionally produce a Markdown report.
- **FR-006**: System MUST identify the current recommended configuration when
  a rankable repeated or sweep ranking is available.
- **FR-007**: System MUST include baseline deltas when available.
- **FR-008**: System MUST include stability notes from repeated sweep spread
  and failure-rate metrics when available.
- **FR-009**: System MUST preserve links to source artifact paths.
- **FR-010**: System MUST clearly list missing optional inputs and excluded or
  failed candidates.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Objective family is reporting and decision support for existing
  optimization artifacts.
- **ER-002**: Reports MUST include source artifact paths and generation inputs
  required to reproduce the report.
- **ER-003**: Reports MUST not create new benchmark measurements.
- **ER-004**: GX10 action classification is local-only with no remote actions.
- **ER-005**: The report MUST name the objective used for each recommendation.

### Key Entities *(include if feature involves data)*

- **Report Input Set**: Optional paths for baseline summary, sweep ranking, and
  repeated sweep ranking.
- **Candidate Snapshot**: One summarized configuration with objective rank,
  metrics, baseline deltas, stability metrics, and artifact links.
- **Recommendation**: Chosen current best candidate with objective, reasoning,
  trade-offs, and source references.
- **Comparison Report**: JSON and Markdown output containing inputs, summaries,
  recommendation, notes, and source artifact links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Fixture-based report generation completes without GX10 access in
  100% of tests.
- **SC-002**: JSON and Markdown outputs name the same winner in fixture tests.
- **SC-003**: Reports include source artifact links for 100% of summarized
  candidates that provide artifact paths.
- **SC-004**: Reports list missing optional inputs instead of failing when at
  least one ranking artifact is available.
- **SC-005**: Stability notes are generated for 100% of repeated-ranking
  candidates with spread or failure-rate metrics.

## Assumptions

- Repeated sweep rankings are preferred over one-shot sweep rankings when both
  are available.
- Throughput is the default headline objective unless a repeated ranking marks
  a balanced winner with materially different trade-offs.
- Markdown output should be concise and suitable for copying into notes or a
  release summary.
