from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_cli_run_browser_writes_json_and_html(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    write_json(artifacts / "optimizer-runs" / "demo" / "pipeline-summary.json", {"completed_stages": ["plan"]})
    out = tmp_path / "run-index.json"
    html = tmp_path / "run-index.html"

    assert main(["run-browser", "--artifacts-root", str(artifacts), "--out", str(out), "--html-out", str(html)]) == 0

    index = read_json(out)
    assert index["run_count"] == 1
    assert index["runs"][0]["artifact_paths"]["pipeline_summary"].endswith("pipeline-summary.json")
    assert "Run Browser" in html.read_text(encoding="utf-8")
