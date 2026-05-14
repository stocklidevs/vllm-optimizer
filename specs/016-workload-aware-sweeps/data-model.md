# Data Model: Workload-Aware Sweeps

## Workload Prompt Set

- `prompt_set_id`: Stable id for reports and reproducibility.
- `cases`: Deterministic prompts with case id, messages, max token budget, and temperature.

## Explicit Sweep Candidate

- A non-empty object of approved parameter overrides.
- Uses the same validation rules as cartesian sweep parameters.
- Can include safe-session and risky-session values.

## Workload Sweep Definition

- `sweep_id`: Stable id for artifact roots and trial ids.
- `profile`: Confirmed recommended Qwen profile path.
- `prompts`: Workload prompt set path.
- `repetitions`: Number of repetitions per explicit candidate.
- `allow_risky_session_flags`: Required for high-impact candidates containing risky-session flags.
- `candidates`: Bounded list of explicit candidate override objects.
