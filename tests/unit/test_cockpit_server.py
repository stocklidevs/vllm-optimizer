from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cockpit_server import (
    CockpitServerConfig,
    CockpitServerError,
    CockpitJobStore,
    handle_controller_action,
    render_active_cockpit,
)


def test_cockpit_server_plan_action_writes_pipeline_artifacts(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "server-plan-test" / tmp_path.name
    result = handle_controller_action(
        "plan",
        {},
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=out_dir,
        ),
    )

    assert result["action"] == "plan"
    assert result["status"] == "completed"
    assert Path(result["artifacts"]["pipeline_plan"]).exists()
    assert read_json(Path(result["artifacts"]["pipeline_summary"]))["mode"] == "plan"


def test_cockpit_server_preview_action_writes_preview_artifacts(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "server-preview-test" / tmp_path.name
    result = handle_controller_action(
        "preview",
        {},
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=out_dir,
        ),
    )

    assert result["action"] == "preview"
    assert result["status"] == "ready"
    assert Path(result["preview_path"]).exists()
    assert Path(result["plan_path"]).exists()


def test_cockpit_server_run_action_requires_confirmation(tmp_path: Path) -> None:
    with pytest.raises(CockpitServerError, match="confirm_live_run"):
        handle_controller_action(
            "run",
            {},
            CockpitServerConfig(
                sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
                config_path=Path("config/gx10.example.json"),
                out_dir=Path("artifacts") / "server-run-test" / tmp_path.name,
            ),
        )


def test_cockpit_server_report_action_writes_report_artifacts(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "server-report-test" / tmp_path.name

    def pipeline_runner(request):
        return {
            "mode": request.mode,
            "completed_stages": ["plan", "preview", "report"],
            "artifacts": {
                "pipeline_summary": (request.out_dir / "pipeline-summary.json").as_posix(),
                "report_json": (request.out_dir / "report.json").as_posix(),
            },
        }

    result = handle_controller_action(
        "report",
        {},
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=out_dir,
        ),
        pipeline_runner=pipeline_runner,
    )

    assert result["action"] == "report"
    assert result["status"] == "completed"
    assert result["remote_execution"] is False
    assert result["pipeline_summary"]["mode"] == "report"
    assert result["artifacts"]["report_json"].endswith("report.json")


def test_active_cockpit_loads_generated_report_from_out_dir(tmp_path: Path) -> None:
    out_dir = tmp_path / "active-report"
    out_dir.mkdir()
    (out_dir / "report.json").write_text(
        """{
          "source": {"label": "generated-report"},
          "recommendation": {"status": "ready", "objective": "balanced", "candidate_id": "winner"},
          "candidates": {}
        }""",
        encoding="utf-8",
    )

    html = render_active_cockpit(
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=out_dir,
        )
    )

    assert "ready" in html
    assert "winner" in html
    assert "Recommendation detail" in html


def test_cockpit_server_rejects_unknown_action(tmp_path: Path) -> None:
    with pytest.raises(CockpitServerError, match="unsupported controller action"):
        handle_controller_action(
            "dance",
            {},
            CockpitServerConfig(
                sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
                out_dir=Path("artifacts") / "server-unknown-test" / tmp_path.name,
            ),
        )


def test_cockpit_job_store_tracks_completed_action(tmp_path: Path) -> None:
    store = CockpitJobStore()
    job = store.start(
        "plan",
        {},
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=Path("artifacts") / "server-job-test" / tmp_path.name,
        ),
    )
    result = store.wait(job["job_id"], timeout_seconds=5)

    assert result["status"] == "completed"
    assert result["progress_percent"] == 100
    assert result["plain_summary"]["what_happened"] == "I made the plan."
    assert result["plain_summary"]["next_step"] == "Click Preview to check if it is safe."


def test_cockpit_job_store_reports_running_heartbeat() -> None:
    store = CockpitJobStore()

    def never_finishes(_action, _payload, _config):
        import time

        time.sleep(2)
        return {"action": "run", "status": "completed"}

    job = store.start(
        "run",
        {"confirm_live_run": True},
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            config_path=Path("config/gx10.example.json"),
            out_dir=Path("artifacts/server-job-heartbeat-test"),
        ),
        action_runner=never_finishes,
    )
    running = store.get(job["job_id"])

    assert running["status"] == "running"
    assert running["elapsed_seconds"] >= 0
    assert running["progress_percent"] >= 8
    assert "live optimization is running" in running["plain_summary"]["what_happened"].lower()


def test_cockpit_job_store_cancel_marks_running_job() -> None:
    store = CockpitJobStore()

    def never_finishes(_action, _payload, _config):
        import time

        time.sleep(2)
        return {"action": "run", "status": "completed"}

    job = store.start(
        "run",
        {"confirm_live_run": True},
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            config_path=Path("config/gx10.example.json"),
            out_dir=Path("artifacts/server-job-cancel-test"),
        ),
        action_runner=never_finishes,
    )

    cancelled = store.cancel(job["job_id"])

    assert cancelled["status"] == "cancel-requested"
    assert cancelled["cancel_requested"] is True
    assert "Stop requested" in cancelled["plain_summary"]["what_happened"]
