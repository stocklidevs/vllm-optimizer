# CLI Contract: A/B Benchmark Confirmation

## Generate A/B confirmation report

```powershell
uv run vllm-optimizer ab-report --original-label original --recommended-label recommended --original-summaries artifacts/benchmarks/qwen-ab/original-r1/summary.json artifacts/benchmarks/qwen-ab/original-r2/summary.json artifacts/benchmarks/qwen-ab/original-r3/summary.json --recommended-summaries artifacts/benchmarks/qwen-ab/recommended-r1/summary.json artifacts/benchmarks/qwen-ab/recommended-r2/summary.json artifacts/benchmarks/qwen-ab/recommended-r3/summary.json --prompt-set-id qwen-baseline-v1 --out artifacts/reports/qwen-ab-confirmation.json --markdown-out artifacts/reports/qwen-ab-confirmation.md
```

Expected behavior:
- Reads local summary artifacts only.
- Writes JSON and optional Markdown reports.
- Fails before writing output if any summary is missing or malformed.

## Live repetition commands

Live repetitions are run with the existing benchmark command:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-ab/original-r1 --timeout-seconds 1200
```

Repeat for original and recommended profile output directories.
