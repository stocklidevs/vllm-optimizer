# Optimization Results

These results summarize the live GX10 evidence collected during development.
They are useful, but intentionally modest in their claims: the optimizer
improved some profiles, found where concurrency helps, and showed that
single-user performance is often bounded by the model/backend more than by
small serve-flag changes.

## Headline Results

| Model / Scenario | Baseline | Best observed | Change | What it means |
| --- | ---: | ---: | ---: | --- |
| Qwen3 Coder Next, C1 single-user | 47.525 tok/s | 49.726 tok/s | +4.63% | Small single-user improvement from safe/risky session tuning. |
| Qwen3 Coder Next, confirmed C8 profile | 96.041 tok/s | 97.683 tok/s | +1.71% | Current promoted concurrent profile stayed slightly ahead in repeated confirmation. |
| Qwen3 Coder Next, best C8 saturation sweep | 47.525 tok/s C1 reference | 98.415 tok/s aggregate | +107.09% aggregate vs C1 | Higher machine throughput under eight concurrent requests, not faster streaming for one user. |
| Gemma 4 E4B IT | 24.561 tok/s | 24.579 tok/s | +0.07% | Safe profile was effectively flat. |
| GLM 4.7 Flash | 30.045 tok/s | 30.545 tok/s | +1.66% | Small gain with Triton MoE pinned. |
| Qwen3.6 27B | 5.636 tok/s | 5.628 tok/s | -0.14% | Safe profile did not beat baseline. |
| Qwen3.5 27B | 5.634 tok/s | 5.612 tok/s | -0.38% | Safe profile did not beat baseline. |
| DeepSeek Coder V2 Lite Instruct | 47.482 tok/s | 48.353 tok/s | +1.83% | Best new-model single-user baseline in the first multi-model pass. |

## How To Read Tokens Per Second

`C1` means one request at a time. It is the closest measurement to one person
using a model interactively.

`C8` means eight requests are in flight together. The reported tokens/sec is
aggregate throughput across the batch, not per-user streaming speed. For
example, the best Qwen C8 saturation result was `98.415 / 8 = 12.302` tokens/sec
per active request on average if the work were evenly divided.

That distinction matters. C8 is valuable for a shared service because the GPU
can stay busier, but it does not imply that a single Codex-like user will see a
98 tok/s stream.

## Why The Results Look Like This

vLLM is designed to batch and schedule many requests efficiently. When multiple
requests arrive together, the engine can amortize GPU work across the batch and
keep the device occupied. That is why aggregate throughput can nearly double
when moving from the Qwen C1 reference to the C8 saturation sweep.

Single-user gains were modest because a single request has fewer scheduling
opportunities. Once the model is loaded, the main limits are model size,
quantization/backend behavior, context length, prompt/output shape, and GPU
kernel efficiency. Small changes such as GPU memory utilization, performance
mode, max model length, prefix caching, or session environment tweaks can help,
but they rarely transform one-user latency by themselves.

Model differences also dominated some sweeps. Gemma was stable but flat in the
safe pass. GLM and DeepSeek needed Triton MoE to avoid a FlashInfer CUTLASS path
that expected `ninja` on the GX10. The larger Qwen 27B variants were
smoke-ready, but slow enough in this environment that safe profile tweaks did
not create a practical performance win.

## Reproduction And Provenance

Primary source artifacts:

- `artifacts/benchmarks/qwen-baseline/summary.json`
- `artifacts/sweeps/qwen-risky-session-small/live/ranking.json`
- `artifacts/benchmarks/qwen-c8-confirmation/current/summary.json`
- `artifacts/benchmarks/qwen-c8-confirmation/candidate/summary.json`
- `artifacts/sweeps/qwen-concurrency-saturation-c8/live/ranking.json`
- `artifacts/models/gemma-4-e4b-it/baseline/summary.json`
- `artifacts/models/gemma-4-e4b-it/safe-profiles/live/ranking.json`
- `artifacts/models/glm-4-7-flash/baseline/summary.json`
- `artifacts/models/glm-4-7-flash/safe-profiles/live/ranking.json`
- `artifacts/models/qwen3-6-27b/baseline/summary.json`
- `artifacts/models/qwen3-6-27b/safe-profiles/live/ranking.json`
- `artifacts/models/qwen3-5-27b/baseline/summary.json`
- `artifacts/models/qwen3-5-27b/safe-profiles/live/ranking.json`
- `artifacts/models/deepseek-coder-v2-lite-instruct/baseline/summary.json`
- `artifacts/models/deepseek-coder-v2-lite-instruct/safe-profiles/live/ranking.json`

See also `docs/PROJECT_STATUS.md` for the model baseline tracker and current
GX10 cache hygiene notes.
