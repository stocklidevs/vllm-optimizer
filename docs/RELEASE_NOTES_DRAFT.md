# v0.56.8-alpha Release Notes Draft

vLLM Optimizer is a deterministic public-alpha lab for planning, running, and
reporting vLLM serving experiments. It is designed for local and self-hosted
model operators who want evidence before changing serve flags.

## Highlights

- Objective-first cockpit for Balanced, Performance, Single User, Stability,
  and Tool Use workflows.
- Deterministic CLI artifacts for plans, previews, live runs, rankings,
  canonical reports, confirmation, and promotion gates.
- Safe local quickstart that runs without SSH, model downloads, or GPU access.
- GX10-validated live workflow with explicit SSH config, risky/session flag
  gates, and manual promotion. Other Linux NVIDIA/vLLM hosts can be targeted by
  adapting local config, serve profiles, and conservative sweep ranges.
- Multi-model catalog coverage for Qwen, Gemma, GLM, Qwen 27B variants, and
  DeepSeek Coder V2 Lite Instruct.
- Public release gates covering pytest, release-check, pinned npm install,
  npm audit, CI, issue templates, and private-reference scanning.

## Results To Explain Publicly

The headline Qwen C8 result is aggregate throughput, not single-user stream
speed:

| Scenario | Baseline | Best observed | Meaning |
| --- | ---: | ---: | --- |
| Qwen C1 single-user | 47.525 tok/s | 49.726 tok/s | Small one-user improvement. |
| Qwen C8 saturation | 47.525 tok/s C1 reference | 98.415 tok/s aggregate | Better shared-service utilization under eight concurrent requests. |
| Confirmed Qwen C8 profile | 96.041 tok/s | 97.683 tok/s | Repeated confirmation supported the concurrent profile. |

For more detail, use `docs/RESULTS.md` as the source when writing the GitHub
release body.

## Safety Notes

- Live runs can start and stop vLLM, run load tests, and download large model
  files.
- Keep real SSH targets and credentials in ignored local config files.
- Risky-session flags, session tuning, live execution, and promotion require
  explicit gates.
- Persistent Linux, NVIDIA, firmware, kernel, service, Docker, and credential
  changes are outside the public-alpha optimizer scope.

## Known Limitations

- Live validation has primarily followed one GX10-style workflow. Other
  SSH-accessible Linux NVIDIA/vLLM hosts should begin with previews, smoke
  tests, and conservative sweeps.
- Results vary by model, quantization, vLLM version, GPU, driver, prompt set,
  and concurrency.
- Tool-use scoring is still early; parser/JSON correctness needs deeper
  model-specific validation.
- Root-owned cache and Docker cleanup remain documented maintenance actions,
  not automated optimizer behavior.

## Suggested GitHub Release Body

````markdown
vLLM Optimizer `v0.56.8-alpha` is the first public alpha of a deterministic
vLLM optimization lab.

It can be cloned and validated locally without SSH or GPU access:

```powershell
uv sync
uv run pytest
uv run vllm-optimizer release-check --out artifacts/catalog/release-check.json --markdown-out artifacts/catalog/release-check.md
```

Use the local cockpit with:

```powershell
uv run vllm-optimizer cockpit-launch
```

This alpha focuses on reproducible artifacts, explicit live-run gates, and
clear reporting. Performance numbers are workload-specific; the strongest Qwen
C8 result is aggregate throughput for concurrent requests, not one-user stream
speed.
````
