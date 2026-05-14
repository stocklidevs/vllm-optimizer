# CLI Contract: Risky Winner Confirmation

## `promote-confirmed-profile`

Writes a promoted profile only if an A/B confirmation report approves switching to the candidate.

```powershell
uv run vllm-optimizer promote-confirmed-profile `
  --confirmation-report artifacts/reports/qwen-risky-winner-confirmation.json `
  --ranking artifacts/sweeps/qwen-risky-session-small/live/ranking.json `
  --objective balanced `
  --profile-out config/profiles/qwen3-coder-next-awq-recommended.json `
  --summary-out artifacts/promotions/qwen3-coder-next-awq-recommended-risky-confirmed.md `
  --profile-id qwen3-coder-next-awq-recommended `
  --expected-recommended-label risky-winner `
  --force
```

### Behavior

- Exit `0` and write both outputs when `decision.status` is `switch-to-recommended`.
- Exit `2` and leave outputs unchanged when the report is inconclusive, keeps the original, is malformed, or has a mismatched recommended label.
- Refuse existing output files unless `--force` is passed.

## Live Confirmation Sequence

The risky winner candidate is benchmarked as the `recommended` side of the existing A/B report because it is the candidate under consideration.
