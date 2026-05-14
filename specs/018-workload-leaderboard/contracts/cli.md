# CLI Contract: Workload Leaderboard

## Generate Qwen Leaderboard

```powershell
uv run vllm-optimizer workload-report --workload interactive=artifacts/sweeps/qwen-high-impact-interactive/live/ranking.json long=artifacts/sweeps/qwen-high-impact-long/live/ranking.json tool-json=artifacts/sweeps/qwen-high-impact-tool-json/live/ranking.json concurrent-interactive=artifacts/sweeps/qwen-high-impact-interactive-concurrent/live/ranking.json --promoted-profile concurrent-interactive=config/profiles/qwen3-coder-next-awq-concurrent-recommended.json --out artifacts/reports/qwen-workload-leaderboard.json --markdown-out artifacts/reports/qwen-workload-leaderboard.md
```

### Behavior

- Exit `0` and write JSON when all ranking/profile paths exist.
- Exit `2` when any ranking path is missing, malformed, or lacks a balanced objective.
- Markdown output is optional.
