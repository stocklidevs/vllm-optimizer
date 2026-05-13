<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Template principle 1 -> Deterministic Experiments
- Template principle 2 -> Complete Traceability
- Template principle 3 -> Remote Safety and Reversibility
- Template principle 4 -> Objective-Driven Optimization
- Template principle 5 -> Testable, Modular Automation
Added sections:
- Operating Constraints
- Development Workflow and Quality Gates
Removed sections:
- Template placeholder sections
Templates requiring updates:
- updated: .specify/templates/plan-template.md
- updated: .specify/templates/spec-template.md
- updated: .specify/templates/tasks-template.md
Follow-up TODOs: none
-->

# vLLM Optimizer Constitution

## Core Principles

### I. Deterministic Experiments

Every experiment MUST be reproducible from recorded inputs. The system MUST
record the benchmark definition, optimizer strategy, parameter search space,
random seeds, prompt corpus identifiers, request mix, model identity, vLLM
version, hardware facts, driver/CUDA facts, environment variables, command
lines, and software git commit for each run. Any stochastic behavior MUST be
explicitly seeded or clearly marked as intentionally non-deterministic.

Rationale: vLLM tuning is only useful when results can be compared across
time, machines, models, and parameter changes.

### II. Complete Traceability

The system MUST preserve raw run artifacts in addition to derived summaries.
For each trial, it MUST retain machine-readable logs for commands executed,
vLLM launch configuration, benchmark inputs, benchmark outputs, telemetry, and
failure modes. Reports MUST link ranked recommendations back to the exact
trial data that produced them.

Rationale: optimization recommendations are decisions, not vibes; every one
must be auditable.

### III. Remote Safety and Reversibility

Any operation that touches the GX10 or changes Linux, NVIDIA, vLLM, or service
state MUST pass through an explicit allowlist and MUST be logged before
execution. Mutating remote actions MUST support dry-run mode, declare expected
side effects, and define rollback or cleanup behavior when practical. The
system MUST NOT run unbounded shell input, destructive commands, credential
printing commands, or package/system upgrades unless a feature spec explicitly
authorizes them.

Rationale: benchmark automation will control a real machine over Tailscale SSH;
speed is not worth losing control of the host.

### IV. Objective-Driven Optimization

Optimization MUST be expressed through named objectives with measurable
criteria. The project MUST support multiple objective families, including
throughput, latency, memory efficiency, tool-call reliability, structured output
validity, long-context stability, serving stability, and balanced weighted
profiles. A result MUST NOT be called "best" without naming the objective,
constraints, and tie-breakers used to rank it.

Rationale: there is no universal best vLLM configuration; there are only best
configurations for a workload and target.

### V. Testable, Modular Automation

Core behavior MUST be split into independently testable modules for experiment
definition, remote execution, vLLM lifecycle control, benchmark execution,
telemetry collection, result storage, and report generation. Tests MUST cover
deterministic search generation, command rendering, artifact parsing, scoring,
and safety gates before real remote execution is relied upon.

Rationale: the optimizer will combine many moving parts; modular tests keep
remote experiments from becoming the only way to find bugs.

## Operating Constraints

The default target environment is a local controller repository that can reach
an Asus GX10 through Tailscale SSH and run vLLM on that remote host. Local
development MAY use mock executors, recorded fixtures, and dry-run plans when
the GX10 is unavailable.

The project MUST treat credentials, SSH identities, hostnames, tokens, and
private model paths as secrets. Such values MUST be supplied through local
configuration or environment variables and MUST NOT be committed.

Benchmark categories MUST be pluggable. Adding a new category SHOULD require
adding a benchmark implementation, objective/scoring metadata, and tests,
without changing unrelated categories.

Remote system tuning MUST begin conservatively. Linux/NVIDIA changes SHOULD be
read-only probes first, then reversible session-level tweaks, then persistent
changes only when a specification explicitly requires them.

## Development Workflow and Quality Gates

Features MUST begin with a SpecKit specification that defines user value,
objective families, measurable success criteria, edge cases, and safety
boundaries before implementation planning.

Implementation plans MUST include a Constitution Check covering reproducibility,
traceability, remote safety, objective definition, and test strategy. Any
exception MUST be listed in Complexity Tracking with a reason and a simpler
alternative.

Task lists MUST keep the first useful increment independently runnable. For
this project, the preferred MVP is a dry-run or local-fixture path before live
GX10 mutation.

Before any live GX10 experiment, the project MUST have passing tests for the
commands and artifacts involved, a dry-run preview of the remote actions, and
an explicit artifact destination.

## Governance

This constitution supersedes conflicting generated plans, task lists, and ad
hoc implementation preferences. Amendments MUST update this file, include a
Sync Impact Report, and propagate affected rules into SpecKit templates.

Versioning follows semantic versioning:
- MAJOR for incompatible governance or principle changes.
- MINOR for new principles, required sections, or materially expanded gates.
- PATCH for clarifications and editorial corrections.

Compliance MUST be reviewed during specification, planning, task generation,
and before any live remote execution. Unresolved constitution violations MUST
be documented before implementation continues.

**Version**: 1.0.0 | **Ratified**: 2026-05-13 | **Last Amended**: 2026-05-13
