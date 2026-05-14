# Data Model: Scheduler Knob Sweep

## OptionalServeFlag

- `json_name`: Underscore-form field used in JSON.
- `cli_name`: Hyphenated vLLM command flag.
- `type`: Boolean or integer.
- `render_when_false`: False for boolean flags.
- `bounds`: Optional integer bounds.

## ExtendedServeProfile

- Existing serve profile fields.
- `optional_flags`: Map of approved optional flag names to values.

## SchedulerSweepDefinition

- Existing repeated sweep fields.
- Parameters for:
  - `max_num_batched_tokens`
  - `max_num_seqs`
  - `enable_chunked_prefill`
  - `enable_prefix_caching`

## SchedulerCandidate

- Candidate id.
- Base Qwen champion fields.
- Optional scheduler flag overrides.
- Repetition count.
