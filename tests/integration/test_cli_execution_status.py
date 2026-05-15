from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json, write_jsonl
from vllm_optimizer.cli import main


def test_execution_status_cli_writes_json_and_html(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    out = tmp_path / "status.json"
    html = tmp_path / "status.html"
    _write_run_dir(run_dir)

    exit_code = main(["execution-status", "--run-dir", str(run_dir), "--out", str(out), "--html-out", str(html)])

    assert exit_code == 0
    status = read_json(out)
    assert status["overall_state"] == "completed"
    assert status["trial_summary"]["total"] == 1
    assert "Execution Status" in html.read_text(encoding="utf-8")


def test_execution_status_cli_rejects_missing_run_dir(tmp_path: Path) -> None:
    exit_code = main(["execution-status", "--run-dir", str(tmp_path / "missing"), "--out", str(tmp_path / "status.json")])

    assert exit_code == 2


def _write_run_dir(run_dir: Path) -> None:
    results = run_dir / "live" / "results.jsonl"
    write_json(
        run_dir / "pipeline-plan.json",
        {
            "mode": "run",
            "stages": [{"name": "run", "artifact": (run_dir / "live").as_posix(), "remote": True}],
            "artifacts": {"results": results.as_posix(), "live_dir": (run_dir / "live").as_posix()},
        },
    )
    write_json(run_dir / "pipeline-summary.json", {"completed_stages": ["plan", "preview", "run"]})
    write_jsonl(results, [{"trial_id": "trial-1", "status": "completed"}])
