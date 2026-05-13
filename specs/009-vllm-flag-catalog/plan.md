# Implementation Plan: vLLM Flag Catalog

**Branch**: `009-vllm-flag-catalog` | **Date**: 2026-05-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/009-vllm-flag-catalog/spec.md`

## Summary

Add a local parser and policy classifier for full `vllm serve` help, plus a
read-only capture command that uses the Qwen profile executable and GX10 SSH
config to save version/help/catalog artifacts.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Standard library, pytest, existing artifact,
redaction, SSH, discovery, and serve-profile helpers

**Storage**: Local JSON/text artifacts under ignored `artifacts/`

**Testing**: pytest unit and integration tests

**Target Platform**: Local controller; optional read-only GX10 SSH capture

**Project Type**: Python CLI

**Performance Goals**: Parse and classify help text in under one second

**Constraints**: Read-only SSH commands only; no vLLM server start; no package
install; no Linux/NVIDIA mutation

**Scale/Scope**: One Qwen-oriented seed policy for known performance-relevant
vLLM flags

## Constitution Check

- **Deterministic Experiments**: PASS. Catalog records source version, help
  text, policy, and generated artifacts.
- **Complete Traceability**: PASS. Catalog links to raw help/version artifacts.
- **Remote Safety and Reversibility**: PASS. Remote actions are read-only help
  and version commands.
- **Objective-Driven Optimization**: PASS. Objective is safe flag discovery for
  future optimizer expansions.
- **Testable, Modular Automation**: PASS. Parser, classifier, CLI, mock capture,
  and artifact writing are independently testable.

## Project Structure

```text
config/vllm-flags/qwen-safe-policy.json
src/vllm_optimizer/flag_catalog.py
src/vllm_optimizer/cli.py
tests/fixtures/vllm/serve-help.txt
tests/unit/test_flag_catalog.py
tests/integration/test_cli_flag_catalog.py
specs/009-vllm-flag-catalog/
```

**Structure Decision**: Add a focused flag catalog module and CLI commands.

## Experiment and Safety Design

**Objective Family**: Flag discovery and safe optimizer policy preparation

**Benchmark Inputs**: None; help/version text only

**Remote Actions**: `vllm --version` and `vllm serve --help=all` through the Qwen
profile executable

**Artifacts**: `version.txt`, `serve-help.txt`, `catalog.json`,
`redaction-report.json`

**Rollback/Cleanup**: Not applicable; no remote mutation

## Complexity Tracking

No constitution violations.
