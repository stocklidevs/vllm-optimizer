# Research: Qwen Baseline Benchmark

## Decision: Sequential prompt baseline

**Rationale**: Sequential requests keep the first baseline simple and isolate
latency and token metrics before introducing concurrency.

**Alternatives considered**: Concurrent load was deferred to the optimization
phase.

## Decision: Reuse smoke lifecycle wrapper

**Rationale**: Smoke serve already proved safe start/readiness/cleanup. The
baseline should extend that wrapper rather than create a second lifecycle path.

**Alternatives considered**: Running against an already-live server was deferred
because it weakens traceability and cleanup guarantees.
