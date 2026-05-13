# Research: vLLM Flag Catalog

## Decision: Capture Help From the Profile Executable

Rationale: The Qwen profile already records the executable used for serving,
which avoids accidentally inspecting a different vLLM installation.

Alternatives considered: Calling `vllm` from PATH was rejected because the GX10
may have multiple environments.

## Decision: Conservative Policy Categories

Rationale: A seed policy should mark only obvious session-level knobs as
sweepable and keep speculative, memory offload, and parallelism flags as risky
until separately specified.

Alternatives considered: Auto-classifying every flag was rejected because names
alone are not enough to determine safety.

## Decision: Store Raw Help Text

Rationale: Parser bugs and vLLM version changes are easier to audit when the
source help text is preserved.

Alternatives considered: Storing only parsed JSON was rejected because it would
lose traceability.
