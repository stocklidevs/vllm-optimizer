from pathlib import Path

import pytest

from vllm_optimizer.flag_catalog import (
    FlagCatalogError,
    build_flag_catalog,
    load_policy,
    parse_serve_help,
)


def test_parse_serve_help_extracts_long_flags() -> None:
    help_text = Path("tests/fixtures/vllm/serve-help.txt").read_text(encoding="utf-8")

    flags = parse_serve_help(help_text)
    names = {flag["name"] for flag in flags}

    assert "gpu-memory-utilization" in names
    assert "max-num-batched-tokens" in names
    assert "performance-mode" in names


def test_parse_serve_help_rejects_empty_text() -> None:
    with pytest.raises(FlagCatalogError, match="empty"):
        parse_serve_help("")


def test_build_flag_catalog_classifies_policy_flags() -> None:
    policy = load_policy(Path("config/vllm-flags/qwen-safe-policy.json"))
    help_text = Path("tests/fixtures/vllm/serve-help.txt").read_text(encoding="utf-8")

    catalog = build_flag_catalog(policy, help_text, "vllm 0.20.1")
    safe_names = {item["name"] for item in catalog["categories"]["safe_session_sweepable"]}
    risky_names = {item["name"] for item in catalog["categories"]["session_risky"]}

    assert catalog["vllm_version"] == "0.20.1"
    assert "max-num-seqs" in safe_names
    assert "kv-cache-dtype" in risky_names
    assert any(item["name"] == "cpu-offload-gb" for item in catalog["unavailable_policy_flags"])
