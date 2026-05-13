from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.discovery import load_target, run_discovery
from vllm_optimizer.ssh import MockExecutor


def test_discovery_parses_normalized_facts(tmp_path: Path) -> None:
    target = load_target(Path("tests/fixtures/discovery/local.gx10.mock.json"))
    outputs = read_json(Path("tests/fixtures/discovery/mock_outputs.json"))

    result = run_discovery(target, MockExecutor(outputs), tmp_path)
    facts = result["summary"]["facts"]

    assert facts["connectivity"] is True
    assert facts["hostname"] == "gx10"
    assert facts["os"]["pretty_name"] == "Ubuntu 24.04.2 LTS"
    assert facts["gpu"]["name"] == "NVIDIA GeForce RTX 5090"
    assert facts["nvidia_driver"] == "575.51.03"
    assert facts["cuda_visible"] is True
    assert facts["python"]["version"] == "Python 3.12.3"
    assert facts["vllm"]["available"] is True
    assert facts["vllm"]["version"] == "0.8.5"
