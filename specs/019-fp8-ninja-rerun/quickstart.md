# Quickstart: FP8 Ninja Rerun

Generate FP8 rerun plans and previews:

```powershell
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-fp8-rerun-interactive.json --out artifacts/sweeps/qwen-fp8-rerun-interactive/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-fp8-rerun-interactive/plan.json --out artifacts/sweeps/qwen-fp8-rerun-interactive/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-fp8-rerun-long.json --out artifacts/sweeps/qwen-fp8-rerun-long/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-fp8-rerun-long/plan.json --out artifacts/sweeps/qwen-fp8-rerun-long/preview.json
uv run vllm-optimizer sweep-plan --sweep config/sweeps/qwen-fp8-rerun-tool-json.json --out artifacts/sweeps/qwen-fp8-rerun-tool-json/plan.json
uv run vllm-optimizer sweep-preview --plan artifacts/sweeps/qwen-fp8-rerun-tool-json/plan.json --out artifacts/sweeps/qwen-fp8-rerun-tool-json/preview.json
```

Run the live reruns with explicit risky-session opt-in:

```powershell
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-fp8-rerun-interactive/plan.json --out artifacts/sweeps/qwen-fp8-rerun-interactive/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-fp8-rerun-long/plan.json --out artifacts/sweeps/qwen-fp8-rerun-long/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
uv run vllm-optimizer sweep-run --config config/local.gx10.json --plan artifacts/sweeps/qwen-fp8-rerun-tool-json/plan.json --out artifacts/sweeps/qwen-fp8-rerun-tool-json/live --timeout-seconds 1200 --continue-on-failure --allow-risky-session-flags
```

Refresh the workload leaderboard with FP8 rerun labels:

```powershell
uv run vllm-optimizer workload-report --workload interactive=artifacts/sweeps/qwen-high-impact-interactive/live/ranking.json long=artifacts/sweeps/qwen-high-impact-long/live/ranking.json tool-json=artifacts/sweeps/qwen-high-impact-tool-json/live/ranking.json concurrent-interactive=artifacts/sweeps/qwen-high-impact-interactive-concurrent/live/ranking.json fp8-interactive=artifacts/sweeps/qwen-fp8-rerun-interactive/live/ranking.json fp8-long=artifacts/sweeps/qwen-fp8-rerun-long/live/ranking.json fp8-tool-json=artifacts/sweeps/qwen-fp8-rerun-tool-json/live/ranking.json --promoted-profile concurrent-interactive=config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --out artifacts/reports/qwen-workload-leaderboard.json --markdown-out artifacts/reports/qwen-workload-leaderboard.md
```

Current FP8 rerun highlights:

```text
plain fp8 interactive: 6080.833 ms, 39.770 tokens/sec, 0/2 failures
plain fp8 long: 20561.000 ms, 36.008 tokens/sec, 0/2 failures
plain fp8 tool-json: 5616.167 ms, 40.297 tokens/sec, 0/2 failures
fp8_e5m2: rejected by vLLM for this FP8 checkpoint
```
