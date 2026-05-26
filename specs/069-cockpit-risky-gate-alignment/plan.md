# Implementation Plan: Cockpit Risky-Session Gate Alignment

**Status**: Completed

## Summary

Fix the default active cockpit failure where the C8 sweep was planned with
risky-session allowance but the active controller still rejected the run before
executing any trials.

## Architecture

- Resolve effective risky-session allowance in `cockpit-launch` from either the
  launcher flag or the selected sweep definition.
- Record effective risky-session allowance in pipeline safety metadata.
- Rebuild stored sweep plans when their safety allowance does not match the
  selected sweep's current effective allowance.
- Keep safe-session sweep overrides strict unless they explicitly declare or
  receive risky-session allowance.
- Add a specific failure-diagnostics branch for missing risky-session gates.

## Verification

- Red/green launcher tests for default C8 and safe-session override behavior.
- Red/green optimizer pipeline tests for effective safety metadata and stale
  safety-plan rebuilds.
- Red/green controller failure diagnostics test for the missing risky-session
  gate.
- Full pytest suite.
- Release check.
- Local cockpit validation with the active default C8 launcher.
