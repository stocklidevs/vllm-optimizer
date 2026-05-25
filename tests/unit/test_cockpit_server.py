from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json, write_json
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


def test_cockpit_server_promote_requires_promotion_gate(tmp_path: Path) -> None:
    with pytest.raises(CockpitServerError, match="allow_promotion"):
        handle_controller_action(
            "promote",
            {"candidate_id": "candidate-2", "objective": "balanced"},
            CockpitServerConfig(
                sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
                out_dir=tmp_path / "promote-gated",
            ),
        )


def test_cockpit_server_promote_writes_selected_candidate_profile(tmp_path: Path) -> None:
    out_dir = tmp_path / "promote-enabled"
    _write_promotable_ranking(out_dir)

    result = handle_controller_action(
        "promote",
        {"candidate_id": "candidate-2", "objective": "balanced"},
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=out_dir,
            allow_promotion=True,
        ),
    )

    assert result["action"] == "promote"
    assert result["status"] == "completed"
    assert result["promotion"] is True
    assert result["candidate_id"] == "candidate-2"
    profile = read_json(Path(result["artifacts"]["profile_json"]))
    assert profile["promotion"]["candidate_id"] == "candidate-2"
    assert Path(result["artifacts"]["summary_markdown"]).exists()


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


def test_active_cockpit_hides_stale_report_from_different_sweep(tmp_path: Path) -> None:
    out_dir = tmp_path / "active-stale-report"
    out_dir.mkdir()
    (out_dir / "sweep-plan.json").write_text(
        """{"sweep_id":"qwen-small-sweep","trials":[]}""",
        encoding="utf-8",
    )
    (out_dir / "report.json").write_text(
        """{
          "recommendation": {"status": "ready", "objective": "balanced", "candidate_id": "qwen-small-sweep-c001"},
          "candidates": [{"candidate_id": "qwen-small-sweep-c001", "metrics": {"aggregate_tokens_per_second": 50}}]
        }""",
        encoding="utf-8",
    )

    html = render_active_cockpit(
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-concurrency-saturation-c8.json"),
            out_dir=out_dir,
        )
    )

    assert "qwen-small-sweep-c001" not in html
    assert "Start Optimization" in html
    assert "no report" in html


def test_active_cockpit_hides_mixed_report_from_different_sweep(tmp_path: Path) -> None:
    out_dir = tmp_path / "active-mixed-report"
    out_dir.mkdir()
    (out_dir / "sweep-plan.json").write_text(
        """{"sweep_id":"qwen-concurrency-saturation-c8","trials":[]}""",
        encoding="utf-8",
    )
    (out_dir / "report.json").write_text(
        """{
          "recommendation": {"status": "ready", "objective": "balanced", "candidate_id": "qwen-concurrency-saturation-c8-c001"},
          "candidates": [
            {"candidate_id": "qwen-concurrency-saturation-c8-c001", "metrics": {"aggregate_tokens_per_second": 98}},
            {"candidate_id": "qwen-small-sweep-c001", "metrics": {"aggregate_tokens_per_second": 50}}
          ]
        }""",
        encoding="utf-8",
    )

    html = render_active_cockpit(
        CockpitServerConfig(
            sweep_path=Path("config/sweeps/qwen-concurrency-saturation-c8.json"),
            out_dir=out_dir,
        )
    )

    assert "qwen-small-sweep-c001" not in html
    assert "Start Optimization" in html
    assert "no report" in html


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


def _write_promotable_ranking(out_dir: Path) -> Path:
    live_dir = out_dir / "live"
    live_dir.mkdir(parents=True, exist_ok=True)
    plan_path = live_dir / "trial-plan.json"
    write_json(
        plan_path,
        {
            "serve_plan": {
                "serve_command": [
                    "vllm",
                    "serve",
                    "cyankiwi/Qwen3-Coder-Next-AWQ-4bit",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8001",
                    "--served-model-name",
                    "Qwen3-Coder-Next",
                    "--max-model-len",
                    "32768",
                    "--gpu-memory-utilization",
                    "0.90",
                    "--enable-auto-tool-choice",
                    "--tool-call-parser",
                    "qwen3_coder",
                    "--performance-mode",
                    "interactivity",
                ]
            }
        },
    )
    ranking_path = live_dir / "ranking.json"
    write_json(
        ranking_path,
        {
            "sweep_id": "server-promotion",
            "objectives": {
                "balanced": [
                    {"candidate_id": "candidate-1", "rank": 1, "metrics": {"aggregate_tokens_per_second": 48.0}},
                    {"candidate_id": "candidate-2", "rank": 2, "metrics": {"aggregate_tokens_per_second": 96.0}},
                ]
            },
            "candidate_aggregates": [
                {
                    "candidate_id": "candidate-1",
                    "success_count": 1,
                    "source_trials": [
                        {"trial_id": "trial-1", "status": "completed", "artifact_paths": {"plan": str(plan_path)}}
                    ],
                },
                {
                    "candidate_id": "candidate-2",
                    "success_count": 1,
                    "overrides": {"gpu_memory_utilization": 0.86, "max_model_len": 32768},
                    "source_trials": [
                        {"trial_id": "trial-2", "status": "completed", "artifact_paths": {"plan": str(plan_path)}}
                    ],
                },
            ],
        },
    )
    return ranking_path
