from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_flag_catalog_cli_writes_catalog(tmp_path: Path) -> None:
    out = tmp_path / "catalog.json"

    exit_code = main(
        [
            "flag-catalog",
            "--policy",
            "config/vllm-flags/qwen-safe-policy.json",
            "--help-file",
            "tests/fixtures/vllm/serve-help.txt",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    catalog = read_json(out)
    assert catalog["policy_id"] == "qwen-safe-policy-v1"
    assert catalog["flag_count"] > 0


def test_flag_catalog_capture_mock_writes_artifacts(tmp_path: Path) -> None:
    mock_results = tmp_path / "mock-results.json"
    mock_results.write_text(
        """{
  "vllm-version": {
    "exit_code": 0,
    "stdout": "vllm 0.20.1"
  },
  "vllm-serve-help": {
    "exit_code": 0,
    "stdout": "--gpu-memory-utilization GPU_MEMORY_UTILIZATION\\n--max-num-batched-tokens MAX_NUM_BATCHED_TOKENS\\n--performance-mode PERFORMANCE_MODE\\n"
  }
}""",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "flag-catalog-capture",
            "--config",
            "tests/fixtures/discovery/local.gx10.mock.json",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--policy",
            "config/vllm-flags/qwen-safe-policy.json",
            "--out",
            str(tmp_path / "capture"),
            "--executor",
            "mock",
            "--mock-results",
            str(mock_results),
        ]
    )

    assert exit_code == 0
    catalog = read_json(tmp_path / "capture" / "catalog.json")
    assert catalog["vllm_version"] == "0.20.1"
    assert (tmp_path / "capture" / "serve-help.txt").exists()
