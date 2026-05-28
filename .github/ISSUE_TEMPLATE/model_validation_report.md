---
name: Model validation report
about: Share baseline, sweep, or cockpit evidence for a model/hardware setup
title: "[model]: "
labels: model-validation
assignees: ""
---

## Model And Hardware

- Model:
- Quantization:
- vLLM version:
- GPU / system:
- Driver / CUDA, if known:

## Workflow

- Objective: Balanced / Performance / Single User / Stability / Tool Use
- Sweep or profile path:
- Prompt set:
- Concurrency:
- Repetitions:

## Results

| Metric | Baseline | Best candidate | Delta |
| --- | ---: | ---: | ---: |
| tokens/sec | | | |
| latency ms | | | |
| failures | | | |

## Interpretation

Explain whether the result improves one-user responsiveness, aggregate
throughput under concurrent load, stability, or tool/JSON behavior.

## Artifacts

List shareable artifact paths or attach redacted report snippets. Do not include
private SSH targets, usernames, tokens, passwords, or private local paths.
