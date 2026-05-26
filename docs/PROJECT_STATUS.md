# Project Status

Last updated: 2026-05-26

Current release: 0.54.5

## What Exists

vLLM Optimizer is a local, deterministic optimization lab for the GX10. The
CLI remains the source of truth, and the cockpit is a controller and reporting
surface over the same artifacts.

The current system can:

- Generate deterministic vLLM sweep plans and previews.
- Run gated live sweeps against the GX10.
- Rank candidates for throughput, latency, balanced score, and single-user
  responsiveness.
- Produce report and release artifacts for cockpit consumption.
- Launch a local active cockpit with objective-first controls, live progress,
  report review, candidate selection, and gated promotion.
- Keep risky-session, live-run, session-tuning, and promotion actions explicit.

## Main User Workflows

Start the default aggregate-throughput cockpit:

```powershell
uv run vllm-optimizer cockpit-launch
```

Start the single-user responsiveness cockpit:

```powershell
uv run vllm-optimizer cockpit-launch --sweep config/sweeps/qwen-single-user-interactive.json --out-dir artifacts/controller/qwen-single-user
```

Run the verification gate before release or handoff:

```powershell
uv run pytest
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

## Current Safety Boundary

Live GX10 runs are session-scoped and gated. Persistent Linux, NVIDIA, kernel,
firmware, service, boot, or credential changes are still intentionally out of
scope until a dedicated safety and rollback spec exists.

## Latest Product Direction

The cockpit should stay objective-first:

- Casual use starts by choosing the outcome: Balanced, Performance, Single
  User, Stability, or Tool Use.
- Advanced users can open the recipe drawer for knob families, command hints,
  artifacts, reports, and gates.
- Reporting should explain the recommendation story: baseline, winner,
  improvement, risk, and next safe action.
- Promotion remains explicit and never automatic.
