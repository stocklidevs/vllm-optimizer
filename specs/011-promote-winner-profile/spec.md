# Feature Specification: Promote Winner Profile

**Feature Branch**: `011-promote-winner-profile`

**Created**: 2026-05-13

**Status**: Draft

**Input**: User description: "Promote the best ranked sweep candidate into a reusable recommended serve profile. The operator can choose a ranking artifact and objective, preview the selected candidate and provenance, then generate a checked-in recommended profile plus a summary of the source sweep and metrics. The feature must be deterministic, refuse failed or missing candidates, avoid mutating remote systems, and preserve traceability to the ranking artifact, candidate id, trial ids, objective, and source configuration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preview Recommended Candidate (Priority: P1)

As the operator, I want to preview the candidate that would be promoted from a ranking artifact for a chosen objective so I can confirm the selected configuration before creating a reusable profile.

**Why this priority**: Promotion should be auditable before it changes tracked project configuration. A preview makes the decision legible and prevents accidentally promoting the wrong objective or candidate.

**Independent Test**: Can be fully tested by providing a completed ranking artifact and objective, then verifying the preview identifies one candidate, its metrics, changed parameters, source trials, and promotion eligibility without creating a profile.

**Acceptance Scenarios**:

1. **Given** a ranking artifact with successful candidates, **When** the operator previews promotion for the balanced objective, **Then** the system shows the top balanced candidate, its metrics, source trials, and proposed profile identity.
2. **Given** a ranking artifact and a non-default objective, **When** the operator previews promotion for that objective, **Then** the selected candidate comes from that objective's top-ranked result.

---

### User Story 2 - Generate Recommended Profile (Priority: P2)

As the operator, I want to generate a reusable recommended profile from the selected candidate so later benchmarks and sweeps can start from the current best-known configuration.

**Why this priority**: The live sweep result only becomes operationally useful when it can be reused without manual copying from ranking artifacts.

**Independent Test**: Can be fully tested by generating a recommended profile from a fixture ranking artifact and verifying the output contains the selected candidate's serve settings and traceability metadata.

**Acceptance Scenarios**:

1. **Given** a successful ranked candidate, **When** the operator generates the recommended profile, **Then** the profile includes the selected serve parameters and approved optional flags.
2. **Given** an existing recommended profile path, **When** the operator generates a replacement, **Then** the system requires an explicit overwrite choice and records the replacement provenance.

---

### User Story 3 - Reject Unsafe or Incomplete Promotion (Priority: P3)

As the operator, I want failed, missing, or ambiguous ranking data to be rejected so recommendations are never based on incomplete evidence.

**Why this priority**: A recommendation carries operational trust. It must fail closed when artifacts are incomplete or inconsistent.

**Independent Test**: Can be fully tested with malformed, empty, and partially failed ranking artifacts and verifying no recommended profile is written.

**Acceptance Scenarios**:

1. **Given** a ranking artifact with no successful candidates for the requested objective, **When** promotion is requested, **Then** the system refuses promotion and explains the missing success evidence.
2. **Given** a candidate whose source profile cannot be reconstructed from available artifacts, **When** promotion is requested, **Then** no output profile is created.

### Edge Cases

- The requested objective is absent from the ranking artifact.
- The ranking artifact references a candidate id not present in candidate aggregates.
- The top candidate has zero successful repetitions or a non-zero failure rate above the allowed promotion threshold.
- The output path already exists and overwrite has not been explicitly allowed.
- The ranking artifact was produced by an older format that lacks optional flag metadata.
- The source sweep artifacts are ignored by git, so the generated profile must retain enough provenance to audit the recommendation later.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the operator to preview promotion from a ranking artifact and objective without writing a recommended profile.
- **FR-002**: System MUST select exactly one candidate: the highest-ranked candidate for the requested objective.
- **FR-003**: System MUST generate a reusable recommended serve profile containing the selected candidate's core serve settings and approved optional serve flags.
- **FR-004**: System MUST include promotion provenance with the ranking artifact path, objective, candidate id, source trial ids, source metrics, source sweep id, and generation timestamp.
- **FR-005**: System MUST refuse promotion when the requested objective is missing, the selected candidate is missing, the candidate has no successful repetitions, or source profile data cannot be reconstructed.
- **FR-006**: System MUST refuse to overwrite an existing recommended profile unless the operator explicitly allows replacement.
- **FR-007**: System MUST provide a human-readable promotion summary that can be reviewed separately from the generated profile.
- **FR-008**: System MUST keep promotion local-only and MUST NOT connect to the GX10 or mutate remote systems.
- **FR-009**: System MUST produce deterministic selected candidate data for the same ranking artifact and objective, excluding explicitly time-based provenance fields.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST optimize reuse of the best-known measured configuration for a chosen objective family.
- **ER-002**: Feature MUST require the ranking artifact, objective, source candidate id, source trial ids, metrics, profile settings, and optional flags as reproducibility inputs.
- **ER-003**: Feature MUST retain the generated recommended profile and promotion summary as raw local artifacts suitable for review and commit.
- **ER-004**: Feature MUST classify all actions as local-only and read-only with respect to the GX10.
- **ER-005**: Feature MUST support a dry-run preview before writing any recommended profile.

### Key Entities *(include if feature involves data)*

- **Promotion Request**: The operator's chosen ranking artifact, objective, output profile path, summary path, and overwrite preference.
- **Promotion Preview**: The selected candidate, metrics, source trials, proposed profile identity, and eligibility decision.
- **Recommended Profile**: A reusable serve profile derived from a ranked candidate, including core serve settings, optional flags, and provenance.
- **Promotion Summary**: A human-readable record of why the candidate was promoted and what evidence supports it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a ranking artifact with at least one successful candidate, the operator can preview the top candidate for an objective in under 10 seconds.
- **SC-002**: Given the same ranking artifact and objective, repeated previews identify the same candidate and same configuration 100% of the time.
- **SC-003**: Generated recommended profiles include 100% of selected candidate core serve settings and approved optional flags present in the source profile.
- **SC-004**: Invalid or incomplete ranking artifacts are rejected before output files are written in 100% of tested failure cases.
- **SC-005**: The promotion summary contains enough provenance for a reviewer to identify the source ranking artifact, objective, candidate id, and source trial ids without opening additional files.

## Assumptions

- The default promotion objective is balanced when the operator does not specify one.
- Recommended profiles are intended to be checked into version control, while live sweep artifacts remain ignored.
- Promotion uses existing ranking artifacts produced by this project and does not rerun benchmarks.
- The first recommended profile target is the Qwen3 Coder Next AWQ profile derived from the GX10 scheduler sweep winner.
