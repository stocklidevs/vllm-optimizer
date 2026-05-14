# CLI Contract: Benchmark Concurrency

## Dry Run

```powershell
uv run vllm-optimizer benchmark-plan --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-coding-interactive-concurrent.json --out artifacts/benchmarks/qwen-concurrency/plan.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-high-impact-interactive-concurrent.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/preview.json
```

## Live Sweep

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-high-impact-interactive-concurrent/plan.json --out artifacts/sweeps/qwen-high-impact-interactive-concurrent/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

## Confirmation

```powershell
uv run vllm-optimizer ab-report --original-label current-concurrent-default --recommended-label concurrent-winner --original-summaries <three-current-summaries> --recommended-summaries <three-winner-summaries> --prompt-set-id qwen-coding-interactive-concurrent-v1 --out artifacts/reports/qwen-concurrency-confirmation.json --markdown-out artifacts/reports/qwen-concurrency-confirmation.md
uv run vllm-optimizer promote-confirmed-profile --confirmation-report artifacts/reports/qwen-concurrency-confirmation.json --ranking artifacts/sweeps/qwen-high-impact-interactive-concurrent/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --summary-out artifacts/promotions/qwen3-coder-next-awq-concurrent-recommended.md --profile-id qwen3-coder-next-awq-concurrent-recommended --expected-recommended-label concurrent-winner
```
