# Data Model: Expanded Qwen Sweep

## ExpandedSweepDefinition

- `sweep_id`: `qwen-expanded-safe`
- `parameters.gpu_memory_utilization`: 0.88, 0.90, 0.92
- `parameters.performance_mode`: interactivity, throughput
- `parameters.max_model_len`: 32768
- `repetitions`: 3
- `objectives`: throughput, latency, balanced

## ExpandedCandidate

- `candidate_id`
- `gpu_memory_utilization`
- `performance_mode`
- `max_model_len`
- `repetitions`

## ExpandedRunArtifacts

- Plan JSON
- Preview JSON
- Results JSONL
- Per-repetition benchmark artifacts
- Ranking JSON
- Comparison report JSON/Markdown
