from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_system_tuning_discover_mock_writes_artifacts(tmp_path: Path) -> None:
    exit_code = main(
        [
            "system-tuning-discover",
            "--config",
            "tests/fixtures/discovery/local.gx10.mock.json",
            "--executor",
            "mock",
            "--mock-results",
            "tests/fixtures/system_tuning/mock_outputs.json",
            "--out",
            str(tmp_path / "system-tuning"),
        ]
    )

    assert exit_code == 0
    catalog = read_json(tmp_path / "system-tuning" / "catalog.json")
    assert catalog["target_label"] == "gx10"
    assert catalog["entries"]["cpu.governor"]["current_value"] == "performance"
    assert catalog["entries"]["vllm.env"]["current_value"]["CUDA_VISIBLE_DEVICES"] == "0"
