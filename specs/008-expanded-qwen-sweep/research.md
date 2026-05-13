# Research: Expanded Qwen Sweep

## Decision: Fix max_model_len at 32768

Rationale: The top repeated candidate used 32768, and fixing this dimension
keeps the next search focused on nearby memory utilization and performance mode.

Alternatives considered: Adding 16384 again was rejected because it already
underperformed in the first sweep and would double live runtime.

## Decision: Test performance_mode as a Safe Session Parameter

Rationale: The serve profile already renders `performance_mode`, and changing
it affects only the vLLM serve process for that trial.

Alternatives considered: Linux/NVIDIA tuning was deferred because it requires a
separate persistent-mutation safety spec.

## Decision: Use Three Repetitions

Rationale: Three repetitions are consistent with the top-two stability feature
and keep the live run bounded at eighteen sequential trials.

Alternatives considered: Five or more repetitions were deferred until the
expanded grid identifies a smaller finalist set.
