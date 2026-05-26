# Implementation Plan: Single User Performance Target

**Status**: Completed

## Summary

Add a first-class Single User Performance target for cockpit users who care
about one active request's responsiveness rather than aggregate concurrent
throughput.

## Architecture

- Add `single_user` to supported sweep objectives with latency-first ranking.
- Add a deterministic Qwen single-user sweep recipe that uses the existing
  concurrency-one interactive coding prompt set.
- Classify the recipe as a Single User tuning area in the deterministic knob
  catalog.
- Add a Single User target card to the objective-first cockpit and map it to
  the `single_user` objective for promotion/report intent.
- Keep live execution, risky-session allowance, and promotion gates unchanged.

## Verification

- Red/green ranking test proving `single_user` prefers lower latency over
  higher aggregate throughput.
- Red/green sweep-config test proving the single-user recipe uses concurrency
  one and exposes the new objective.
- Red/green cockpit rendering test for the new target card and objective
  mapping.
- Red/green catalog test for the Single User tuning area.
- Focused tests, full pytest suite, release check, and local cockpit browser
  validation.
