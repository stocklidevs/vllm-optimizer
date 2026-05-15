# Feature Specification: Impactful Sweep Bundles

**Feature Branch**: `036-impactful-sweep-bundles`

**Created**: 2026-05-15

**Status**: Draft

**Input**: Project roadmap Phase 6: expand optimization into more impactful knob families while preserving dry-run safety. Add curated sweep definitions for KV/cache memory tradeoffs and prefix/chunked-prefill tool/JSON behavior.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Plan KV/Memory Tradeoff Sweeps (Priority: P1)

As an optimizer user, I want a ready-to-plan sweep for KV cache and memory-related flags so that potentially impactful memory/performance tradeoffs can be tested with the existing safe preview and run flow.

**Why this priority**: KV/cache behavior can materially affect throughput, latency, and stability on constrained GPU memory.

**Independent Test**: Generate a sweep plan from the new config and verify candidate/trial counts, risky-session classification, and opt-in requirement.

### User Story 2 - Plan Tool/JSON Prefill Sweeps (Priority: P2)

As an optimizer user, I want a ready-to-plan sweep for prefix caching and chunked prefill on tool/JSON prompts so that structured-output workloads can be tuned separately from generic coding prompts.

**Why this priority**: Tool and structured JSON workloads are a target objective family for the final product.

**Independent Test**: Generate a sweep plan from the new config and verify it targets the tool/JSON prompt set and safe session flags.

### Edge Cases

- Risky KV cache candidates must remain blocked without explicit opt-in.
- Tool/JSON candidates must use the tool/JSON prompt set.
- Candidate counts should stay small enough for live GX10 validation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST include a KV/cache memory tradeoff sweep definition.
- **FR-002**: System MUST include a prefix/chunked-prefill tool/JSON sweep definition.
- **FR-003**: New sweeps MUST be compatible with existing `sweep-plan` and `sweep-preview` commands.
- **FR-004**: Risky KV/cache candidates MUST require explicit risky-session allowance.
- **FR-005**: New sweeps MUST use deterministic seeds and bounded candidate counts.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST define objective families for throughput, latency, and balanced ranking.
- **ER-002**: Feature MUST define reproducibility inputs through committed config files.
- **ER-003**: Feature MUST retain normal sweep artifacts through existing sweep workflows.
- **ER-004**: Feature MUST identify risky session mutations before live use.
- **ER-005**: Feature MUST support dry-run preview before live remote execution.

### Key Entities *(include if feature involves data)*

- **KV/Memory Sweep**: Risky-session sweep testing KV cache dtype and block/memory settings.
- **Tool/JSON Prefill Sweep**: Safe-session sweep testing prefix caching and chunked prefill behavior for structured workloads.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both new sweep definitions produce deterministic plans through `sweep-plan`.
- **SC-002**: The KV/cache sweep reports risky-session flags in preview unless opt-in is provided.
- **SC-003**: The tool/JSON sweep produces at least four candidates and uses `qwen-tool-json-v1`.
- **SC-004**: No live GX10 execution is required to validate the new sweep definitions.

## Assumptions

- Live execution of these sweeps remains a later explicit run step.
- The existing sweep engine continues to own validation and ranking.
