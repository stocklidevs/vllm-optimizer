# Quickstart: vLLM Flag Catalog

Generate from fixture help:

```powershell
uv run vllm-optimizer flag-catalog --policy config/vllm-flags/qwen-safe-policy.json --help-file tests/fixtures/vllm/serve-help.txt --out artifacts/vllm-flags/fixture/catalog.json
```

Capture from GX10 read-only:

```powershell
uv run vllm-optimizer flag-catalog-capture --config config/local.gx10.json --profile config/profiles/qwen3-coder-next-awq.json --policy config/vllm-flags/qwen-safe-policy.json --out artifacts/vllm-flags/gx10-qwen --executor ssh
```
