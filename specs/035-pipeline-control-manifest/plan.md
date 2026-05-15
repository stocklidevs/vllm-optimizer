# Implementation Plan: Pipeline Control Manifest

**Branch**: `035-pipeline-control-manifest` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)

## Summary

Add a local manifest generator that turns a selected knob group into ordered UI control stages. The manifest describes command hints, artifact paths, remote actions, and explicit safety gates without running anything.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing artifact helpers and knob group catalog contract

**Storage**: JSON control manifest and optional standalone HTML preview

**Testing**: pytest unit and CLI integration tests

**Target Platform**: Windows host reading local catalog artifacts

**Project Type**: Python CLI generating local UI control artifacts

**Constraints**: No GX10 calls; promotion disabled by default; deterministic output.

## Constitution Check

- **Deterministic Experiments**: Pass. Manifest is generated from catalog input and selected id.
- **Complete Traceability**: Pass. Manifest preserves config and artifact paths.
- **Remote Safety and Reversibility**: Pass. Manifest only describes gated remote actions.
- **Objective-Driven Optimization**: Pass. Manifest preserves selected family context.
- **Testable, Modular Automation**: Pass. Unit and CLI tests cover stage generation.

## Project Structure

```text
specs/035-pipeline-control-manifest/
|-- spec.md
|-- plan.md
`-- tasks.md

src/vllm_optimizer/
|-- pipeline_control.py
`-- cli.py

tests/
|-- unit/test_pipeline_control.py
`-- integration/test_cli_pipeline_control.py
```

## Experiment and Safety Design

**Objective Family**: Pipeline control and safety-gated orchestration.

**Benchmark Inputs**: Knob group catalog and selected group id.

**Remote Actions**: None during manifest generation.

**Artifacts**: `pipeline-control.json` and optional `pipeline-control.html`.

**Rollback/Cleanup**: Generated manifest files can be regenerated or deleted locally.

## Complexity Tracking

No constitution violations.
