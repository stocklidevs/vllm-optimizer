# Research: Benchmark Concurrency

## Decision: Store concurrency on prompt sets

**Rationale**: Concurrency describes the workload being sent to vLLM, not the served model profile. Keeping it in prompt sets lets the same profile be compared under sequential and concurrent workloads.

**Alternatives considered**: Add concurrency as a serve sweep parameter. Rejected because request concurrency is benchmark harness behavior, not a vLLM serve flag.

## Decision: Use batch duration for concurrent throughput

**Rationale**: Summing per-request durations undercounts true concurrent throughput because overlapping requests share wall-clock time. Batch duration better reflects user-visible concurrent throughput.

**Alternatives considered**: Keep sequential throughput math. Rejected because it would make concurrency runs look artificially slow.

## Decision: Promote a workload-specific profile

**Rationale**: The concurrent winner uses higher GPU memory utilization but should not automatically replace the sequential default. A separate profile preserves the result without overgeneralizing it.

**Alternatives considered**: Replace the default profile. Rejected because the win was confirmed for concurrent interactive coding only.
