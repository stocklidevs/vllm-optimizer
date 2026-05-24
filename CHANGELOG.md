# Changelog

## 0.53.2 - 2026-05-24

- Fixed the cockpit close-history flow so future `Load Report` and
  `Review Report` actions become visible and clickable again after a fresh run.
- Switched cockpit action buttons to delegated click handling so dynamic
  controller/tab transitions remain wired after page load.
- Added regression coverage for report loading after closing old run history.

## 0.53.1 - 2026-05-24

- Added a cockpit escape hatch for loaded report history so old runs can be
  closed locally without deleting artifacts.
- Kept `Start Optimization` visible when a loaded report is present, allowing a
  fresh optimization to begin from the same dashboard session.
- Reset the visible loaded-run progress copy when the old history is closed and
  added regression coverage for the stuck previous-run state.

## 0.53.0 - 2026-05-24

- Rebuilt the web cockpit around an objective-first command center with model,
  target, selected recipe, primary action, live progress, and decision-story
  panels.
- Moved micro-tweaks, tuning areas, command hints, reports, runs, sources, and
  promotion gates into a collapsed advanced recipe drawer.
- Preserved active controller hooks, progress reset behavior, target/profile
  selection, report review, and static command-copy fallback while replacing the
  old left/right rail default layout.

## 0.52.1 - 2026-05-24

- Fixed Start Optimization reset behavior so the visible pipeline percentage
  badge resets along with the progress bar when a new run begins from a loaded
  artifact state.

## 0.52.0 - 2026-05-24

- Added model/profile selection to the web cockpit, with static and active
  cockpit entrypoints accepting `--profile PROFILE.json`.
- Added local cockpit optimization target cards for Balanced, Performance,
  Stability, and Tool Use.
- Wired selected target state into the decision strip and primary flow while
  preserving existing optimizer ranking semantics for future target-aware
  scoring work.

## 0.51.2 - 2026-05-24

- Clarified first-open cockpit state when existing status/report artifacts are
  loaded, labeling history as `Loaded Artifact State` instead of implying that
  a fresh run has already completed.
- Changed report-ready pipeline rows from running language to review language
  when the page is only displaying loaded artifacts.

## 0.51.1 - 2026-05-24

- Fixed cockpit rendering for report artifacts whose `candidates` payload is a
  list instead of a mapping.
- Kept both overview analytics and Reports-tab visualizations populated for
  list-shaped candidate artifacts.

## 0.51.0 - 2026-05-24

- Added a premium cockpit analytics overview with a decision strip for selected
  workload, current winner, baseline improvement, safety decision, and next
  safe action.
- Added report-backed evidence charts for baseline vs winner throughput,
  latency/throughput position, stability context, and candidate failure heatmap.
- Upgraded the web cockpit visual system with graphite texture, restrained
  glass layers, metal-like rails, and denser first-viewport hierarchy.

## 0.50.9 - 2026-05-24

- Marked Spec 060 completed after the cockpit reset work was committed.
- Added a release-check guard that fails when a completed active SpecKit task
  list still leaves `spec.md` or `plan.md` in Draft/Implementing status.
- Extended release-check tests and docs coverage for SpecKit completion status.

## 0.50.8 - 2026-05-24

- Added pinned Playwright UI validation support with `npm ci` installation and
  npm audit verification.
- Reset cockpit progress, workflow, and flow-map state when Start Optimization
  begins from a report-loaded dashboard.
- Added Reports-tab continuation cards for review, confirmation, and promotion
  gates.
- Fixed false tab-refresh handling so non-refresh tab jumps do not reload.

## 0.50.7 - 2026-05-23

- Added an end-to-end cockpit flow map that explains the operational journey
  from Start Optimization through report review, confirmation, and promotion
  gates.
- Changed report-ready primary actions to open the Reports view instead of
  exposing unsupported confirmation controller endpoints.
- Disabled gated confirmation and promotion shell buttons so manual gates stay
  visible without pretending they are runnable server calls.

## 0.50.6 - 2026-05-23

- Added a `Review Report` next action after report generation.
- Active cockpit rendering now auto-loads generated `out_dir/report.json`
  artifacts and can reload directly into the Reports tab.

## 0.50.5 - 2026-05-23

- Synced the cockpit pipeline progress with completed controller job results so
  finished runs no longer leave the pipeline at the initial 8% state.
- Added a local `report` controller action and moved the next action to
  `Load Report` after run completion.

## 0.50.4 - 2026-05-23

- Added live right-rail execution feedback for active cockpit jobs, including
  progress and elapsed-time updates.
- Added heartbeat progress to active controller jobs while long-running
  optimization work is still in progress.

## 0.50.3 - 2026-05-23

- Replaced primary cockpit `Generate Plan` calls-to-action with
  `Start Optimization`.
- Kept Plan visible as an internal pipeline progress stage for artifact
  traceability.

## 0.50.2 - 2026-05-23

- Removed deprecated standalone `Safety Gates` and `Controller` panels from the
  cockpit right rail.
- Moved controller feedback into the command shell so action status appears next
  to the command being run.

## 0.50.1 - 2026-05-23

- Fixed cockpit family filters so they update the left-rail tuning-area selector
  and the detailed Tuning Areas tab together.
- Added left-rail empty-state and auto-selection behavior when a family filter
  is applied.

## 0.50.0 - 2026-05-23

- Added an automatic pipeline progress panel to `web-cockpit` with one primary
  Start Optimization flow.
- Reframed Plan, Preview, Run, Report, and Confirm as internal stages while
  preserving explicit live execution and promotion gates.
- Added per-stage status rows and an overall progress bar derived from existing
  status/report artifacts.

## 0.49.0 - 2026-05-18

- Added user-facing tuning-area labels and knobs-tuned metadata to the knob
  catalog while preserving internal group IDs and config filenames.
- Updated the cockpit left rail from passive knob-group cards to selectable
  tuning areas.
- Hid internal history terms such as "rerun" from FP8 user-facing labels.

## 0.48.0 - 2026-05-18

- Redesigned `web-cockpit` around a guided six-step mission-control workflow.
- Added a Next Action panel, active-step command shell, and clearer locked
  safety states for Plan, Preview, Run, Report, Confirm, and Promote.
- Kept the cockpit deterministic and dependency-free while preserving local
  controller API hooks and static command-copy fallback.

## 0.47.0 - 2026-05-18

- Added `cockpit-launch`, a one-command launcher that generates standard
  cockpit artifacts and starts the active localhost cockpit.
- Added launcher defaults for the small Qwen sweep, GX10 local/example config,
  knob catalog, control manifest, run index, and active controller output dir.

## 0.46.0 - 2026-05-17

- Added active cockpit job status for controller actions, including progress
  percentage, polling, and cancel-request state.
- Added an Operation Result panel with kid-simple "what happened", "what it
  means", and "next step" guidance.
- Replaced vague running feedback with progress UI and honest cancellation
  messaging for in-flight controller jobs.

## 0.45.0 - 2026-05-16

- Added `cockpit-server`, a dependency-free localhost controller that serves
  the cockpit and runs Plan/Preview through local API endpoints.
- Added active controller fetch hooks with command-copy fallback, while keeping
  Run gated by explicit browser confirmation.
- Added cockpit question-mark help and a How to Use tab explaining Plan,
  Preview, Run, Report, Confirm, and Promote.

## 0.44.1 - 2026-05-16

- Fixed `web-cockpit` controller buttons so they copy deterministic CLI
  commands or show the command inline when clipboard access is unavailable.
- Kept browser-side execution and promotion gated while removing dead disabled
  controller placeholders.

## 0.44.0 - 2026-05-16

- Added a gated Promotion tab to `web-cockpit` with recommendation state,
  candidate/objective details, promotion gate metadata, and deterministic CLI
  command hints.
- Kept browser-side promotion disabled and artifact-driven.

## 0.43.0 - 2026-05-16

- Added the `cockpit-run` command for confirmed live-run control through the
  existing deterministic optimizer pipeline.
- Required `--confirm-live-run`, preserved `config/` and `artifacts/` path
  gates, and kept promotion disabled for cockpit run control.

## 0.42.0 - 2026-05-16

- Added the `cockpit-preview` command to generate local sweep plan, preview,
  and controller result artifacts for the web cockpit.
- Preserved controller safety by requiring sweeps under `config/`, outputs
  under `artifacts/`, retaining risky-session preview blocks, and avoiding live
  GX10 execution or promotion.

## 0.41.0 - 2026-05-16

- Added the `run-browser` command to index local optimizer artifact directories
  and generate JSON/HTML run browser outputs.
- Added optional `--run-index` support to `web-cockpit` with a Runs tab for
  summaries, rankings, canonical reports, execution status, and result files.

## 0.40.0 - 2026-05-16

- Added richer `web-cockpit` report visuals for recommendation detail,
  candidate throughput and latency bars, failure summaries, rationale, and next
  actions.
- Kept report rendering canonical-artifact driven and read-only.

## 0.39.0 - 2026-05-16

- Added local-only `web-cockpit` interactions for tab switching, knob family
  filters, search, visible counts, and no-match empty states.
- Kept cockpit controller actions disabled and avoided npm dependencies.

## 0.38.0 - 2026-05-16

- Improved the `web-cockpit` mobile layout so the main Mission Control
  workspace appears before the long knob navigation rail on narrow screens.

## 0.37.0 - 2026-05-15

- Added the static `web-cockpit` mission-control interface for knob groups,
  pipeline manifests, execution status, canonical report summaries, safety
  gates, and disabled future controller controls.
- Added a high-tech cockpit layout while keeping the implementation standalone,
  local-only, and npm-free.
- Added tests for cockpit rendering, empty optional artifact states, and CLI
  generation.

## 0.36.0 - 2026-05-15

- Added release setup documentation for local install, safe previews, GX10
  config expectations, live sweep gates, promotion gates, and reporting.
- Added documentation tests that keep the setup guide, README link, and current
  changelog entry aligned with the package version.
- Captured recent release-polish commands including `artifact-contracts` and
  `release-check` in handoff documentation.

## 0.35.0 - 2026-05-15

- Added the `release-check` command for local repository readiness reports.
- Added checks for package version consistency, README badge freshness, active
  SpecKit files, artifact contract availability, release docs, and essential
  project files.
- Added JSON and Markdown release-check outputs for handoff and packaging.

## 0.34.0 - 2026-05-15

- Added the `artifact-contracts` command for release-facing artifact contract
  catalogs.
- Documented stable contract fields for canonical reports, execution status,
  knob group catalogs, and pipeline control manifests.
- Added JSON and Markdown contract references for future web UI consumers.

## 0.33.0 - 2026-05-15

- Added curated impactful sweep bundles for KV/cache memory tradeoffs and
  prefix/chunked-prefill behavior on tool/JSON workloads.
- Preserved risky-session gating for KV cache and block-size candidates.
- Added focused CLI coverage for safe and risky impactful sweep planning.

## 0.6.0 - 2026-05-13

- Added read-only vLLM flag discovery from the GX10 profile executable.
- Added Qwen safe flag policy and catalog generation for performance-relevant
  vLLM serve flags.
- Added parser, mock/live capture workflow, and SpecKit feature docs for flag
  cataloging.

## 0.5.0 - 2026-05-13

- Added expanded safe Qwen sweep configuration around the current 0.90/32768
  winner.
- Added local plan/preview tests for the expanded six-candidate,
  eighteen-trial repeated sweep.
- Added SpecKit feature docs for expanded Qwen sweep evaluation.

## 0.4.0 - 2026-05-13

- Added local run comparison reporting for baseline, sweep, and repeated sweep
  artifacts.
- Added JSON and Markdown report outputs with recommendations, baseline deltas,
  stability notes, failure counts, and artifact links.
- Added SpecKit feature docs for run comparison reporting.

## 0.3.0 - 2026-05-13

- Added deterministic Qwen parameter sweep planning, dry-run preview, live
  sequential sweep execution, and objective ranking.
- Added repeated top-two sweep stability analysis with candidate-level
  aggregation, spread metrics, failure-rate tracking, and baseline deltas.
- Added sample sweep configs for the small Qwen sweep and repeated top-two
  comparison.
- Added SpecKit feature docs for parameter sweep and repeated stability
  analysis.

## 0.2.0 - 2026-05-13

- Added read-only GX10 discovery over SSH.
- Added Qwen3 Coder Next serve profile and dry-run serve rendering.
- Added safe Qwen smoke serve lifecycle with cleanup verification.
- Added Qwen baseline benchmark with fixed prompts and summary metrics.
- Added CLI version output and README badges.

## 0.1.0 - 2026-05-13

- Initialized SpecKit project.
- Added deterministic experiment planning, dry-run action previews, fixture
  ranking, and artifact helpers.
