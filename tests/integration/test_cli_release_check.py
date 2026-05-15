from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_release_check_writes_json_and_markdown(tmp_path: Path) -> None:
    out = tmp_path / "release-check.json"
    markdown_out = tmp_path / "release-check.md"

    assert main(["release-check", "--out", str(out), "--markdown-out", str(markdown_out)]) == 0

    report = read_json(out)
    assert report["overall_status"] == "pass"
    assert any(check["id"] == "active-speckit-feature" for check in report["checks"])

    markdown = markdown_out.read_text(encoding="utf-8")
    assert "# vLLM Optimizer Release Check" in markdown
    assert "active-speckit-feature" in markdown
