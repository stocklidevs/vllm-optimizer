from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_discover_mock_writes_redacted_artifacts(tmp_path: Path) -> None:
    code = main(
        [
            "discover",
            "--config",
            "tests/fixtures/discovery/local.gx10.mock.json",
            "--executor",
            "mock",
            "--mock-results",
            "tests/fixtures/discovery/mock_outputs.json",
            "--out",
            str(tmp_path),
        ]
    )

    assert code == 0
    summary = read_json(tmp_path / "summary.json")
    raw_text = (tmp_path / "raw-probes.json").read_text(encoding="utf-8")
    assert summary["status"] == "completed"
    assert summary["facts"]["hostname"] == "gx10"
    assert "203.0.113.10" not in raw_text
