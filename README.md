# vLLM Optimizer

[![version](https://img.shields.io/badge/version-0.56.4-blue.svg)](pyproject.toml)
[![python](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](pyproject.toml)
[![tests](https://img.shields.io/badge/tests-pytest-green.svg)](tests)
[![SpecKit](https://img.shields.io/badge/SpecKit-enabled-purple.svg)](.specify)

Public alpha deterministic optimization lab for vLLM experiments. The project
can be evaluated locally without a GX10, while live runs remain gated behind an
ignored local SSH config.

Start here:

- [Setup Guide](docs/SETUP.md)
- [Optimization Results](docs/RESULTS.md)
- [Public Release Checklist](docs/PUBLIC_RELEASE.md)
- [Publication Checklist](docs/PUBLICATION_CHECKLIST.md)
- [Project Status](docs/PROJECT_STATUS.md)
- [Roadmap and Autonomy Rules](specs/000-project-roadmap-autonomy/spec.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [License](LICENSE)

The project is spec-driven with SpecKit and currently supports:

- Deterministic trial-plan generation from JSON experiment definitions.
- Dry-run remote action previews.
- Read-only GX10 discovery over SSH.
- Qwen3 Coder Next serve-profile rendering.
- Safe smoke serve lifecycle with preflight checks, readiness polling, one
  request, artifact capture, and cleanup.
- A small Qwen baseline benchmark with fixed prompts and summary metrics.
- Deterministic small Qwen parameter sweeps with dry-run previews and local
  ranking for throughput, latency, balanced, and single-user objectives.
- Repeated top-two sweep stability analysis with per-candidate aggregates,
  spread metrics, baseline deltas, and stability-aware rankings.
- Local comparison reports that summarize baseline, sweep, and repeated sweep
  artifacts into JSON and Markdown recommendations.
- Expanded safe Qwen sweep configuration for testing nearby GPU utilization
  and performance-mode candidates around the current winner.
- Read-only vLLM flag discovery and safe performance knob cataloging from the
  installed GX10 vLLM help output.
- Scheduler and prefill knob sweep support for approved vLLM serve flags such
  as batched tokens, sequence count, chunked prefill, and prefix caching.
- Local promotion of ranked sweep winners into reusable recommended serve
  profiles with provenance.
- Recommended-profile benchmark validation with a default decision report.
- Repeated A/B confirmation reports for original vs recommended profiles.
- Risk-tiered risky-session vLLM sweeps with explicit preview/run opt-in.
- Guarded risky-winner promotion that requires repeated A/B confirmation before
  the default recommended profile is updated.
- Workload-aware prompt sets and explicit high-impact sweep candidates for
  interactive coding, long coding, and tool/JSON workloads.
- Benchmark-side request concurrency with batch-duration throughput accounting
  and a confirmed concurrent interactive coding profile.
- Workload leaderboard reports that summarize live workload winners, promoted
  profiles, failed risky candidates, and next actions.
- FP8 KV cache rerun sweeps that expose the vLLM venv binary directory on
  remote `PATH` so helpers such as `ninja` are available to child processes.
- Concurrency saturation prompt sets, sweep configs, and local reports for
  mapping where concurrent interactive throughput flattens or destabilizes.
- A conservative `optimize-workload` pipeline MVP that orchestrates one sweep
  through plan, preview, explicit run, and report stages without auto-promotion.
- A local pipeline confirmation stage that turns the ranked winner into a
  candidate profile, aggregates repeated A/B summaries, and only writes a
  confirmed profile when `--allow-promotion` is explicitly provided.
- A full `optimize-workload` orchestration mode that runs the sweep, report,
  repeated current-vs-candidate confirmation benchmarks, A/B decision, and
  optional gated promotion from one deterministic pipeline command.
- Read-only Linux/NVIDIA/runtime system tuning discovery that captures current
  GX10 tuning state and classifies future knobs before any session or
  persistent tuning is attempted.
- Guarded session-only benchmark tuning profiles for shell-scoped environment
  variables and `ulimit` changes, with deterministic previews and explicit
  live-run opt-in.
- Repeated A/B confirmation for session tuning profiles against the same serve
  profile without tuning.
- Dry-run session tuning sweep plans and previews for comparing multiple
  shell-scoped runtime tuning variants before live execution.
- Live execution and ranking for session tuning sweeps, with explicit
  `--allow-session-tuning` gating and no promotion.
- Canonical machine-readable and Markdown reports that serve as the source of
  truth for future web dashboards without recomputing optimizer decisions.
- Static web report viewer generation from canonical report JSON, producing
  standalone browser-openable dashboards with no server or network assets.
- Local execution-status snapshots and static HTML progress dashboards for
  pipeline/run directories, including stages, trial counts, failures, and
  artifact availability.
- Deterministic tuning-area catalog and static selector preview for safe,
  risky, workload, concurrency, FP8, session tuning, and read-only discovery
  families.
- Pipeline control manifests for selected tuning areas, exposing ordered command
  stages, artifact targets, remote-action markers, and safety gates for future
  web orchestration.
- Curated impactful sweep bundles for KV/cache memory tradeoffs and
  prefix/chunked-prefill behavior on tool/JSON workloads.
- Release-facing artifact contract catalogs that document stable JSON fields,
  schema versions, producers, and dashboard consumers.
- Local release readiness checks for package version consistency, active
  SpecKit metadata, completed-spec status, release docs, artifact contracts,
  and essential files.
- A standalone high-tech `web-cockpit` interface that combines tuning areas,
  pipeline stages, execution status, report summaries, safety gates, and
  disabled future controller controls from deterministic artifacts.
- Local-only `web-cockpit` interactions for tab switching, tuning-area family
  filters, search, visible group counts, and no-match empty states.
- Rich `web-cockpit` report visuals for recommendation detail, candidate
  throughput and latency bars, failure summaries, rationale, and next actions.
- Local run browser indexes for optimizer artifacts, with a cockpit Runs tab
  for browsing summaries, rankings, canonical reports, execution status, and
  result files.
- Local cockpit preview control for generating sweep plans, dry-run previews,
  and controller result artifacts while preserving path and risky-session gates.
- Confirmed cockpit live-run control that invokes the deterministic pipeline
  only after an explicit live execution gate.
- A gated `web-cockpit` Promotion tab that shows recommendation state,
  confirmation-oriented command hints, and disabled promotion controls.
- A dependency-free `cockpit-server` that serves the cockpit on localhost,
  runs Plan/Preview through local API endpoints, and keeps Run gated.
- Active cockpit operation feedback with a progress bar, plain-language result
  cards, polling, and cancel requests for in-flight controller jobs.
- A one-command `cockpit-launch` shortcut that prepares standard cockpit
  artifacts and starts the active localhost cockpit.
- A guided mission-control cockpit layout with a six-step workflow, Next Action
  panel, active command shell, and clearer locked safety states.
- User-facing tuning-area labels, visible knobs-tuned metadata, and left-rail
  selection for the cockpit.
- Family filters that update both the left-rail tuning-area selector and the
  detailed Tuning Areas tab.
- Automatic pipeline progress UX that treats Plan, Preview, Run, Report, and
  Confirm as internal stages, while keeping live execution and promotion gates
  explicit.
- End-to-end cockpit flow mapping that shows runnable actions, report review,
  and manual confirmation/promotion gates without presenting unsupported gated
  stages as active server calls.
- Active cockpit state reset when Start Optimization begins from a report-loaded
  dashboard, plus Reports-tab continuation cards for confirmation and promotion
  gates.
- Premium cockpit analytics with an outcome-first decision strip, baseline vs
  winner comparison, latency/throughput map, stability band, and failure
  heatmap rendered from canonical report artifacts.
- Model/profile selection and local optimization target selection for
  Balanced, Performance, Single User, Stability, and Tool Use cockpit
  workflows.
- An objective-first cockpit command center that replaces the old left/right
  rail default with model, target, recipe, primary action, progress, and
  decision-story panels while hiding micro-tweaks in an advanced recipe drawer.
- Loaded cockpit run history can be closed locally, keeping old artifacts on
  disk while revealing a fresh Start Optimization path for the next run.
- Cockpit report actions remain recoverable after closing loaded history, so a
  later completed run can surface `Generate & Review Report` and open the
  Reports view automatically.
- The active cockpit can select a report candidate and exercise gated local
  promotion when launched with `--allow-promotion`; the default launcher now
  starts from the high-throughput Qwen C8 concurrency sweep.
- Active cockpit and `optimize-workload` report mode validate sweep artifact
  provenance so a reused output directory cannot show an old small-sweep
  50 tok/s report as the current C8 performance result.
- Active cockpit failures now persist a recent job/failure artifact and render
  likely cause, next steps, relevant artifact paths, and failed trial reasons
  instead of showing only a bare "Failed" state.
- The default C8 active cockpit now applies the sweep's declared risky-session
  allowance consistently, so curated high-impact recipes do not fail before
  any live trials start.
- Single-user performance is available as a cockpit target and deterministic
  sweep recipe. It uses a one-request interactive workload and ranks candidates
  by responsiveness instead of aggregate concurrent throughput.
- A local vLLM model catalog records Qwen, Gemma, GLM, Qwen 27B, and DeepSeek
  candidates with deterministic smoke plans, parser/template metadata, and
  model-aware readiness artifacts before any expensive sweeps run.
- New-model live runs can export session-scoped profile environment variables;
  the GLM profile also pins `--moe-backend triton` to avoid the GX10
  FlashInfer CUTLASS JIT dependency path during smoke readiness.
- Conservative safe-profile sweep recipes are available for Gemma 4 E4B IT,
  GLM 4.7 Flash, Qwen3.6 27B, Qwen3.5 27B, and DeepSeek Coder V2 Lite
  Instruct, with first GX10 baseline and ranking results recorded in the
  project status handoff.
- The multi-model workflow documents one-model-at-a-time cache hygiene with a
  dedicated optimizer `HF_HOME` and explicit cleanup notes for stale model
  files on the GX10.

Persistent Linux/NVIDIA tuning is intentionally not implemented yet. It will be
handled by separate specs with explicit safety gates.

## Quickstart

See the [Setup Guide](docs/SETUP.md) for local installation, GX10 config
expectations, safe first commands, and release checks. See
[Project Status](docs/PROJECT_STATUS.md) for the current release state,
main workflows, and safety boundary.

```powershell
uv sync
uv run vllm-optimizer --version
uv run pytest
```

## Local Demo

```powershell
uv run vllm-optimizer plan --experiment tests/fixtures/experiments/throughput.json --out artifacts/demo/trial-plan.json
uv run vllm-optimizer dry-run --plan artifacts/demo/trial-plan.json --out artifacts/demo/dry-run.json --allow-blocked-preview
uv run vllm-optimizer rank --plan artifacts/demo/trial-plan.json --results tests/fixtures/results/throughput.jsonl --out artifacts/demo/report.json
uv run vllm-optimizer discover --config tests/fixtures/discovery/local.gx10.mock.json --executor mock --mock-results tests/fixtures/discovery/mock_outputs.json --out artifacts/discovery/mock
uv run vllm-optimizer serve-plan --profile config/profiles/qwen3-coder-next-awq.json --out artifacts/demo/qwen-serve-plan.json
uv run vllm-optimizer model-catalog --catalog config/model-catalog.json --out artifacts/models/catalog.json
uv run vllm-optimizer model-smoke-plan --catalog config/model-catalog.json --model gemma-4-e4b-it --out artifacts/models/gemma-4-e4b-it/smoke-plan.json
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-baseline/plan.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-small-sweep.json --out artifacts/sweeps/qwen-small/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-small/plan.json --out artifacts/sweeps/qwen-small/preview.json
```

## GX10 Workflows

Create an ignored local config from the example and set the real SSH
destination/redaction values:

```powershell
Copy-Item config/gx10.example.json config/local.gx10.json
```

Read-only discovery:

```powershell
uv run vllm-optimizer discover --config config/local.gx10.json --executor ssh --out artifacts/discovery/gx10-live
uv run vllm-optimizer system-tuning-discover --config config/local.gx10.json --executor ssh --out artifacts/system-tuning/gx10-live
uv run vllm-optimizer session-tuning-preview --profile config/session-tuning/qwen-runtime-env.json --catalog artifacts/system-tuning/gx10-live/catalog.json --out artifacts/session-tuning/qwen-runtime-env/preview.json
```

System tuning discovery is observational only. It records raw probe output,
parsed tuning entries, redaction metadata, and future action classifications
such as `read-only`, `session-mutating`, and `persistent-mutating`; it does not
change Linux, NVIDIA, GPU, CPU, memory, kernel, or runtime settings.

Session tuning profiles are limited to shell-scoped benchmark changes such as
`export` statements and `ulimit -n`. Benchmark plans and live runs require
`--allow-session-tuning` when a session tuning profile is supplied:

```powershell
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --prompts config/prompts/qwen-coding-interactive-concurrency-8.json --session-tuning config/session-tuning/qwen-runtime-env.json --allow-session-tuning --out artifacts/session-tuning/qwen-runtime-env/benchmark-plan.json
```

Repeated session tuning confirmation:

```powershell
uv run vllm-optimizer session-tuning-confirm --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --prompts config/prompts/qwen-coding-interactive-concurrency-8.json --session-tuning config/session-tuning/qwen-runtime-env.json --allow-session-tuning --repetitions 5 --current-label current-c8 --tuned-label runtime-env --out artifacts/session-tuning/qwen-runtime-env-confirmation --timeout-seconds 1200
```

Session tuning sweep planning:

```powershell
uv run vllm-optimizer session-tuning-sweep-plan --sweep config/session-tuning-sweeps/qwen-runtime-env-sweep.json --out artifacts/session-tuning-sweeps/qwen-runtime-env/plan.json
uv run vllm-optimizer session-tuning-sweep-preview --plan artifacts/session-tuning-sweeps/qwen-runtime-env/plan.json --out artifacts/session-tuning-sweeps/qwen-runtime-env/preview.json
uv run vllm-optimizer session-tuning-sweep-run --config config/local.gx10.json --plan artifacts/session-tuning-sweeps/qwen-runtime-env/plan.json --out artifacts/session-tuning-sweeps/qwen-runtime-env/live --allow-session-tuning --continue-on-failure --timeout-seconds 1200
uv run vllm-optimizer session-tuning-sweep-rank --plan artifacts/session-tuning-sweeps/qwen-runtime-env/plan.json --results artifacts/session-tuning-sweeps/qwen-runtime-env/live/results.jsonl --out artifacts/session-tuning-sweeps/qwen-runtime-env/live/ranking.json
```

Canonical report artifacts:

```powershell
uv run vllm-optimizer canonical-report --family session-tuning-sweep --label qwen-runtime-env --ranking artifacts/session-tuning-sweeps/qwen-runtime-env/live/ranking.json --summary artifacts/session-tuning-sweeps/qwen-runtime-env/live/summary.json --out artifacts/reports/qwen-runtime-env/canonical-report.json --markdown-out artifacts/reports/qwen-runtime-env/report.md
uv run vllm-optimizer report-viewer --report artifacts/reports/qwen-runtime-env/canonical-report.json --out artifacts/reports/qwen-runtime-env/viewer.html
```

Canonical reports are the source of truth for the future web interface. They
contain recommendation status, objective winners, candidate metrics,
chart-ready datasets, failure/exclusion state, and provenance links while
remaining local-only and deterministic from existing artifacts.

`report-viewer` turns a canonical report into a standalone HTML dashboard that
can be opened directly in a browser. It does not start a server and does not
load external assets.

Optimization pipeline MVP:

```powershell
uv run vllm-optimizer optimize-workload --mode plan --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/optimizer-runs/qwen-c8
uv run vllm-optimizer optimize-workload --mode preview --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/optimizer-runs/qwen-c8 --allow-risky-session-flags
uv run vllm-optimizer optimize-workload --mode run --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/optimizer-runs/qwen-c8 --config config/local.gx10.json --continue-on-failure --allow-risky-session-flags
uv run vllm-optimizer optimize-workload --mode report --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/optimizer-runs/qwen-c8 --allow-risky-session-flags
uv run vllm-optimizer optimize-workload --mode confirm --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/optimizer-runs/qwen-c8 --current-profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --prompts config/prompts/qwen-coding-interactive-concurrency-8.json --candidate-profile-out artifacts/optimizer-runs/qwen-c8/candidate-profile.json --confirmed-profile-out artifacts/optimizer-runs/qwen-c8/confirmed-profile.json --confirmation-repetitions 5 --original-label current-concurrent --recommended-label c8-saturation --allow-risky-session-flags
uv run vllm-optimizer optimize-workload --mode full --sweep config/sweeps/qwen-concurrency-saturation-c8.json --out artifacts/optimizer-runs/qwen-c8-full --config config/local.gx10.json --current-profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --prompts config/prompts/qwen-coding-interactive-concurrency-8.json --candidate-profile-out artifacts/optimizer-runs/qwen-c8-full/candidate-profile.json --confirmed-profile-out artifacts/optimizer-runs/qwen-c8-full/confirmed-profile.json --confirmation-repetitions 5 --original-label current-concurrent --recommended-label c8-saturation --continue-on-failure --allow-risky-session-flags
uv run vllm-optimizer execution-status --run-dir artifacts/optimizer-runs/qwen-c8-full --out artifacts/optimizer-runs/qwen-c8-full/execution-status.json --html-out artifacts/optimizer-runs/qwen-c8-full/execution-status.html
uv run vllm-optimizer knob-groups --config-root config --out artifacts/catalog/knob-groups.json --html-out artifacts/catalog/knob-groups.html
uv run vllm-optimizer pipeline-control --catalog artifacts/catalog/knob-groups.json --group-id qwen-concurrency-saturation-c8 --out artifacts/catalog/qwen-c8-control.json --html-out artifacts/catalog/qwen-c8-control.html
uv run vllm-optimizer artifact-contracts --out artifacts/catalog/artifact-contracts.json --markdown-out artifacts/catalog/artifact-contracts.md
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
uv run vllm-optimizer run-browser --artifacts-root artifacts --out artifacts/catalog/run-index.json --html-out artifacts/catalog/run-index.html
uv run vllm-optimizer cockpit-preview --sweep config/sweeps/qwen-prefix-prefill-tool-json.json --out-dir artifacts/controller/qwen-prefix-prefill-tool-json --result-out artifacts/controller/qwen-prefix-prefill-tool-json/controller-result.json
uv run vllm-optimizer cockpit-run --sweep config/sweeps/qwen-concurrency-saturation-c8.json --config config/local.gx10.json --out-dir artifacts/controller/qwen-c8-live --confirm-live-run
uv run vllm-optimizer cockpit-launch
uv run vllm-optimizer cockpit-launch --allow-promotion
uv run vllm-optimizer cockpit-launch --sweep config/sweeps/qwen-single-user-interactive.json --out-dir artifacts/controller/qwen-single-user
uv run vllm-optimizer cockpit-server --sweep config/sweeps/qwen-concurrency-saturation-c8.json --config config/local.gx10.json --out-dir artifacts/controller/qwen-c8-active --catalog artifacts/catalog/knob-groups.json --manifest artifacts/catalog/qwen-c8-control.json --run-index artifacts/catalog/run-index.json --allow-promotion
uv run vllm-optimizer web-cockpit --catalog artifacts/catalog/knob-groups.json --manifest artifacts/catalog/qwen-c8-control.json --status artifacts/optimizer-runs/qwen-c8-full/execution-status.json --report artifacts/reports/qwen-runtime-env/canonical-report.json --run-index artifacts/catalog/run-index.json --profile config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --out artifacts/cockpit/index.html
```

Pipeline boundaries:

The MVP records deterministic artifact paths and runs one existing sweep at a
time. It can generate plans, previews, live sweep outputs, rankings, and local
reports. It never promotes profiles automatically; promotion remains an
explicit confirmation-gated command.

`confirm` mode expects repeated benchmark summaries under
`<out>/confirmation/current-rN/summary.json` and
`<out>/confirmation/candidate-rN/summary.json`. It writes a candidate profile
and A/B confirmation report locally. Even when the report says
`switch-to-recommended`, the pipeline does not write the confirmed profile
unless `--allow-promotion` is included.

`full` mode is the end-to-end orchestration path. It requires `--config`
because it performs live GX10 vLLM sessions for both the sweep and repeated
confirmation benchmarks. It still does not write the confirmed profile unless
`--allow-promotion` is included and the A/B decision is
`switch-to-recommended`.

`execution-status` is local-only. It reads existing pipeline/run artifacts and
produces a progress snapshot plus optional standalone HTML dashboard for stage
state, trial counts, failures, and artifact availability.

`knob-groups` is also local-only. It reads repository configuration files and
generates a selectable tuning-area catalog with friendly labels, family, safety
tier, knobs tuned, opt-in requirement, command kind, and config path for each
optimization group.

`pipeline-control` is local-only as well. It turns a selected tuning area into a
UI-readable ordered control manifest with command hints, remote markers,
artifact targets, and explicit gates such as `--allow-risky-session-flags`,
`--allow-session-tuning`, and `--allow-promotion`.

`artifact-contracts` is a release-polish command. It documents stable
release-facing JSON artifacts such as canonical reports, execution status,
knob group catalogs, and pipeline control manifests so CLI and web consumers
can share the same contract assumptions.

`release-check` is local-only and read-only apart from its output files. It
checks version metadata, the README version badge, active SpecKit files,
artifact contract availability, release workflow docs, and essential project
files before packaging or handoff.

`run-browser` is local-only and read-only. It scans an artifact root for known
outputs such as `summary.json`, `ranking.json`, `canonical-report.json`,
`execution-status.json`, `pipeline-summary.json`, and `results.jsonl`, then
writes a JSON/HTML index for the cockpit Runs tab.

`cockpit-preview` is local-only and preview-only. It accepts sweep definitions
under `config/`, writes controller artifacts under `artifacts/`, preserves the
risky-session preview gate, and does not connect to the GX10, execute trials, or
promote profiles.

`cockpit-run` is the first remote-capable cockpit controller command. It keeps
the same `config/` and `artifacts/` path envelope, requires
`--confirm-live-run`, delegates execution to the deterministic optimizer
pipeline in `run` mode, and never promotes profiles.

`cockpit-server` turns the cockpit into a local active app. It serves the UI on
localhost, lets Plan and Preview run through local API endpoints, and requires
an explicit browser confirmation before Run can call the remote-capable
controller. If the cockpit is opened without the server, controller buttons
fall back to command-copy behavior. Active operations show a progress bar and
plain-language result cards: what happened, what it means, and what to do next.
Cancel requests are recorded through the server; if remote work is already in a
non-interruptible step, the cockpit says that honestly instead of pretending it
stopped instantly.

`cockpit-launch` is the simplest way to start the cockpit. With no arguments it
uses `config/sweeps/qwen-concurrency-saturation-c8.json`, generates the knob
catalog, selected sweep control manifest, and run index, then starts the active
cockpit at `http://127.0.0.1:8787`. Optional flags can override the sweep,
config, output directory, host, and port. Add `--allow-promotion` only when you
want to test the local selected-candidate promotion write path.
Use `--sweep config/sweeps/qwen-single-user-interactive.json` when the goal is
one active user's interactive responsiveness rather than serving many
simultaneous requests. The Single User cockpit target maps to the
`single_user` ranking objective, which prioritizes lower latency and stable
one-request behavior before aggregate tokens/sec.
For curated risky-session recipes such as the default C8 sweep, the launcher
honors the sweep's checked-in `allow_risky_session_flags` setting and passes
that effective allowance to the active server. Safe-session overrides remain
strict unless the sweep definition or command line explicitly enables risky
session flags.

`web-cockpit` is the combined web interface. It now opens as an objective
command center: choose the model/profile, choose the optimization target,
review the selected recipe, and use one clear primary action. Automatic Plan,
Preview, Run, Report, and Confirm stages are shown as progress and provenance,
not as the main navigation model. The cockpit only interrupts the user for real
gates such as live GX10 execution, risky/session opt-in, and promotion.

Micro-tweaks are still available for power users. The advanced recipe drawer
exposes tuning areas, family filters, search, exact command hints, pipeline
artifacts, reports, run indexes, source paths, and promotion gates. Controller
buttons call the local server when served by `cockpit-server`, or copy
deterministic CLI commands when opened as static HTML. Browser-side execution
and promotion remain explicitly gated, and unsupported confirmation or
promotion stages are rendered as review/gate actions rather than active server
calls.

Reports read as a decision story: baseline, winner, improvement, risk, and the
next safe action. Starting a new optimization from a report-loaded dashboard
clears the previous progress and completed-stage state immediately, then
advances to `Generate & Review Report` when the new run completes. Report
generation opens the advanced Reports view automatically so the freshly
generated artifact is visible. Reports also expose selectable candidate cards;
when the cockpit was launched with `--allow-promotion`, the Promotion action
writes the selected candidate profile artifact under the cockpit output
directory. The runtime cockpit remains dependency-free; Playwright is pinned as
a dev-only UI QA dependency, installed with `npm ci`, and checked with
`npm audit`.

The cockpit only auto-loads implicit reports from its output directory when
those artifacts match the configured sweep. If you switch from one sweep to
another while reusing an output directory, old reports are hidden and report
mode fails loudly with a stale-artifact message instead of presenting the wrong
winner. Start a new optimization or use a sweep-specific `--out-dir` to produce
fresh report artifacts.

When an active cockpit job fails, the server writes `controller-last-job.json`
and `controller-failure.json` under the cockpit output directory. The operation
panel reloads recent failed or running job state from the server and shows a
plain-language likely cause, first failed-trial reason when available, next
steps, and the artifact paths to inspect.

If the cockpit opens on an older loaded report, use `Close Loaded Run` to hide
that history in the current browser session and return the dashboard to a fresh
ready state. This does not delete report, status, or run artifacts; it only
prevents an old run from blocking the next `Start Optimization` action. Future
run results can still restore `Generate & Review Report` actions in that same
browser session.

Smoke serve:

```powershell
uv run vllm-optimizer smoke-serve-plan --profile config/profiles/qwen3-coder-next-awq.json --out artifacts/smoke/qwen/plan.json
uv run vllm-optimizer smoke-serve --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --out artifacts/smoke/qwen --timeout-seconds 1200
```

Model-aware smoke checks:

```powershell
uv run vllm-optimizer model-catalog --catalog config/model-catalog.json --out artifacts/models/catalog.json
uv run vllm-optimizer model-smoke-plan --catalog config/model-catalog.json --model gemma-4-e4b-it --out artifacts/models/gemma-4-e4b-it/smoke-plan.json
uv run vllm-optimizer model-smoke-run --catalog config/model-catalog.json --model gemma-4-e4b-it --config config/local.gx10.json --out artifacts/models/gemma-4-e4b-it/live --timeout-seconds 1200 --confirm-live-run
```

Baseline benchmark:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-baseline --timeout-seconds 1200
```

Parameter sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-small-sweep.json --out artifacts/sweeps/qwen-small/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-small/plan.json --out artifacts/sweeps/qwen-small/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-small/plan.json --out artifacts/sweeps/qwen-small/live --timeout-seconds 1200 --continue-on-failure
```

Repeated top-two stability sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-top2-repeated.json --out artifacts/sweeps/qwen-top2-repeated/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-top2-repeated/plan.json --out artifacts/sweeps/qwen-top2-repeated/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-top2-repeated/plan.json --out artifacts/sweeps/qwen-top2-repeated/live --timeout-seconds 1200 --continue-on-failure
```

Expanded safe Qwen sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-expanded-safe.json --out artifacts/sweeps/qwen-expanded-safe/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-expanded-safe/plan.json --out artifacts/sweeps/qwen-expanded-safe/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-expanded-safe/plan.json --out artifacts/sweeps/qwen-expanded-safe/live --timeout-seconds 1200 --continue-on-failure
```

Scheduler knob sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-scheduler-safe.json --out artifacts/sweeps/qwen-scheduler-safe/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-scheduler-safe/plan.json --out artifacts/sweeps/qwen-scheduler-safe/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-scheduler-safe/plan.json --out artifacts/sweeps/qwen-scheduler-safe/live --timeout-seconds 1200 --continue-on-failure
```

Latest GX10 scheduler sweep result:

```text
Best balanced candidate: gpu_memory_utilization=0.90, max_model_len=32768,
max_num_batched_tokens=4096, max_num_seqs=16, enable_chunked_prefill=true,
enable_prefix_caching=false, performance_mode=interactivity

Mean latency: 1004.0 ms
Throughput: 48.16 tokens/sec
Failures: 0/3 repetitions
```

Rank completed or fixture sweep results:

```powershell
uv run vllm-optimizer sweep-rank --plan artifacts/sweeps/qwen-small/plan.json --results artifacts/sweeps/qwen-small/live/results.jsonl --out artifacts/sweeps/qwen-small/ranking.json
```

Comparison report:

```powershell
uv run vllm-optimizer report --baseline artifacts/benchmarks/qwen-baseline/summary.json --sweep-ranking artifacts/sweeps/qwen-small/live/ranking.json --repeated-ranking artifacts/sweeps/qwen-top2-repeated/live/ranking.json --out artifacts/reports/qwen-comparison.json --markdown-out artifacts/reports/qwen-comparison.md
```

vLLM flag catalog:

```powershell
uv run vllm-optimizer flag-catalog --policy config/vllm-flags/qwen-safe-policy.json --help-file tests/fixtures/vllm/serve-help.txt --out artifacts/vllm-flags/fixture/catalog.json
uv run vllm-optimizer flag-catalog-capture --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --policy config/vllm-flags/qwen-safe-policy.json --out artifacts/vllm-flags/gx10-qwen --executor ssh
```

Promote a ranked winner to a recommended profile:

```powershell
uv run vllm-optimizer promote-preview --ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --objective balanced --out artifacts/promotions/qwen-scheduler-safe-preview.json
uv run vllm-optimizer promote-profile --ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-recommended.json --summary-out artifacts/promotions/qwen3-coder-next-awq-recommended.md
uv run vllm-optimizer serve-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --out artifacts/promotions/recommended-serve-plan.json
```

Validate the recommended profile as a default candidate:

```powershell
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-recommended/plan.json
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-recommended --timeout-seconds 1200
uv run vllm-optimizer recommended-report --baseline artifacts/benchmarks/qwen-baseline/summary.json --recommended artifacts/benchmarks/qwen-recommended/summary.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --source-ranking artifacts/sweeps/qwen-scheduler-safe/live/ranking.json --out artifacts/reports/qwen-recommended-default.json --markdown-out artifacts/reports/qwen-recommended-default.md
```

Repeated A/B confirmation:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r3 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r3 --timeout-seconds 1200
uv run vllm-optimizer ab-report --original-label original --recommended-label recommended --original-summaries artifacts/benchmarks/qwen-ab/original-r1/summary.json artifacts/benchmarks/qwen-ab/original-r2/summary.json artifacts/benchmarks/qwen-ab/original-r3/summary.json --recommended-summaries artifacts/benchmarks/qwen-ab/recommended-r1/summary.json artifacts/benchmarks/qwen-ab/recommended-r2/summary.json artifacts/benchmarks/qwen-ab/recommended-r3/summary.json --prompt-set-id qwen-baseline-v1 --out artifacts/reports/qwen-ab-confirmation.json --markdown-out artifacts/reports/qwen-ab-confirmation.md
```

Risky-session knob sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-risky-session-small.json --out artifacts/sweeps/qwen-risky-session-small/plan.json --allow-risky-session-flags
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-risky-session-small/plan.json --out artifacts/sweeps/qwen-risky-session-small/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-risky-session-small/plan.json --out artifacts/sweeps/qwen-risky-session-small/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Risky winner confirmation and guarded promotion:

```powershell
uv run vllm-optimizer promote-profile --ranking artifacts/sweeps/qwen-risky-session-small/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-risky-winner.json --summary-out artifacts/promotions/qwen3-coder-next-awq-risky-winner.md --profile-id qwen3-coder-next-awq-risky-winner
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r3 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r3 --timeout-seconds 1200
uv run vllm-optimizer ab-report --original-label current-recommended --recommended-label risky-winner --original-summaries artifacts/benchmarks/qwen-risky-ab/current-r1/summary.json artifacts/benchmarks/qwen-risky-ab/current-r2/summary.json artifacts/benchmarks/qwen-risky-ab/current-r3/summary.json --recommended-summaries artifacts/benchmarks/qwen-risky-ab/risky-r1/summary.json artifacts/benchmarks/qwen-risky-ab/risky-r2/summary.json artifacts/benchmarks/qwen-risky-ab/risky-r3/summary.json --prompt-set-id qwen-baseline-v1 --out artifacts/reports/qwen-risky-winner-confirmation.json --markdown-out artifacts/reports/qwen-risky-winner-confirmation.md
uv run vllm-optimizer promote-confirmed-profile --confirmation-report artifacts/reports/qwen-risky-winner-confirmation.json --ranking artifacts/sweeps/qwen-risky-session-small/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-recommended.json --summary-out artifacts/promotions/qwen3-coder-next-awq-recommended-risky-confirmed.md --profile-id qwen3-coder-next-awq-recommended --expected-recommended-label risky-winner --force
```

Latest GX10 risky winner confirmation:

```text
Decision: switch-to-recommended
Current recommended mean latency: 1008.444 ms
Risky winner mean latency: 992.667 ms
Latency delta: -15.778 ms (-1.565%)
Current recommended throughput: 47.948 tokens/sec
Risky winner throughput: 48.717 tokens/sec
Throughput delta: +0.770 tokens/sec (+1.605%)
Failures: 0/9 requests for each profile
Confirmed default flag addition: block_size=16
```

Workload-aware high-impact sweeps:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-interactive.json --out artifacts/sweeps/qwen-high-impact-interactive/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-interactive/plan.json --out artifacts/sweeps/qwen-high-impact-interactive/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-long.json --out artifacts/sweeps/qwen-high-impact-long/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-long/plan.json --out artifacts/sweeps/qwen-high-impact-long/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-tool-json.json --out artifacts/sweeps/qwen-high-impact-tool-json/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-tool-json/plan.json --out artifacts/sweeps/qwen-high-impact-tool-json/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-high-impact-interactive/plan.json --out artifacts/sweeps/qwen-high-impact-interactive/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Concurrent interactive sweep:

```powershell
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-coding-interactive-concurrent.json --out artifacts/benchmarks/qwen-concurrency/plan.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-interactive-concurrent.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Impactful sweep bundles:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-kv-cache-memory-tradeoff.json --out artifacts/sweeps/qwen-kv-cache-memory-tradeoff/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-kv-cache-memory-tradeoff/plan.json --out artifacts/sweeps/qwen-kv-cache-memory-tradeoff/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-prefix-prefill-tool-json.json --out artifacts/sweeps/qwen-prefix-prefill-tool-json/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-prefix-prefill-tool-json/plan.json --out artifacts/sweeps/qwen-prefix-prefill-tool-json/preview.json
```

The KV/cache memory tradeoff bundle intentionally includes risky-session flags
such as `block_size` and `kv_cache_dtype`, so previews and live runs stay gated
until `--allow-risky-session-flags` is explicitly provided. The tool/JSON
prefix-prefill bundle stays inside safe-session scheduler and prefill flags.

Latest GX10 concurrent interactive confirmation:

```text
Best concurrent profile: gpu_memory_utilization=0.92, block_size=16,
max_num_batched_tokens=4096, max_num_seqs=16, performance_mode=interactivity

Current concurrent default: 6866.111 ms, 94.884 tokens/sec
Concurrent winner: 6670.778 ms, 96.560 tokens/sec
Delta: -195.333 ms (-2.845%), +1.676 tokens/sec (+1.766%)
Failures: 0/9 requests per side
```

Concurrency saturation sweep:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-concurrency-saturation-c1.json --out artifacts/sweeps/qwen-concurrency-saturation-c1/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-concurrency-saturation-c1/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c1/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-concurrency-saturation-c1/plan.json --out artifacts/sweeps/qwen-concurrency-saturation-c1/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
uv run vllm-optimizer saturation-report --ranking 1=artifacts/sweeps/qwen-concurrency-saturation-c1/live/ranking.json 2=artifacts/sweeps/qwen-concurrency-saturation-c2/live/ranking.json 3=artifacts/sweeps/qwen-high-impact-interactive-concurrent/live/ranking.json 4=artifacts/sweeps/qwen-concurrency-saturation-c4/live/ranking.json 6=artifacts/sweeps/qwen-concurrency-saturation-c6/live/ranking.json 8=artifacts/sweeps/qwen-concurrency-saturation-c8/live/ranking.json --out artifacts/reports/qwen-concurrency-saturation.json --markdown-out artifacts/reports/qwen-concurrency-saturation.md
```

Latest GX10 concurrency saturation result:

```text
Best current saturation candidate: concurrency=8
Profile: gpu_memory_utilization=0.90, block_size=16,
max_num_batched_tokens=4096, max_num_seqs=16, performance_mode=interactivity

c1: 41.100 tokens/sec, 5879.333 ms, failures 0/2
c2: 59.429 tokens/sec, 5932.000 ms, failures 0/2
c3: 96.667 tokens/sec, 6717.167 ms, failures 0/2
c4: 97.437 tokens/sec, 6615.500 ms, failures 0/2
c6: 97.445 tokens/sec, 6601.000 ms, failures 0/2
c8: 98.415 tokens/sec, 6611.500 ms, failures 0/2

Next action: repeated confirmation for concurrency=8 before promotion.
```

Latest c8 concurrency confirmation:

```text
Decision: switch-to-recommended
Prompt set: qwen-coding-interactive-concurrency-8-v1

Previous concurrent profile: 6766.867 ms, 96.041 tokens/sec
Confirmed c8 profile: 6644.200 ms, 97.683 tokens/sec
Delta: -122.667 ms (-1.813%), +1.642 tokens/sec (+1.710%)
Failures: 0/5 repetitions per side

Confirmed concurrent profile: gpu_memory_utilization=0.90, block_size=16,
max_num_batched_tokens=4096, max_num_seqs=16, performance_mode=interactivity
```

Workload leaderboard:

```powershell
uv run vllm-optimizer workload-report --workload interactive=artifacts/sweeps/qwen-high-impact-interactive/live/ranking.json long=artifacts/sweeps/qwen-high-impact-long/live/ranking.json tool-json=artifacts/sweeps/qwen-high-impact-tool-json/live/ranking.json concurrent-interactive=artifacts/sweeps/qwen-high-impact-interactive-concurrent/live/ranking.json fp8-interactive=artifacts/sweeps/qwen-fp8-rerun-interactive/live/ranking.json fp8-long=artifacts/sweeps/qwen-fp8-rerun-long/live/ranking.json fp8-tool-json=artifacts/sweeps/qwen-fp8-rerun-tool-json/live/ranking.json --promoted-profile concurrent-interactive=config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --out artifacts/reports/qwen-workload-leaderboard.json --markdown-out artifacts/reports/qwen-workload-leaderboard.md
```

Latest workload leaderboard says:

```text
Promoted profile: qwen3-coder-next-awq-concurrent-recommended
Sequential interactive winner: block_size=32, watch only
Long coding winner: block_size=32 plus 8192 batched tokens, watch only
Tool/JSON winner: smaller batch/seq envelope, watch only
Historical high-impact FP8 failures still show the old missing-ninja blocker
FP8 rerun labels show plain fp8 completed on all workloads
```

FP8 KV cache rerun:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-fp8-rerun-interactive.json --out artifacts/sweeps/qwen-fp8-rerun-interactive/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-fp8-rerun-interactive/plan.json --out artifacts/sweeps/qwen-fp8-rerun-interactive/preview.json
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-fp8-rerun-interactive/plan.json --out artifacts/sweeps/qwen-fp8-rerun-interactive/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Latest GX10 FP8 rerun result:

```text
plain fp8 interactive: 6080.833 ms, 39.770 tokens/sec, 0/2 failures
plain fp8 long: 20561.000 ms, 36.008 tokens/sec, 0/2 failures
plain fp8 tool-json: 5616.167 ms, 40.297 tokens/sec, 0/2 failures
fp8_e5m2: rejected by vLLM for this FP8 checkpoint
```

## Safety

- Local secrets belong in ignored files such as `config/local.gx10.json`.
- Live SSH commands use batch-mode authentication.
- Discovery probes are read-only.
- Smoke and benchmark commands are session-mutating and include preflight
  checks plus cleanup verification.
- Sweep live execution is sequential and session-mutating only.
- Promotion commands are local-only and do not contact the GX10.
- Confirmed promotion refuses to update the default profile unless the repeated
  A/B report approves switching to the candidate.
- Risky-session sweeps are blocked by default and require explicit preview/run
  opt-in; persistent/system flags remain blocked.
- Generated artifacts under `artifacts/` are ignored by git.

## SpecKit

Project governance and feature design live under `.specify/` and `specs/`.
Current feature specs:

- `specs/001-vllm-optimization-lab/spec.md`
- `specs/002-gx10-readonly-discovery/spec.md`
- `specs/003-qwen-smoke-serve/spec.md`
- `specs/004-qwen-baseline-benchmark/spec.md`
- `specs/005-qwen-parameter-sweep/spec.md`
- `specs/006-repeated-sweep-stability/spec.md`
- `specs/007-run-comparison-report/spec.md`
- `specs/008-expanded-qwen-sweep/spec.md`
- `specs/009-vllm-flag-catalog/spec.md`
- `specs/010-scheduler-knob-sweep/spec.md`
- `specs/011-promote-winner-profile/spec.md`
- `specs/012-recommended-profile-benchmark/spec.md`
- `specs/013-ab-benchmark-confirmation/spec.md`
- `specs/014-risky-session-knobs/spec.md`
- `specs/015-risky-winner-confirmation/spec.md`
- `specs/016-workload-aware-sweeps/spec.md`
- `specs/017-benchmark-concurrency/spec.md`
- `specs/018-workload-leaderboard/spec.md`
- `specs/019-fp8-ninja-rerun/spec.md`
- `specs/020-concurrency-saturation/spec.md`
- `specs/021-live-concurrency-saturation/spec.md`
- `specs/022-confirm-c8-saturation/spec.md`
- `specs/023-optimization-pipeline-mvp/spec.md`
