# Implementation Plan: System Tuning Discovery

**Branch**: `026-system-tuning-discovery` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

## Summary

Add a read-only `system-tuning-discover` command that probes Linux/NVIDIA/runtime tuning state over SSH or mock execution and writes a structured catalog. The catalog is intentionally observational: it records current values and future risk classification but performs no mutations.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Standard library, existing SSH executor, existing redaction/artifact helpers

**Storage**: Local JSON artifacts

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows development host orchestrating a Linux GX10 over SSH

**Project Type**: Python CLI

**Performance Goals**: Discovery should finish within the target config timeout per probe.

**Constraints**: Read-only commands only; optional probe failures do not fail the whole run; secrets redacted.

**Scale/Scope**: One host per command invocation.

## Constitution Check

- **Deterministic Experiments**: Pass. Probe list and raw outputs are recorded.
- **Complete Traceability**: Pass. Raw probe outputs and parsed catalog are linked in the redaction report.
- **Remote Safety and Reversibility**: Pass. All probes are read-only and validated before execution.
- **Objective-Driven Optimization**: Pass. Objective is tuning eligibility discovery.
- **Testable, Modular Automation**: Pass. Parsers and mock executor behavior are unit/integration tested.

## Project Structure

```text
specs/026-system-tuning-discovery/
|-- spec.md
|-- plan.md
|-- contracts/
|   `-- system-tuning-discover.md
`-- tasks.md

src/vllm_optimizer/
|-- cli.py
`-- system_tuning.py

tests/
|-- integration/test_cli_system_tuning.py
`-- unit/test_system_tuning.py
```

## Experiment and Safety Design

**Objective Family**: Discovery and tuning eligibility.

**Benchmark Inputs**: Target config and fixed probe list.

**Remote Actions**: Read-only shell commands for NVIDIA, CPU, memory, kernel, limits, and runtime environment.

**Artifacts**: `raw-probes.json`, `catalog.json`, `redaction-report.json`.

**Rollback/Cleanup**: None required because no mutations are performed.

## Complexity Tracking

No constitution violations.
