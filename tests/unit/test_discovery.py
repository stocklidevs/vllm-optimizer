from dataclasses import replace
from pathlib import Path

import pytest

from vllm_optimizer.discovery import DiscoveryError, PROBES, load_target, validate_probe_catalog


def test_load_target_from_fixture() -> None:
    target = load_target(Path("tests/fixtures/discovery/local.gx10.mock.json"))

    assert target.target_label == "gx10"
    assert target.ssh_destination == "mock-user@203.0.113.10"
    assert "203.0.113.10" in target.redact_values


def test_load_target_rejects_bad_timeout(tmp_path: Path) -> None:
    config = tmp_path / "bad.json"
    config.write_text(
        '{"target_label":"gx10","ssh_destination":"mock","timeout_seconds":0}',
        encoding="utf-8",
    )

    with pytest.raises(DiscoveryError, match="timeout_seconds"):
        load_target(config)


def test_validate_probe_catalog_blocks_non_read_only() -> None:
    bad_probe = replace(PROBES[0], classification="session-mutating")  # type: ignore[arg-type]

    with pytest.raises(DiscoveryError, match="non-read-only"):
        validate_probe_catalog((bad_probe,))
