# Quickstart: Workload Leaderboard

Generate the current Qwen workload leaderboard:

```powershell
uv run vllm-optimizer workload-report --workload interactive=artifacts/sweeps/qwen-high-impact-interactive/live/ranking.json long=artifacts/sweeps/qwen-high-impact-long/live/ranking.json tool-json=artifacts/sweeps/qwen-high-impact-tool-json/live/ranking.json concurrent-interactive=artifacts/sweeps/qwen-high-impact-interactive-concurrent/live/ranking.json --promoted-profile concurrent-interactive=config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --out artifacts/reports/qwen-workload-leaderboard.json --markdown-out artifacts/reports/qwen-workload-leaderboard.md
```

Current highlights:

```text
Promoted concurrent profile: qwen3-coder-next-awq-concurrent-recommended
Sequential workload winners remain evidence/watch items.
FP8 KV cache candidates need ninja installed or exposed on the GX10 before rerun.
```
