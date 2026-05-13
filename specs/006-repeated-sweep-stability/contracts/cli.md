# CLI Contract: Repeated Sweep Stability

Existing sweep commands continue to work.

## `vllm-optimizer sweep-plan`

Additional behavior:
- Accepts `repetitions` in the sweep definition.
- Emits both `candidate_count` and `trial_count`.
- Each trial includes `candidate_id`, `candidate_order`, and
  `repetition_index`.

## `vllm-optimizer sweep-rank`

Additional behavior:
- Groups repeated rows by candidate.
- Emits `candidate_aggregates`.
- Rankings use candidate aggregates rather than individual repetitions when
  repeated trial metadata is present.

## `vllm-optimizer sweep-run`

Additional behavior:
- Executes repeated trials sequentially in plan order.
- Writes one result row per repeated trial.
- Writes aggregate `ranking.json` after execution.
