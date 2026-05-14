# Research: Workload-Aware Sweeps

## Decision: Add explicit sweep candidates

**Rationale**: High-impact knobs interact in ways that make a full cartesian grid expensive and noisy. Explicit candidate lists let us test known-good baselines, latency-leaning candidates, throughput-leaning candidates, block-size variants, and KV cache probes in a bounded plan.

**Alternatives considered**: Use `max_trials` on a large cartesian grid. Rejected because cartesian ordering can accidentally over-sample early values and miss important interactions.

## Decision: Split workloads by prompt set

**Rationale**: The current benchmark runner binds one prompt set to one sweep. Separate configs keep each ranking honest for a single workload shape and make live runs easy to compare.

**Alternatives considered**: Mix all workloads into one prompt file. Rejected because a single aggregate can hide workload-specific wins and regressions.

## Decision: Include risky KV cache probes but keep them session-scoped

**Rationale**: KV cache dtype can materially affect memory and throughput. Keeping it behind risky-session validation and dry-run preview preserves safety while allowing useful exploration.

**Alternatives considered**: Defer KV cache dtype until later. Rejected because it is one of the more promising high-impact knobs and is already represented in the approved risk catalog.
