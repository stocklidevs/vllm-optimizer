# Quickstart: A/B Benchmark Confirmation

Run three original profile repetitions:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r3 --timeout-seconds 1200
```

Run three recommended profile repetitions:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/recommended-r3 --timeout-seconds 1200
```

Generate the confirmation report:

```powershell
uv run vllm-optimizer ab-report --original-label original --recommended-label recommended --original-summaries artifacts/benchmarks/qwen-ab/original-r1/summary.json artifacts/benchmarks/qwen-ab/original-r2/summary.json artifacts/benchmarks/qwen-ab/original-r3/summary.json --recommended-summaries artifacts/benchmarks/qwen-ab/recommended-r1/summary.json artifacts/benchmarks/qwen-ab/recommended-r2/summary.json artifacts/benchmarks/qwen-ab/recommended-r3/summary.json --prompt-set-id qwen-baseline-v1 --out artifacts/reports/qwen-ab-confirmation.json --markdown-out artifacts/reports/qwen-ab-confirmation.md
```
