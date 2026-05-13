# Research: Qwen Parameter Sweep

## Decision: Start With Profile Override Sweeps

Rationale: The project already has reliable profile rendering and a safe
baseline benchmark lifecycle. Treating each trial as a profile variant keeps
the first optimizer increment small, auditable, and reversible.

Alternatives considered: A generic system-tuning layer was deferred because it
would require persistent mutation policies. A benchmark-only ranking layer was
too passive because it would not generate candidates.

## Decision: Use Bounded Cartesian Generation With Stable Sorting

Rationale: Small Cartesian products are easy to inspect, deterministic, and
adequate for first-pass tuning of a few parameters. Stable sorting plus
content-based trial identifiers makes repeated plans comparable.

Alternatives considered: Random search and Bayesian optimization were deferred
until the project has enough trusted measurements to justify adaptive runs.

## Decision: Keep Live Sweeps Sequential

Rationale: Sequential trials reuse the existing lifecycle safety model and
avoid broad load testing, GPU pressure surprises, and ambiguous attribution of
failures.

Alternatives considered: Concurrent requests and multi-worker load tests were
deferred to a later workload-specific benchmark spec.

## Decision: Rank From Existing Benchmark Metrics

Rationale: Baseline benchmark artifacts already include latency and token
throughput. Throughput, latency, and balanced rankings can be derived from
those metrics without introducing a new benchmark harness.

Alternatives considered: External benchmark tools were deferred because they
would add installation and compatibility questions on the GX10.
