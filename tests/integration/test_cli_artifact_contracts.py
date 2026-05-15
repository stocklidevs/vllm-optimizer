from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_artifact_contracts_writes_json_and_markdown(tmp_path: Path) -> None:
    out = tmp_path / "contracts.json"
    markdown_out = tmp_path / "contracts.md"

    assert main(["artifact-contracts", "--out", str(out), "--markdown-out", str(markdown_out)]) == 0

    catalog = read_json(out)
    assert catalog["schema_version"] == "1.0"
    assert any(contract["artifact_type"] == "pipeline-control-manifest" for contract in catalog["contracts"])

    markdown = markdown_out.read_text(encoding="utf-8")
    assert "# vLLM Optimizer Artifact Contracts" in markdown
    assert "pipeline-control-manifest" in markdown
