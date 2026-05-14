# Quickstart: Benchmark Concurrency

Generate local plans:

```powershell
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-coding-interactive-concurrent.json --out artifacts/benchmarks/qwen-concurrency/plan.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-interactive-concurrent.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/preview.json
```

Run live:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Confirmed result:

```text
Concurrent winner: gpu_memory_utilization=0.92, block_size=16,
max_num_batched_tokens=4096, max_num_seqs=16, performance_mode=interactivity

A/B decision: switch-to-recommended
Latency delta: -195.333 ms (-2.845%)
Throughput delta: +1.676 tokens/sec (+1.766%)
Failures: 0/9 requests per side
```
