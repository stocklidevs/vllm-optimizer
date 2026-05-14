# Feature Specification: Risky Winner Confirmation

**Feature Branch**: `015-risky-winner-confirmation`

**Created**: 2026-05-14

**Status**: Draft

**Input**: User description: "Confirm the risky-session sweep winner with repeated live A/B benchmarks against the current recommended profile, generate a promotion-ready risky winner profile, and promote it to the default recommended profile only if the repeated confirmation materially wins."

## User Scenarios & Testing

### User Story 1 - Guard Risky Promotion (Priority: P1)

As the optimizer operator, I want a risky sweep winner to be promoted only after a repeated A/B confirmation says it is materially better, so the default profile does not change based on one noisy sweep.

**Why this priority**: This is the safety gate between experimental risky-session flags and the reusable default profile.

**Independent Test**: Provide a repeated A/B report with a switch decision and verify promotion succeeds with confirmation provenance; provide an inconclusive report and verify promotion is refused.

**Acceptance Scenarios**:

1. **Given** a risky winner ranking and an A/B report whose decision is `switch-to-recommended`, **When** promotion is requested, **Then** the default profile is written with ranking and A/B confirmation provenance.
2. **Given** a risky winner ranking and an A/B report whose decision is `keep-original` or `inconclusive`, **When** promotion is requested, **Then** the default profile remains unchanged.

---

### User Story 2 - Run Repeated Live Confirmation (Priority: P2)

As the optimizer operator, I want the current recommended profile and risky winner profile benchmarked with the same prompt set and repetition count, so the decision is based on like-for-like evidence.

**Why this priority**: The risky winner looked promising in the sweep, but live repetitions are needed before it becomes the default.

**Independent Test**: Run three repetitions for each profile, generate an A/B report, and verify the report includes aggregates, spread metrics, deltas, and a decision.

**Acceptance Scenarios**:

1. **Given** current recommended and risky winner profiles, **When** three live benchmark repetitions are run for both, **Then** each repetition produces a summary artifact.
2. **Given** the six summaries, **When** the A/B report is generated, **Then** it ranks the risky winner against the current recommended profile using the same noise band as previous A/B confirmation.

### Edge Cases

- The confirmation report label for the candidate under promotion does not match the expected risky winner label.
- The confirmation report is missing a decision, aggregates, or benchmark deltas.
- A live repetition fails or produces a malformed summary.
- A profile output path already exists and overwrite is not explicitly allowed.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST provide a promotion command that requires an A/B confirmation report approving a switch before writing a promoted profile.
- **FR-002**: The promotion command MUST refuse `keep-original`, `inconclusive`, malformed, or label-mismatched confirmation reports.
- **FR-003**: The promoted profile MUST retain ranking provenance and add compact A/B confirmation provenance.
- **FR-004**: The workflow MUST create a reusable risky winner profile from the risky-session sweep ranking for repeated confirmation.
- **FR-005**: The workflow MUST promote the risky winner to the default recommended profile only if the repeated A/B confirmation materially favors it.
- **FR-006**: Documentation MUST include the repeated live confirmation and guarded promotion commands.

### Experiment Requirements

- **ER-001**: Objective family is balanced latency and throughput with zero added failures.
- **ER-002**: Reproducibility inputs are profile files, prompt set id, ranking artifact path, benchmark summaries, noise band, vLLM model identity, and git version.
- **ER-003**: Raw artifacts retained are each benchmark plan, metrics JSONL, summary JSON, A/B report JSON/Markdown, and promotion summary.
- **ER-004**: GX10 actions are session-mutating benchmark runs only; promotion and report generation are local-only.
- **ER-005**: Dry-run expectations are satisfied by local profile rendering and existing benchmark-plan output before live benchmark-run commands.

### Key Entities

- **Confirmation Report**: Repeated A/B aggregate with decision, labels, deltas, source summaries, and noise band.
- **Risky Winner Profile**: Reusable serve profile generated from the risky-session sweep ranking.
- **Confirmed Promotion**: Default profile update that includes both sweep ranking provenance and repeated A/B confirmation provenance.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Promotion is refused for 100% of A/B reports that do not decide `switch-to-recommended`.
- **SC-002**: Confirmed promotion records the source confirmation report path, decision, labels, repetition counts, aggregate latency, aggregate throughput, and deltas.
- **SC-003**: Repeated live confirmation uses at least three successful benchmark repetitions for the current recommended profile and at least three for the risky winner profile.
- **SC-004**: If promoted, the default recommended profile renders a valid vLLM serve command including the confirmed risky-session flags.

## Assumptions

- The existing risky-session sweep ranking remains available under ignored artifacts for local promotion input.
- The current recommended profile is the control and the risky winner profile is the candidate in the A/B report.
- A 1% noise band remains the materiality threshold for repeated A/B confirmation.
- Generated benchmark artifacts remain ignored by git; only profiles, docs, tests, and source changes are committed.
