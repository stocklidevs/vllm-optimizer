# Feature Specification: Single User Performance Target

**Status**: Completed

**Created**: 2026-05-26

**Input**: User clarified that high concurrency improves aggregate throughput but does not necessarily improve one person's interactive experience, and requested a cockpit mode beside Balanced, Performance, Stability, and Tool Use for single-user performance.

## User Scenarios & Testing

### User Story 1 - Choose one-request responsiveness (Priority: P1)

As a cockpit user, I want a Single User Performance target, so I can tune for the feel of one active interactive request instead of maximum concurrent aggregate throughput.

**Why this priority**: The current Performance target favors total tokens/sec and can recommend high-concurrency recipes that are useful for serving many requests but confusing when the user wants the best Codex-like single-session experience.

**Independent Test**: Render the cockpit and verify the target selector exposes Single User Performance with copy that distinguishes responsiveness from aggregate throughput.

**Acceptance Scenarios**:

1. **Given** the cockpit target selector is visible, **When** the user reviews available objectives, **Then** Single User Performance appears as a first-class target.
2. **Given** the user selects Single User Performance, **When** the cockpit updates selected objective state, **Then** the promotion/report objective maps to a single-user objective rather than aggregate throughput.

### User Story 2 - Rank candidates for responsiveness (Priority: P1)

As an optimizer user, I want single-user rankings to prefer lower latency and stable one-request behavior, so the winner reflects interactive responsiveness.

**Why this priority**: Without a separate ranking objective, the new target would be only cosmetic and could still promote a throughput winner.

**Independent Test**: Rank synthetic candidate results where one candidate has lower latency but lower throughput, and verify the single-user objective chooses the lower-latency candidate.

**Acceptance Scenarios**:

1. **Given** two successful candidates where one is faster in aggregate throughput and the other has lower latency, **When** ranked for Single User Performance, **Then** the lower-latency candidate ranks first.
2. **Given** single-user ranking compares repeated candidates, **When** latency is similar, **Then** failure rate and variance are used before throughput as tie-breakers.

### User Story 3 - Provide an explicit single-user recipe (Priority: P2)

As a cockpit user, I want the tuning catalog to include an explicit single-user recipe, so advanced users can inspect the exact one-request sweep behind the target.

**Why this priority**: The objective-first cockpit hides micro-tweaks by default, but advanced users still need traceable recipe provenance.

**Independent Test**: Build the knob catalog and verify a Single User tuning area exists with concurrency-one prompt provenance and clear knob metadata.

**Acceptance Scenarios**:

1. **Given** the deterministic sweep configs are cataloged, **When** the catalog is built, **Then** a Single User family/area is available.
2. **Given** the single-user sweep is planned, **When** its benchmark plan is inspected, **Then** request concurrency is one and the single-user objective is present.

### Edge Cases

- If a report lacks a `single_user` ranking, promotion must still fail clearly through the existing ranking contract instead of silently falling back to throughput.
- If no profile data is loaded, the target card must still be visible and selectable.
- The feature must not change live GX10 execution gates, risky-session gates, or promotion gates.

## Requirements

### Functional Requirements

- **FR-001**: The cockpit target selector MUST include a Single User Performance target with user-facing copy that distinguishes it from aggregate throughput performance.
- **FR-002**: Selecting Single User Performance MUST map cockpit objective state to a `single_user` optimizer objective.
- **FR-003**: The sweep ranking layer MUST accept `single_user` as a supported objective.
- **FR-004**: The `single_user` objective MUST rank lower latency first, then lower failure rate and variance, then higher throughput as a tie-breaker.
- **FR-005**: A deterministic single-user Qwen sweep config MUST use request concurrency one and include the `single_user` objective.
- **FR-006**: The tuning-area catalog MUST classify the single-user recipe with clear display family, label, description, and knobs tuned.
- **FR-007**: Version metadata, README, changelog, SpecKit pointers, tests, and release checks MUST be updated.

### Experiment Requirements

- **ER-001**: The optimized objective family is single-user responsiveness.
- **ER-002**: Reproducibility inputs are the selected serve profile, concurrency-one prompt set, deterministic seed, repetitions, objectives, and explicit candidate overrides.
- **ER-003**: Raw sweep plan, preview, live results, ranking, report, and promotion artifacts remain retained through the existing artifact layout.
- **ER-004**: GX10 actions remain session-mutating only; no persistent Linux/NVIDIA/system tuning is introduced.
- **ER-005**: Dry-run plan and preview must remain available before live remote execution.

### Key Entities

- **Optimization Target**: A cockpit-level user intent such as Balanced, Performance, or Single User Performance.
- **Single User Objective**: A ranking objective that prioritizes one-request latency and stability over aggregate throughput.
- **Single User Sweep Recipe**: A deterministic sweep configuration using concurrency-one workload inputs.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user can identify and select Single User Performance from the cockpit target selector without opening advanced knobs.
- **SC-002**: Synthetic rankings prove that single-user objective selection can choose a lower-latency candidate even when another candidate has higher throughput.
- **SC-003**: The single-user sweep plan reports benchmark concurrency one and includes the `single_user` objective.
- **SC-004**: Focused tests, full tests, release check, and local cockpit validation pass.

## Assumptions

- Single-user performance means one active request, optimized for latency/responsiveness, not multi-request aggregate throughput.
- Existing concurrency-one prompt sets are the correct starting workload for the first single-user recipe.
- Tool-use scoring remains future work; this feature only adds the single-user target and objective.
