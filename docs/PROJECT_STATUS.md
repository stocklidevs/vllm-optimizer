# Project Status

Last updated: 2026-05-27

Current release: 0.56.5 public alpha

## Public Alpha Scope

The public alpha is ready for local evaluation, documentation review, and
careful GX10 reproduction. Local users can run planning, previews, mock/demo
commands, report generation, cockpit launch, tests, and release-check without a
remote machine. Live GX10 runs remain optional and explicitly gated.

The CLI artifacts remain the source of truth. The cockpit is a friendlier
controller and reporting layer over those artifacts, not a separate optimizer.

## What Exists

vLLM Optimizer is a local, deterministic optimization lab for the GX10. The
CLI remains the source of truth, and the cockpit is a controller and reporting
surface over the same artifacts.

The current system can:

- Generate deterministic vLLM sweep plans and previews.
- Run gated live sweeps against the GX10.
- Rank candidates for throughput, latency, balanced score, and single-user
  responsiveness.
- List local vLLM model candidates and generate model-aware smoke plans before
  benchmarking new models.
- Run one-model-at-a-time live smoke, baseline, and safe-profile sweeps for
  catalog models while keeping Hugging Face cache usage explicit.
- Produce report and release artifacts for cockpit consumption.
- Launch a local active cockpit with objective-first controls, live progress,
  report review, candidate selection, and gated promotion.
- Keep risky-session, live-run, session-tuning, and promotion actions explicit.

## Main User Workflows

Start the default aggregate-throughput cockpit:

```powershell
uv run vllm-optimizer cockpit-launch
```

Start the single-user responsiveness cockpit:

```powershell
uv run vllm-optimizer cockpit-launch --sweep config/sweeps/qwen-single-user-interactive.json --out-dir artifacts/controller/qwen-single-user
```

Run the verification gate before release or handoff:

```powershell
uv run pytest
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

## Current Safety Boundary

Live GX10 runs are session-scoped and gated. Persistent Linux, NVIDIA, kernel,
firmware, service, boot, or credential changes are still intentionally out of
scope until a dedicated safety and rollback spec exists.

## Latest Product Direction

The cockpit should stay objective-first:

- Casual use starts by choosing the outcome: Balanced, Performance, Single
  User, Stability, or Tool Use.
- Advanced users can open the recipe drawer for knob families, command hints,
  artifacts, reports, and gates.
- Reporting should explain the recommendation story: baseline, winner,
  improvement, risk, and next safe action.
- Promotion remains explicit and never automatic.

## Model Baseline Tracker

Validated on 2026-05-26 against upstream model pages, vLLM documentation, and
live GX10 artifacts. "Baseline" means the first conservative single-user
benchmark for the model. "Safe sweep top" means the best ranked candidate from
the initial four-candidate safe-profile sweep; it is not automatically a
promotion if it does not beat baseline.

| Model | Runtime lane | Live smoke status | Baseline | Safe sweep top | Next action |
| --- | --- | --- | --- | --- | --- |
| Qwen3 Coder Next AWQ 4-bit | `cyankiwi/Qwen3-Coder-Next-AWQ-4bit`, served as `Qwen3-Coder-Next`, `max_model_len=32768`, `gpu_memory_utilization=0.90`, `qwen3_coder`, interactivity mode. | Passed in `artifacts/models/qwen3-coder-next-awq/live/summary.json`. | Confirmed C8 reference remains 97.683 tokens/sec and 6644.200 ms mean latency; saturation sweep recorded 98.415 aggregate tokens/sec. | Existing promoted concurrent profile remains the project reference. | Keep as the reference while comparing new models and objective recipes. |
| Gemma 4 E4B IT | `google/gemma-4-E4B-it`, served as `Gemma-4-E4B-IT`, `max_model_len=16384`, `gpu_memory_utilization=0.80`, `gemma4`, chat template `$HOME/vllm-templates/tool_chat_template_gemma4.jinja`. | Passed in `artifacts/models/gemma-4-e4b-it/live/summary.json`. | 24.561 tokens/sec, 10830.0 ms mean latency, 0 failures. | `gemma-4-e4b-it-safe-profiles-c002-4e4b7240`: 24.579 tokens/sec, 10822.0 ms, `gpu_memory_utilization=0.84`, interactivity mode. | Keep the C002 safe profile as the local comparison point; run objective-specific workloads before promotion. |
| GLM 4.7 Flash | `zai-org/GLM-4.7-Flash`, local profile uses `--moe-backend triton` because the FlashInfer CUTLASS path requires `ninja` on the GX10. | Passed in `artifacts/models/glm-4-7-flash/live/summary.json`. | 30.045 tokens/sec, 8375.7 ms mean latency, 0 failures. | `glm-4-7-flash-safe-profiles-c002-74dc2794`: 30.545 tokens/sec, 8238.7 ms, `gpu_memory_utilization=0.84`, `moe_backend=triton`, interactivity mode. | Keep Triton MoE pinned; run deeper performance/tool workloads only after cache space is confirmed. |
| Qwen3.6 27B | `Qwen/Qwen3.6-27B`, Qwen parser/tool metadata recorded in the catalog. | Passed in `artifacts/models/qwen3-6-27b/live/summary.json` after a longer startup window. | 5.636 tokens/sec, 46312.7 ms mean latency, 0 failures. | `qwen3-6-27b-safe-profiles-c002-fcb682db`: 5.628 tokens/sec, 46377.7 ms, `gpu_memory_utilization=0.80`, interactivity mode. | Treat as smoke-ready but not performance-competitive in this safe profile pass. |
| Qwen3.5 27B | `Qwen/Qwen3.5-27B`, legacy comparison candidate. | Passed in `artifacts/models/qwen3-5-27b/live/summary.json`. | 5.634 tokens/sec, 46328.7 ms mean latency, 0 failures. | `qwen3-5-27b-safe-profiles-c002-c4dedd70`: 5.612 tokens/sec, 46506.7 ms, `gpu_memory_utilization=0.80`, interactivity mode. | Keep only if we want a generational delta; it did not improve over Qwen3.6 in this pass. |
| DeepSeek Coder V2 Lite Instruct | `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`, plain-chat-first profile with `--moe-backend triton`. | Passed in `artifacts/models/deepseek-coder-v2-lite-instruct/live/summary.json`; tool probe is unsupported/skipped by design. | 47.482 tokens/sec, 4997.7 ms mean latency, 0 failures. | `deepseek-coder-v2-lite-instruct-safe-profiles-c002-a7b18c4c`: 48.353 tokens/sec, 4908.0 ms, `gpu_memory_utilization=0.86`, `moe_backend=triton`, interactivity mode. | Best new-model single-user baseline so far; tool behavior needs a dedicated validation path before tool-use tuning. |

## GX10 Cache Hygiene

The GX10 root filesystem reports 916G total. After removing stale user-owned
model caches, root-owned Hugging Face caches, and Docker build cache, the latest
disk check showed 64G used, 805G available, and 8% usage.

The remaining top-level usage is ordinary system/project footprint:

- `/home`: 21G
- `/usr`: 16G
- `/var`: 4.6G
- `/opt`: 2.4G
- `/.cache`: 921M

New live model work should continue to run one model at a time, use the
profile-scoped `HF_HOME=$HOME/.cache/huggingface-vllm-optimizer`, and delete
the model cache after each completed block unless the next run reuses that same
model immediately.

Source notes:

- Gemma 4 E4B IT: https://huggingface.co/google/gemma-4-E4B-it and https://docs.vllm.ai/projects/recipes/en/stable/Google/Gemma4.html
- GLM 4.7 Flash: https://huggingface.co/zai-org/GLM-4.7-Flash
- Qwen3.6 27B: https://huggingface.co/Qwen/Qwen3.6-27B
- Qwen3.5 27B: https://huggingface.co/Qwen/Qwen3.5-27B
- DeepSeek Coder V2 Lite Instruct: https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct
