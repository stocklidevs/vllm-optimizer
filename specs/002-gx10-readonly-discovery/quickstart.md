# Quickstart: GX10 Read-Only Discovery

This quickstart stops before real GX10 connection.

## 1. Prepare local config later

Copy `config/gx10.example.json` to an ignored local config when ready:

```powershell
Copy-Item config/gx10.example.json config/local.gx10.json
```

Then replace the example SSH destination locally and include the IP address in
`redact_values`.

## 2. Run mock discovery

```powershell
uv run vllm-optimizer discover --config tests/fixtures/discovery/local.gx10.mock.json --executor mock --mock-results tests/fixtures/discovery/mock_outputs.json --out artifacts/discovery/mock
```

Expected result:
- `artifacts/discovery/mock/raw-probes.json`
- `artifacts/discovery/mock/summary.json`
- `artifacts/discovery/mock/redaction-report.json`

## 3. Run tests

```powershell
uv run pytest
```

## 4. Run live read-only discovery

Only after key-based SSH works:

```powershell
uv run vllm-optimizer discover --config config/local.gx10.json --executor ssh --out artifacts/discovery/gx10-live
```
