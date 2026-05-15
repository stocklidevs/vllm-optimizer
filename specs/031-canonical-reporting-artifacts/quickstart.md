# Quickstart: Canonical Reporting Artifacts

Generate a canonical report for the latest session tuning sweep:

```powershell
uv run vllm-optimizer canonical-report --family session-tuning-sweep --label qwen-runtime-env --ranking artifacts/session-tuning-sweeps/qwen-runtime-env/live/ranking.json --summary artifacts/session-tuning-sweeps/qwen-runtime-env/live/summary.json --out artifacts/reports/qwen-runtime-env/canonical-report.json --markdown-out artifacts/reports/qwen-runtime-env/report.md
```

Expected result:

- `canonical-report.json` contains the machine-readable source of truth for future web dashboards.
- `report.md` explains whether a candidate should be confirmed, promoted, or rejected in favor of baseline.
- No GX10 connection is required.
