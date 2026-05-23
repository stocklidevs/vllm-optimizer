# Implementation Plan: Unified Start Optimization CTA

## Summary

Change the cockpit's main action model from explicit `Generate Plan` to a
single `Start Optimization` intent. Planning remains an internal stage shown in
progress and artifacts.

## Architecture

- Add helpers for the user-facing primary automatic action.
- Update right-rail next action rendering to use `Start Optimization` when the
  pipeline is ready to begin.
- Update the guided workspace command shell to show the automatic run command
  by default in the initial state.
- Keep `WORKFLOW_STEPS` intact for progress labels and traceability.
- Update tests, docs, version, and lockfile.

## Verification

- Focused cockpit and release-doc tests.
- Full pytest suite.
- Browser validation of generated cockpit HTML.
