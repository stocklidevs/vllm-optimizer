from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_knob_groups_cli_writes_catalog_and_html(tmp_path: Path) -> None:
    out = tmp_path / "knob-groups.json"
    html = tmp_path / "knob-groups.html"

    exit_code = main(["knob-groups", "--config-root", "config", "--out", str(out), "--html-out", str(html)])

    assert exit_code == 0
    catalog = read_json(out)
    assert catalog["group_count"] >= 5
    assert any(group["requires_opt_in"] for group in catalog["groups"])
    assert "Tuning Area Selector" in html.read_text(encoding="utf-8")


def test_knob_groups_cli_rejects_missing_config_root(tmp_path: Path) -> None:
    exit_code = main(["knob-groups", "--config-root", str(tmp_path / "missing"), "--out", str(tmp_path / "out.json")])

    assert exit_code == 2
