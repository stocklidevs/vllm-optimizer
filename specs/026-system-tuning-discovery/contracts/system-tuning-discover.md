# Contract: `system-tuning-discover`

## Command

```powershell
uv run vllm-optimizer system-tuning-discover `
  --config config/local.gx10.json `
  --executor ssh `
  --out artifacts/system-tuning/gx10
```

## Mock Command

```powershell
uv run vllm-optimizer system-tuning-discover `
  --config tests/fixtures/discovery/local.gx10.mock.json `
  --executor mock `
  --mock-results tests/fixtures/system_tuning/mock_outputs.json `
  --out artifacts/system-tuning/mock
```

## Output Artifacts

- `raw-probes.json`: Every probe command, stdout, stderr, exit code, and timeout state.
- `catalog.json`: Structured tuning facts and knob classifications.
- `redaction-report.json`: Redaction metadata and artifact paths.

## Safety Contract

- Every command executed by this feature is classified `read-only`.
- The feature MUST reject any non-read-only probe definition.
- The feature MUST NOT run commands that write to system paths, change process state, or alter NVIDIA/Linux settings.
