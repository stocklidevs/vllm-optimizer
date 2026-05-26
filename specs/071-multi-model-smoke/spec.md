# Feature Specification: Multi-Model Registry and Smoke Workflow

**Feature Branch**: `071-multi-model-smoke`

**Created**: 2026-05-26

**Status**: Implementing

**Input**: User supplied a Gemma 4 E4B IT vLLM serve recipe and asked to add other models and test them after the Qwen optimization flow. Candidate local models include Gemma 4 E4B IT, GLM 4.7 Flash, Qwen 3.6 27B, DeepSeek Coder V2 Lite, and optional Qwen 3.5 27B; Gemini is deferred to a later external API baseline.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Choose a Model Before Tuning (Priority: P1)

As an optimizer user, I want to choose which local vLLM model is being tested before starting smoke checks or sweeps, so that results are not accidentally mixed across model families.

**Why this priority**: Parameter winners are model-specific. The optimizer must make the model identity explicit before more tuning is useful.

**Independent Test**: Can be tested by listing available models and confirming that Gemma 4 E4B IT appears with its served name, safety notes, parser metadata, and default serve settings.

**Acceptance Scenarios**:

1. **Given** the model catalog is available, **When** the user lists local vLLM candidates, **Then** Gemma 4 E4B IT, GLM 4.7 Flash, Qwen 3.6 27B, DeepSeek Coder V2 Lite, and optional Qwen 3.5 27B are shown as separate model choices.
2. **Given** the user selects Gemma 4 E4B IT, **When** the optimizer prepares the model context, **Then** it records the Hugging Face model identity, served model name, context length, memory utilization target, tool parser, and chat template requirement.

---

### User Story 2 - Smoke Test a Model Safely (Priority: P2)

As an optimizer user, I want a repeatable smoke check before a model enters expensive sweeps, so that broken templates, parser settings, or serve commands are caught early.

**Why this priority**: Multi-model tuning can waste time quickly if a model cannot serve, answer, or produce tool calls under the expected contract.

**Independent Test**: Can be tested by generating a dry-run smoke plan for Gemma 4 E4B IT and confirming that no GX10 command is executed without a live run request.

**Acceptance Scenarios**:

1. **Given** a model profile exists, **When** the user previews smoke testing, **Then** the optimizer shows the serve command, readiness probe, plain chat probe, tool-call probe when supported, artifact paths, and cleanup step.
2. **Given** a smoke check completes, **When** the user reviews the result, **Then** the optimizer reports pass, fail, or unsupported for serve readiness, text response, tool call behavior, and cleanup.

---

### User Story 3 - Compare Model Readiness Before Sweeps (Priority: P3)

As an optimizer user, I want to see which models are ready for optimization and which objective targets they support, so that I can decide which model deserves a full sweep.

**Why this priority**: The cockpit should guide the user toward the next useful model action instead of treating all models as equally ready.

**Independent Test**: Can be tested with fixture smoke results that mark one model passing, one model failing tools, and one model not yet tested.

**Acceptance Scenarios**:

1. **Given** smoke results exist for multiple models, **When** the user opens model readiness, **Then** each model shows the latest status, supported objectives, known constraints, and next recommended action.
2. **Given** a model has no smoke result, **When** the user attempts to start optimization for that model, **Then** the optimizer recommends smoke testing first and does not silently reuse another model's artifacts.

---

### Edge Cases

- A model requires a local chat template file that is missing on the GX10.
- A model supports text generation but not reliable tool calling.
- A smoke run fails after starting the server and cleanup still needs to be attempted.
- Two models share the same port or served model name in user-provided recipes.
- Existing Qwen sweep artifacts are present while a different model is selected.
- A model is external API only and cannot be exercised through local vLLM; this must be excluded from local smoke runs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST maintain a model catalog that separates local vLLM models from external API baselines.
- **FR-002**: The catalog MUST include Gemma 4 E4B IT using the user-provided serve defaults: model identity `google/gemma-4-E4B-it`, served name `Gemma-4-E4B-IT`, port `8001`, maximum context `16384`, GPU memory utilization `0.80`, auto tool choice enabled, tool parser `gemma4`, and chat template `~/vllm-templates/tool_chat_template_gemma4.jinja`.
- **FR-003**: The catalog MUST include local candidate metadata for GLM 4.7 Flash, Qwen 3.6 27B, DeepSeek Coder V2 Lite, and optional Qwen 3.5 27B without treating any untested model as a confirmed winner.
- **FR-004**: Users MUST be able to list model candidates with model identity, served name, runtime type, support status, tool/parser notes, context defaults, safety notes, and recommended next action.
- **FR-005**: Users MUST be able to generate a deterministic smoke plan for a selected local model before live execution.
- **FR-006**: Smoke planning MUST show all expected live actions, side effects, artifact paths, and cleanup behavior.
- **FR-007**: Smoke execution results MUST record serve readiness, plain chat behavior, tool-call behavior when applicable, cleanup outcome, failure details, model identity, served model name, command inputs, and timestamps.
- **FR-008**: The cockpit MUST expose model selection separately from objective selection so that users can choose both "what model" and "what target" before optimization.
- **FR-009**: The cockpit MUST prevent or clearly warn against starting a full optimization for a model whose latest smoke status is failed or missing.
- **FR-010**: Existing single-model Qwen behavior MUST continue to work when the user does not select a new model.
- **FR-011**: Gemini MUST be represented only as a future external baseline candidate unless a separate spec defines external API benchmarking.

### Experiment Requirements *(include for optimizer features)*

- **ER-001**: Feature MUST define the objective family as model readiness and compatibility before model-specific throughput, latency, stability, tool-use, or balanced sweeps.
- **ER-002**: Feature MUST define reproducibility inputs for each smoke run: model catalog entry, serve command defaults, prompt set, selected tool-call probe, vLLM version, GX10 host facts when available, controller git commit, and artifact directory.
- **ER-003**: Feature MUST retain raw smoke artifacts including rendered serve command, readiness probes, request payloads, responses, logs, and structured summary.
- **ER-004**: Feature MUST classify GX10 actions as session-mutating because smoke execution starts and stops a vLLM process, while catalog listing and dry-run planning remain local and read-only.
- **ER-005**: Feature MUST support dry-run smoke planning without connecting to the GX10.

### Key Entities *(include if feature involves data)*

- **Model Candidate**: A model option the optimizer can reason about, including identity, runtime type, served name, default serve settings, parser/template notes, known limitations, and status labels.
- **Model Smoke Plan**: The deterministic preview of actions required to serve, probe, and clean up one local model.
- **Model Smoke Result**: The structured outcome of a smoke run for one model at one time, including pass/fail details and artifact links.
- **Model Readiness Summary**: The latest known readiness state used by the cockpit and CLI before deeper sweeps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify the selected model and served model name before starting a smoke check or sweep in 100% of tested cockpit and CLI flows.
- **SC-002**: Generating the same smoke plan twice for the same model produces identical action ordering and equivalent command content.
- **SC-003**: A model with no smoke result is never presented as fully ready for optimization.
- **SC-004**: A completed smoke result links to raw artifacts for every readiness category: serve, chat, tool behavior when applicable, and cleanup.
- **SC-005**: Existing Qwen optimization tests continue to pass after adding multi-model catalog support.

## Assumptions

- Local vLLM models are the first implementation target; external hosted providers are out of scope for this feature.
- Gemma 4 E4B IT is the first new model to receive exact serve defaults because the user supplied a tested command recipe.
- Untested model defaults may be conservative and labeled as pending until live smoke results exist.
- Smoke checks are compatibility gates, not final performance benchmarks.
- Live GX10 smoke execution requires the existing SSH configuration and existing safety rules.
