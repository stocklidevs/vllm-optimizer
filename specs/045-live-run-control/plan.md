# Implementation Plan: Live Run Control

## Summary

Add a confirmed live-run controller command that wraps the existing
`optimize-workload --mode run` behavior. The controller owns cockpit-facing
validation, artifact paths, and confirmation metadata; the optimizer pipeline
continues to own sweep execution, risky-session checks, and result/ranking
artifacts.

## Technical Context

- Language: Python 3.11
- Existing surfaces: `optimizer_pipeline`, `cockpit_controller`, CLI
- Test style: pytest unit and CLI integration tests
- Safety: local path gates plus explicit `--confirm-live-run`

## Architecture

- Extend `cockpit_controller.py` with:
  - `CockpitRunRequest`
  - `run_cockpit_live`
  - injectable pipeline runner for tests
- Extend CLI with `cockpit-run`.
- Reuse `OptimizerPipelineRequest(mode="run")`.
- Write `controller-result.json` under the selected artifact directory.

## Verification

- Focused controller and CLI tests.
- Version/release documentation tests.
- Full pytest suite.
