# Research: vLLM Optimization Lab

## Decision: Python CLI/library for the local controller

**Rationale**: Python is the natural ecosystem for vLLM users, benchmark
clients, JSON/JSONL processing, SSH orchestration, and later integration with
ML tooling. A CLI plus importable library keeps the first increment useful both
for humans and tests.

**Alternatives considered**: A web app was deferred because it adds UI surface
area before the experiment model is stable. A shell-only tool was rejected
because deterministic planning, scoring, and artifact validation need stronger
data modeling than scripts provide.

## Decision: JSON-first experiment definitions with optional YAML later

**Rationale**: JSON is available in the Python standard library, easy to
validate, stable for tests, and sufficient for deterministic fixtures. The
contract allows YAML as a future convenience without making the MVP depend on
extra runtime packages.

**Alternatives considered**: YAML-only definitions are nicer to hand-edit but
would require an extra dependency for the MVP. TOML is available in newer
Python versions but less convenient for nested benchmark workloads.

## Decision: Deterministic Cartesian trial expansion

**Rationale**: The first optimizer must be transparent and reproducible.
Cartesian expansion over sorted parameter keys gives stable trial order and
clear coverage. More advanced strategies can be added later behind the same
trial-plan contract.

**Alternatives considered**: Bayesian optimization and random search were
deferred because they introduce state, stochastic behavior, and more complex
explanations before baseline artifact handling exists.

## Decision: Dry-run executor before live SSH

**Rationale**: The constitution requires remote safety. A dry-run executor
lets us prove command rendering, allowlist enforcement, artifact destinations,
and cleanup intent without contacting the GX10.

**Alternatives considered**: Direct SSH was deferred until command contracts,
safety tests, and artifact storage have proven themselves locally.

## Decision: File artifacts instead of a database for MVP

**Rationale**: JSON and JSONL artifacts are inspectable, diffable, easy to
archive, and enough for one-machine experiment runs. A database can be added
when query needs outgrow files.

**Alternatives considered**: SQLite or DuckDB were considered for later
analysis but deferred to avoid hiding raw artifacts behind a storage layer too
early.
