# Feature Specification: Workload Leaderboard

**Feature Branch**: `018-workload-leaderboard`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Create a workload leaderboard and next-action report that summarizes live workload sweep rankings, promoted profiles, and failed risky candidates such as FP8/ninja across sequential and concurrent Qwen workloads."

## User Scenarios & Testing

### User Story 1 - See Workload Winners (Priority: P1)

As the optimizer operator, I want one report that lists each workload winner, its metrics, and its parameter overrides, so I do not have to inspect multiple ranking artifacts by hand.

**Why this priority**: The project now has several workload-specific rankings and decisions.

**Independent Test**: Generate a leaderboard from multiple ranking artifacts and verify each workload has a winner, metrics, baseline delta, and recommendation.

**Acceptance Scenarios**:

1. **Given** live ranking artifacts for multiple workloads, **When** the leaderboard is generated, **Then** each workload lists the top balanced candidate and metrics.
2. **Given** a promoted profile path for a workload, **When** the leaderboard is generated, **Then** the profile is listed as promoted for that workload.

---

### User Story 2 - Surface Actionable Failures (Priority: P2)

As the optimizer operator, I want failed risky candidates summarized as findings, so setup blockers like missing `ninja` become clear next actions.

**Why this priority**: Failed risky candidates are useful evidence, not noise.

**Independent Test**: Provide a ranking with failed candidates and server logs mentioning `ninja`; verify the report calls out the dependency.

**Acceptance Scenarios**:

1. **Given** FP8 candidate failures caused by missing `ninja`, **When** the report is generated, **Then** next actions include installing or exposing `ninja` on the GX10.

### Edge Cases

- A ranking artifact is missing a balanced objective.
- A workload has no promoted profile.
- A failed candidate has missing or unreadable server logs.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST provide a workload leaderboard command that accepts one or more labeled ranking artifacts.
- **FR-002**: The leaderboard MUST include winner metrics, overrides, baseline deltas, and recommendation status for each workload.
- **FR-003**: The leaderboard MUST accept optional labeled promoted profiles and list them separately.
- **FR-004**: The leaderboard MUST detect failed candidates and summarize likely causes when logs contain known dependency failures.
- **FR-005**: The leaderboard MUST output JSON and optionally Markdown.
- **FR-006**: Documentation MUST show how to generate the Qwen workload leaderboard from live artifacts.

### Experiment Requirements

- **ER-001**: Objective family is workload-specific balanced ranking.
- **ER-002**: Reproducibility inputs are ranking artifact paths, promoted profile paths, and report generation version.
- **ER-003**: Raw artifacts retained are source rankings, failed trial logs, report JSON, and report Markdown.
- **ER-004**: GX10 actions are none; the report is local-only.
- **ER-005**: Dry-run/live remote behavior is not applicable because this feature reads existing artifacts only.

### Key Entities

- **Workload Summary**: Winner, baseline candidate, deltas, failed candidates, and recommendation.
- **Promoted Profile Summary**: Profile id, path, candidate provenance, and confirmation provenance.
- **Failed Candidate Finding**: Workload, candidate id, overrides, and likely cause.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A leaderboard can summarize at least four workload rankings in one JSON and Markdown report.
- **SC-002**: FP8/ninja failures are surfaced as next-action findings.
- **SC-003**: Workloads without promoted profiles are marked as evidence/watch rather than promoted.
- **SC-004**: The full automated test suite passes after adding the report.

## Assumptions

- Ranking artifacts remain available under ignored `artifacts/` paths.
- Candidate order `0` is the baseline/control candidate for the workload sweeps created in Spec 016 and Spec 017.
- The leaderboard is advisory and does not promote profiles by itself.
