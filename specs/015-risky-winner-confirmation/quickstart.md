# Quickstart: Risky Winner Confirmation

Generate a reusable risky winner profile from the risky-session sweep ranking:

```powershell
uv run vllm-optimizer promote-profile --ranking artifacts/sweeps/qwen-risky-session-small/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-risky-winner.json --summary-out artifacts/promotions/qwen3-coder-next-awq-risky-winner.md --profile-id qwen3-coder-next-awq-risky-winner
```

Run three current recommended repetitions:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-recommended.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/current-r3 --timeout-seconds 1200
```

Run three risky winner repetitions:

```powershell
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r1 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r2 --timeout-seconds 1200
uv run vllm-optimizer benchmark-run --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq-risky-winner.json --prompts config/prompts/qwen-baseline.json --out artifacts/benchmarks/qwen-risky-ab/risky-r3 --timeout-seconds 1200
```

Generate the A/B report:

```powershell
uv run vllm-optimizer ab-report --original-label current-recommended --recommended-label risky-winner --original-summaries artifacts/benchmarks/qwen-risky-ab/current-r1/summary.json artifacts/benchmarks/qwen-risky-ab/current-r2/summary.json artifacts/benchmarks/qwen-risky-ab/current-r3/summary.json --recommended-summaries artifacts/benchmarks/qwen-risky-ab/risky-r1/summary.json artifacts/benchmarks/qwen-risky-ab/risky-r2/summary.json artifacts/benchmarks/qwen-risky-ab/risky-r3/summary.json --prompt-set-id qwen-baseline-v1 --out artifacts/reports/qwen-risky-winner-confirmation.json --markdown-out artifacts/reports/qwen-risky-winner-confirmation.md
```

Promote only if the A/B report approves switching to the risky winner:

```powershell
uv run vllm-optimizer promote-confirmed-profile --confirmation-report artifacts/reports/qwen-risky-winner-confirmation.json --ranking artifacts/sweeps/qwen-risky-session-small/live/ranking.json --objective balanced --profile-out config/profiles/qwen3-coder-next-awq-recommended.json --summary-out artifacts/promotions/qwen3-coder-next-awq-recommended-risky-confirmed.md --profile-id qwen3-coder-next-awq-recommended --expected-recommended-label risky-winner --force
```
