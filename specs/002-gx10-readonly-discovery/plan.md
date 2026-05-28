# Implementation Plan: GX10 Read-Only Discovery

**Branch**: `002-gx10-readonly-discovery` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-gx10-readonly-discovery/spec.md`

## Summary

Add a read-only discovery workflow to the existing Python CLI. The feature
loads a local, ignored GX10 target config; validates that all probes are
read-only; supports mock discovery without network access; parses host/GPU/
Python/vLLM facts; redacts configured secret values before writing artifacts;
and can run the same fixed read-only probe catalog over SSH once key-based
authentication has been confirmed.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library only for runtime; pytest for tests

**Storage**: Local filesystem artifacts under `artifacts/discovery/<run-id>/`
with JSON raw probe logs and JSON normalized summary

**Testing**: pytest unit and integration tests with mock executor fixtures

**Target Platform**: Local Windows controller; remote Linux GX10 later through
configured SSH

**Project Type**: Python CLI plus importable library

**Performance Goals**: Mock discovery completes in under 1 second; redaction is
applied before every artifact write

**Constraints**: All probe definitions must be read-only; local GX10 config
stays ignored by git; SSH uses batch mode and must not prompt interactively

**Scale/Scope**: One configured target, one discovery run at a time, host/GPU/
CUDA/Python/vLLM availability facts only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic Experiments**: PASS. Discovery run artifacts include probe
  definitions, target label, tool version, timestamp, and repository commit
  when available. Mock runs are deterministic from fixture outputs.
- **Complete Traceability**: PASS. Raw per-probe results and normalized summary
  are saved separately and linked by run id.
- **Remote Safety and Reversibility**: PASS. This feature implements mock
  execution, read-only probe validation, and an SSH executor that only runs the
  fixed read-only probe catalog with batch-mode authentication.
- **Objective-Driven Optimization**: PASS. This feature measures environment
  readiness, not performance optimization, and reports availability fields.
- **Testable, Modular Automation**: PASS. Config loading, probe validation,
  execution abstraction, parsing, redaction, artifact writing, and CLI wiring
  are separate and testable.

## Project Structure

### Documentation (this feature)

```text
specs/002-gx10-readonly-discovery/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- cli.md
|   `-- discovery-config.schema.json
`-- tasks.md
```

### Source Code (repository root)

```text
src/vllm_optimizer/
|-- discovery.py
|-- discovery_cli.py
|-- redaction.py
|-- ssh.py
`-- existing modules

tests/fixtures/discovery/
|-- local.gx10.mock.json
`-- mock_outputs.json

tests/unit/
tests/integration/
```

**Structure Decision**: Keep discovery as focused modules inside the existing
package. `ssh.py` defines an executor interface and mock executor now; a real
SSH executor can be added later behind the same interface.

## Experiment and Safety Design

**Objective Family**: Environment readiness measurement; no optimization
objective is ranked in this feature.

**Benchmark Inputs**: None. Inputs are local discovery config, read-only probe
definitions, and mock output fixtures.

**Remote Actions**: Probe definitions are read-only only. Implemented commands:
connectivity identity, OS release, kernel/host identity, GPU/driver query,
CUDA visibility query, Python version query, and vLLM version/import query.
Mock and SSH executor modes are available.

**Artifacts**: `raw-probes.json`, `summary.json`, and `redaction-report.json`
under `artifacts/discovery/<run-id>/`.

**Rollback/Cleanup**: Not applicable because no mutating command is allowed or
executed.

## Complexity Tracking

No constitution violations are required for this plan.
