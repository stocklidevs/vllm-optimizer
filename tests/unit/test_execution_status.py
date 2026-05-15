from pathlib import Path

from vllm_optimizer.artifacts import write_json, write_jsonl
from vllm_optimizer.execution_status import build_execution_status, render_execution_status_html


def test_execution_status_summarizes_stages_trials_and_failures(tmp_path: Path) -> None:
    run_dir = _write_run_dir(tmp_path)

    status = build_execution_status(run_dir)

    assert status["overall_state"] == "failed"
    assert status["completed_stages"] == ["plan", "preview", "run"]
    assert status["trial_summary"]["total"] == 3
    assert status["trial_summary"]["by_status"]["completed"] == 2
    assert status["trial_summary"]["by_status"]["failed"] == 1
    assert status["failures"][0]["trial_id"] == "trial-3"
    assert status["stages"][0]["name"] == "plan"
    assert status["stages"][0]["state"] == "completed"
    assert status["artifacts"]["ranking"]["exists"] is False


def test_execution_status_handles_plan_without_summary(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    live_dir = run_dir / "live"
    write_json(
        run_dir / "pipeline-plan.json",
        {
            "mode": "run",
            "stages": [{"name": "plan", "artifact": (run_dir / "pipeline-plan.json").as_posix(), "remote": False}],
            "artifacts": {"live_dir": live_dir.as_posix()},
        },
    )

    status = build_execution_status(run_dir)

    assert status["overall_state"] == "planned"
    assert status["trial_summary"]["total"] == 0


def test_render_execution_status_html_contains_dashboard_sections(tmp_path: Path) -> None:
    status = build_execution_status(_write_run_dir(tmp_path))

    html = render_execution_status_html(status)

    assert "Execution Status" in html
    assert "failed" in html
    assert "Trial summary" in html
    assert "trial-3" in html
    assert "Artifacts" in html


def _write_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    live_dir = run_dir / "live"
    results = live_dir / "results.jsonl"
    ranking = live_dir / "ranking.json"
    write_json(
        run_dir / "pipeline-plan.json",
        {
            "mode": "run",
            "stages": [
                {"name": "plan", "artifact": (run_dir / "pipeline-plan.json").as_posix(), "remote": False},
                {"name": "preview", "artifact": (run_dir / "sweep-preview.json").as_posix(), "remote": False},
                {"name": "run", "artifact": live_dir.as_posix(), "remote": True},
                {"name": "report", "artifact": (run_dir / "report.json").as_posix(), "remote": False},
            ],
            "artifacts": {
                "pipeline_plan": (run_dir / "pipeline-plan.json").as_posix(),
                "sweep_preview": (run_dir / "sweep-preview.json").as_posix(),
                "live_dir": live_dir.as_posix(),
                "results": results.as_posix(),
                "ranking": ranking.as_posix(),
            },
        },
    )
    write_json(run_dir / "sweep-preview.json", {"blocked": False})
    write_json(
        run_dir / "pipeline-summary.json",
        {"mode": "run", "completed_stages": ["plan", "preview", "run"]},
    )
    write_jsonl(
        results,
        [
            {"trial_id": "trial-1", "status": "completed"},
            {"trial_id": "trial-2", "status": "completed"},
            {"trial_id": "trial-3", "status": "failed", "failure_reason": "benchmark failure"},
        ],
    )
    return run_dir
