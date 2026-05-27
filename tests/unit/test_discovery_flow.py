from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.discovery import load_target, run_discovery
from vllm_optimizer.ssh import MockExecutor


def test_discovery_skips_remaining_probes_when_connectivity_fails(tmp_path: Path) -> None:
    target = load_target(Path("tests/fixtures/discovery/local.gx10.mock.json"))
    executor = MockExecutor(
        {
            "connectivity": {
                "exit_code": 255,
                "stdout": "",
                "stderr": "connection timed out",
            }
        }
    )

    result = run_discovery(target, executor, tmp_path)

    assert result["status"] == "connectivity-failed"
    raw = read_json(tmp_path / "raw-probes.json")
    skipped = [item for item in raw["probes"] if item["status"] == "skipped"]
    assert len(skipped) == 6


def test_discovery_success_saves_redacted_artifacts(tmp_path: Path) -> None:
    target = load_target(Path("tests/fixtures/discovery/local.gx10.mock.json"))
    outputs = read_json(Path("tests/fixtures/discovery/mock_outputs.json"))

    result = run_discovery(target, MockExecutor(outputs), tmp_path)

    assert result["status"] == "completed"
    raw_text = (tmp_path / "raw-probes.json").read_text(encoding="utf-8")
    summary_text = (tmp_path / "summary.json").read_text(encoding="utf-8")
    assert "203.0.113.10" not in raw_text
    assert "/home/mock-user/private-models" not in raw_text
    assert "203.0.113.10" not in summary_text
    assert result["redaction"]["redacted_value_count"] > 0
