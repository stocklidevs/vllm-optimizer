# Implementation Plan: One-Command Cockpit Launcher

## Summary

Add `cockpit-launch`, a convenience command that prepares standard cockpit
artifacts and starts the active cockpit server with sensible defaults.

## Technical Context

- Language: Python 3.11
- Dependencies: stdlib plus existing project modules only
- Existing modules: `knob_catalog`, `pipeline_control`, `run_browser`,
  `cockpit_server`

## Architecture

- Add `src/vllm_optimizer/cockpit_launcher.py`.
- Keep launch preparation testable separately from the blocking server loop.
- Wire `cockpit-launch` in `cli.py`.
- Defaults:
  - sweep: `config/sweeps/qwen-small-sweep.json`
  - config: `config/local.gx10.json` if present, else `config/gx10.example.json`
  - out-dir: `artifacts/controller/cockpit-active`
  - catalog: `artifacts/catalog/knob-groups.json`
  - manifest: `artifacts/catalog/<sweep-stem>-control.json`
  - run-index: `artifacts/catalog/run-index.json`

## Verification

- Focused launcher unit and CLI tests.
- Version/release docs tests.
- Full pytest suite.
