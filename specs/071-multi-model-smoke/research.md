# Research: Multi-Model Registry and Smoke Workflow

## Decision: Record Baselines Before Performance Sweeps

**Rationale**: The project already has measured Qwen3 Coder Next GX10 results,
but the new models do not yet have smoke or performance artifacts. Recording
serve/readiness baselines first prevents accidental comparison between a proven
Qwen winner and untested model candidates.

**Alternatives considered**: Starting with full sweeps for every model was
rejected because template, parser, memory, or dependency failures would waste
live GX10 time and produce confusing reports.

## Decision: Gemma 4 E4B IT Is the First New Concrete Baseline

**Rationale**: The user supplied an exact vLLM command with model identity,
served name, context length, GPU memory utilization, tool parser, and chat
template. Official vLLM Gemma 4 guidance also calls out the `gemma4` parser and
the Gemma tool chat template for tool use.

**Alternatives considered**: Guessing baseline flags for all models was
rejected. Only Gemma has enough local recipe detail to become a first-class
baseline immediately.

## Decision: Gemini Is Deferred to External Baseline Work

**Rationale**: The Gemini API is not a local vLLM/GX10 serve target. The current
local model smoke workflow should not mix hosted API cost, credential, quota,
and latency controls into local vLLM artifacts.

**Alternatives considered**: Adding Gemini to the same catalog as a runnable
local model was rejected because it would violate the local smoke safety model.

## Decision: Large Qwen Models Need Memory-Fit Validation

**Rationale**: Qwen3.6 27B and Qwen3.5 27B publish long context defaults and
tool parser guidance, but the GX10 baseline may need a reduced local context or
text-only profile to fit safely. The first local step is smoke/readiness, not
optimization.

**Alternatives considered**: Treating upstream long-context commands as GX10
baselines was rejected because upstream examples often assume multi-GPU tensor
parallel deployment.
