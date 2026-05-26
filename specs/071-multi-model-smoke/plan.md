# Implementation Plan: Multi-Model Registry and Smoke Workflow

**Branch**: `071-multi-model-smoke` | **Date**: 2026-05-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/071-multi-model-smoke/spec.md`

## Summary

Add a deterministic model registry and smoke-readiness workflow so the optimizer
can move beyond the current Qwen3 Coder Next baseline without mixing artifacts
or pretending untested models have performance winners. The first concrete new
baseline is the user-provided Gemma 4 E4B IT vLLM serve recipe; GLM 4.7 Flash,
Qwen3.6 27B, Qwen3.5 27B, and DeepSeek Coder V2 Lite Instruct are cataloged as
local vLLM candidates whose performance baselines remain pending until smoke
checks and benchmarks run.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Existing standard-library CLI/web cockpit modules; no
new runtime dependencies for this phase

**Storage**: JSON model catalog, JSON smoke plan/result artifacts, Markdown
handoff documentation

**Testing**: pytest unit and integration tests

**Target Platform**: Local controller on Windows, remote Asus GX10 reachable
through existing Tailscale SSH configuration

**Project Type**: Python CLI plus dependency-free local web cockpit

**Performance Goals**: Smoke-plan generation is deterministic and local; live
performance metrics are measured only after a model passes readiness checks

**Constraints**: No persistent GX10 system changes; live smoke is session
mutating only because it may start and stop vLLM

**Scale/Scope**: Initial catalog covers the existing Qwen3 Coder Next model plus
five new local model candidates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic Experiments**: PASS. Model identity, served name, serve
  defaults, parser/template notes, prompt probes, vLLM assumptions, artifact
  paths, and controller version are recorded before execution.
- **Complete Traceability**: PASS. Smoke plans and results retain rendered
  commands, request payloads, responses, logs, cleanup status, and source
  profile metadata.
- **Remote Safety and Reversibility**: PASS. Catalog listing and planning are
  local read-only actions; live smoke execution is session-mutating with
  managed vLLM startup and cleanup. Persistent system changes remain out of
  scope.
- **Objective-Driven Optimization**: PASS. The objective family for this spec
  is model readiness and compatibility before throughput, latency, stability,
  tool-use, or balanced sweeps.
- **Testable, Modular Automation**: PASS. Coverage focuses on catalog loading,
  profile rendering, deterministic smoke planning, artifact parsing, cockpit
  model selection, and safety messaging.

## Project Structure

### Documentation (this feature)

```text
specs/071-multi-model-smoke/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- model-catalog.schema.md
|   `-- model-smoke-artifacts.md
`-- tasks.md
```

### Source Code (repository root)

```text
config/
|-- model-catalog.json
`-- profiles/
    |-- gemma-4-e4b-it.json
    |-- glm-4-7-flash.json
    |-- qwen3-6-27b.json
    |-- qwen3-5-27b.json
    `-- deepseek-coder-v2-lite-instruct.json

src/vllm_optimizer/
|-- cli.py
|-- model_catalog.py
|-- serve_profiles.py
|-- smoke.py
`-- web_cockpit.py

tests/
|-- integration/
`-- unit/
```

**Structure Decision**: Keep the registry and smoke workflow inside the existing
single Python package. Profiles remain under `config/profiles/`; shared catalog
metadata lives under `config/model-catalog.json`; generated artifacts continue
under `artifacts/`.

## Experiment and Safety Design

**Objective Family**: Model readiness and compatibility.

**Benchmark Inputs**: Smoke probes use a short deterministic plain-chat prompt
and, when the catalog marks tool calls as supported, a minimal deterministic
tool-call probe. Full workload sweeps are blocked until smoke readiness exists.

**Remote Actions**: Dry-run catalog and smoke planning are local. Live smoke
checks run only through the existing GX10 safety path, start a managed vLLM
process, probe readiness and chat/tool behavior, collect logs, then stop the
managed process.

**Artifacts**: Model catalog snapshots, profile JSON, smoke plan JSON, readiness
summary JSON, response JSON, cleanup JSON, server log JSON, redaction report,
and later model comparison reports.

**Rollback/Cleanup**: Live smoke traps process cleanup, terminates the managed
vLLM PID, waits for exit, force-kills only that managed PID if needed, and
records cleanup success or failure.

## Complexity Tracking

No constitution violations are introduced.
