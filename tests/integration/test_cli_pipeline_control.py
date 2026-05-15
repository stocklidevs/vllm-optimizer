from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_pipeline_control_cli_writes_manifest_and_html(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    out = tmp_path / "control.json"
    html = tmp_path / "control.html"
    write_json(
        catalog,
        {
            "groups": [
                {
                    "id": "safe",
                    "label": "Safe Sweep",
                    "family": "safe-vllm",
                    "safety_tier": "safe-session",
                    "config_path": "config/sweeps/qwen-small-sweep.json",
                    "command_kind": "sweep",
                    "requires_opt_in": False,
                }
            ]
        },
    )

    exit_code = main(["pipeline-control", "--catalog", str(catalog), "--group-id", "safe", "--out", str(out), "--html-out", str(html)])

    assert exit_code == 0
    manifest = read_json(out)
    assert manifest["group"]["id"] == "safe"
    assert any(stage["name"] == "run" for stage in manifest["stages"])
    assert "Pipeline Control" in html.read_text(encoding="utf-8")


def test_pipeline_control_cli_rejects_unknown_group(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    write_json(catalog, {"groups": []})

    exit_code = main(["pipeline-control", "--catalog", str(catalog), "--group-id", "missing", "--out", str(tmp_path / "out.json")])

    assert exit_code == 2
