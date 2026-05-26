# Project Status

Last updated: 2026-05-26

Current release: 0.54.6

## What Exists

vLLM Optimizer is a local, deterministic optimization lab for the GX10. The
CLI remains the source of truth, and the cockpit is a controller and reporting
surface over the same artifacts.

The current system can:

- Generate deterministic vLLM sweep plans and previews.
- Run gated live sweeps against the GX10.
- Rank candidates for throughput, latency, balanced score, and single-user
  responsiveness.
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

Validated on 2026-05-26 against upstream model pages and vLLM
documentation. "Baseline" means the starting serve/readiness baseline to record
before optimization. Only Qwen3 Coder Next has local GX10 performance baselines
today; the new models are not performance-ranked until Spec 071 smoke checks
and first benchmarks run.

| Model | Runtime lane | Validation baseline | Local baseline status | Next action |
| --- | --- | --- | --- | --- |
| Qwen3 Coder Next AWQ 4-bit | Local vLLM | Existing profile `cyankiwi/Qwen3-Coder-Next-AWQ-4bit`, served as `Qwen3-Coder-Next`, port 8001, `max_model_len=32768`, `gpu_memory_utilization=0.90`, `qwen3_coder` tool parser, interactivity mode. | Measured GX10 reference. Confirmed C8 profile: 6644.200 ms mean latency and 97.683 tokens/sec; saturation sweep candidate recorded 98.415 aggregate tokens/sec. | Keep as the current reference model while new model smoke baselines are added. |
| Gemma 4 E4B IT | Local vLLM | User-provided baseline: `google/gemma-4-E4B-it`, served as `Gemma-4-E4B-IT`, port 8001, `max_model_len=16384`, `gpu_memory_utilization=0.80`, auto tool choice, `gemma4` tool parser, chat template `~/vllm-templates/tool_chat_template_gemma4.jinja`. | Serve recipe captured, performance not measured in this repo yet. | First Spec 071 smoke target; verify template, plain chat, and tool-call behavior before sweeps. |
| GLM 4.7 Flash | Local vLLM candidate | Upstream model `zai-org/GLM-4.7-Flash`; upstream card shows vLLM serving support and describes it as a 30B-A3B MoE model. Start with a plain local smoke baseline before enabling tool/parser assumptions. | Not smoked or benchmarked locally yet. | Add catalog entry, generate dry-run smoke plan, then live serve readiness if GX10 dependencies match. |
| Qwen3.6 27B | Local vLLM candidate | Upstream model `Qwen/Qwen3.6-27B`; upstream card lists vLLM compatibility, recommends `vllm>=0.19.0`, and documents Qwen tool-call parser support. | Not smoked or benchmarked locally yet. | Treat as the highest-priority larger Qwen comparison after Gemma; validate memory fit before long-context sweeps. |
| Qwen3.5 27B | Local vLLM candidate | Upstream model `Qwen/Qwen3.5-27B`; upstream card lists vLLM compatibility, long-context defaults, and `qwen3_coder` tool-call parser support. | Not smoked or benchmarked locally yet. | Optional legacy comparison after Qwen3.6, useful only if we want a generational delta. |
| DeepSeek Coder V2 Lite Instruct | Local vLLM candidate | Upstream model `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`; upstream card documents 16B total parameters, 2.4B active parameters, 128k context, and a plain vLLM serve example. | Not smoked or benchmarked locally yet. | Add a conservative plain-chat smoke first; tool behavior requires separate validation. |

Source notes:

- Gemma 4 E4B IT: https://huggingface.co/google/gemma-4-E4B-it and https://docs.vllm.ai/projects/recipes/en/stable/Google/Gemma4.html
- GLM 4.7 Flash: https://huggingface.co/zai-org/GLM-4.7-Flash
- Qwen3.6 27B: https://huggingface.co/Qwen/Qwen3.6-27B
- Qwen3.5 27B: https://huggingface.co/Qwen/Qwen3.5-27B
- DeepSeek Coder V2 Lite Instruct: https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct
