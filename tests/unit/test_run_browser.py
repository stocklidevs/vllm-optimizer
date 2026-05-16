from pathlib import Path

from vllm_optimizer.artifacts import write_json, write_jsonl
from vllm_optimizer.run_browser import build_run_index, render_run_browser_html


def test_build_run_index_detects_known_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "sweeps" / "example" / "live"
    write_json(run_dir / "summary.json", {"success_count": 2, "failure_count": 0})
    write_json(run_dir / "ranking.json", {"sweep_id": "example"})
    write_jsonl(run_dir / "results.jsonl", [{"trial_id": "t1"}])
    report_dir = tmp_path / "reports" / "example"
    write_json(report_dir / "canonical-report.json", {"schema_version": "1.0"})

    index = build_run_index(tmp_path)

    assert index["schema_version"] == "1.0"
    assert index["run_count"] == 2
    entries = {entry["relative_dir"]: entry for entry in index["runs"]}
    assert entries["sweeps/example/live"]["artifact_paths"]["summary"].endswith("summary.json")
    assert entries["sweeps/example/live"]["artifact_paths"]["ranking"].endswith("ranking.json")
    assert entries["reports/example"]["artifact_paths"]["canonical_report"].endswith("canonical-report.json")


def test_render_run_browser_html_lists_entries(tmp_path: Path) -> None:
    write_json(tmp_path / "run" / "execution-status.json", {"overall_status": "running"})
    index = build_run_index(tmp_path)
    html = render_run_browser_html(index)

    assert "Run Browser" in html
    assert "execution_status" in html
    assert "run/execution-status.json" in html
