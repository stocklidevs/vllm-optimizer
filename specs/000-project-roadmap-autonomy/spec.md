# Project Roadmap and Autonomy Agreement

**Status**: Active project guidance

**Created**: 2026-05-15

**Purpose**: Record the shared end-state vision, execution sequence, and decision gates so Codex can continue feature-by-feature with minimal user input while preserving safety, traceability, and SpecKit discipline.

## End-State Objective

Build a deterministic vLLM optimization system for the GX10 that can:

- Tune vLLM and related runtime knob families through reproducible experiment plans.
- Execute safe live sweeps and confirmation benchmarks over SSH.
- Rank candidates by objective families such as throughput, latency, stability, tool/JSON behavior, and balanced score.
- Produce canonical reports that explain winners, baselines, failures, and next actions.
- Provide a polished web interface where users can select knob groups, monitor execution, inspect progress, and explore graphical reports.
- Keep the automation auditable enough that every recommendation can be traced back to source artifacts.

## Product Architecture Decision

The project uses a hybrid architecture:

- The CLI and artifact layer are the deterministic source of truth.
- The web interface is a controller, monitor, and visual reporting surface over the same artifacts.
- Web dashboards must consume canonical reports and run metadata rather than independently recomputing optimizer decisions.
- Promotion or persistent tuning remains gated by explicit user opt-in and confirmation logic.

## Roadmap Phases

### Phase 1 - Canonical Reporting Artifacts

Create stable report artifacts for completed sweeps, session tuning sweeps, confirmation runs, and pipeline runs.

Expected outputs:

- Machine-readable report data for future dashboards.
- Human-readable Markdown decision summaries.
- Candidate ranking tables, recommendation status, objective summaries, metric spreads, failure counts, and provenance links.

### Phase 2 - Web Report Viewer

Build the first web UI around existing artifacts only.

Expected outputs:

- Run/report browser.
- Recommendation summary view.
- Ranking, throughput, latency, stability, and provenance visualizations.
- No live run control yet.

### Phase 3 - Web Execution Dashboard

Add execution feedback for live runs and pipeline stages.

Expected outputs:

- Current stage/status display.
- Per-trial progress and failure visibility.
- Artifact links as they are produced.
- Safe cancellation/status behavior if supported by the underlying runner.

### Phase 4 - Knob Group Selection UI

Let users choose which optimization families to run from the web interface.

Expected knob families:

- Safe vLLM serve parameters.
- Scheduler and prefill parameters.
- Concurrency and workload shape.
- Risky session-only vLLM flags.
- Session-scoped runtime/environment tuning.
- Read-only system discovery.
- Future persistent system tuning only after separate explicit safety specs.

### Phase 5 - Full Pipeline Control

Expose the existing deterministic pipeline through the web UI.

Expected outputs:

- Plan, preview, run, report, confirm, and gated promotion controls.
- Explicit safety gates for risky or mutating actions.
- Clear separation between recommended, confirmed, and promoted configurations.

### Phase 6 - More Impactful Knob Families

Continue expanding optimization beyond currently tested flags.

Candidate families:

- Batch/scheduler pressure points.
- KV cache and memory tradeoffs.
- Workload-specific prompt/concurrency mixes.
- Tool/JSON behavior and parser settings.
- Runtime environment settings that remain session-scoped.
- Persistent Linux/NVIDIA/system settings only after a dedicated safety and rollback design.

### Phase 7 - Release Polish

Make the project usable as a repeatable local tool.

Expected outputs:

- Stable commands and documentation.
- Versioned report contracts.
- Clear install/setup instructions.
- Example configs and safe defaults.
- Release notes and migration notes when report schemas or profile contracts change.

## Standing Execution Preferences

Unless the user explicitly redirects, Codex should:

- Use SpecKit for every major feature.
- Keep changes deterministic and artifact-driven.
- Prefer CLI/report foundations before web UI polish when shared logic is needed.
- Update documentation when behavior or user workflow changes.
- Update the package version when implementation changes affect user-facing behavior, commands, report contracts, or released workflows.
- Commit completed coherent units of work.
- Run focused tests for changed behavior and broader tests when shared modules or CLI surfaces change.
- Preserve existing user changes and avoid unrelated refactors.
- Continue spec-by-spec without asking for routine approval when requirements are already captured here or in the active feature spec.

## Autonomy Rules

Codex may proceed without additional user input when:

- The next task is an implementation, planning, documentation, test, or reporting step already implied by this roadmap or the active SpecKit feature.
- The work is local, reversible, and within the repository.
- Live GX10 runs use already-approved safety gates and existing SSH configuration.
- The action does not require persistent system changes or destructive file/git operations.

Codex must pause or ask before:

- Making persistent Linux, NVIDIA, firmware, kernel, boot, or system service changes on the GX10.
- Changing credentials, SSH identity, Tailscale settings, or remote access assumptions.
- Deleting user data, resetting git history, force-pushing, or overwriting unrelated user edits.
- Auto-promoting a profile or configuration without the explicit promotion gate required by the relevant spec.
- Choosing between materially different product directions that are not already decided here.
- Adding external hosted services, cloud dependencies, or network-facing deployment changes.

## Current Active Feature

The next implementation target is:

- `specs/031-canonical-reporting-artifacts/spec.md`

This roadmap should guide future specs, but it should not replace `.specify/feature.json` as the active feature pointer.

## Success Criteria

- A future Codex session can identify the end-state objective, current phase, autonomy rules, and decision gates without asking the user to restate them.
- Routine features can proceed from spec to plan to tasks to implementation to docs/version/commit with minimal user input.
- The web interface direction remains aligned with deterministic CLI artifacts rather than diverging into separate decision logic.
- Safety-sensitive actions remain explicitly gated.
