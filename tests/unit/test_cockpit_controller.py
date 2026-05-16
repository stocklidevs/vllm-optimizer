from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cockpit_controller import (
    CockpitControllerError,
    CockpitPreviewRequest,
    CockpitRunRequest,
    run_cockpit_live,
    run_cockpit_preview,
)


def test_cockpit_preview_generates_plan_and_preview(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "controller-test" / tmp_path.name

    result = run_cockpit_preview(
        CockpitPreviewRequest(
            sweep_path=Path("config/sweeps/qwen-prefix-prefill-tool-json.json"),
            out_dir=out_dir,
        )
    )

    assert result["action"] == "preview"
    assert Path(result["plan_path"]).exists()
    assert Path(result["preview_path"]).exists()
    plan = read_json(Path(result["plan_path"]))
    assert plan["sweep_id"] == "qwen-prefix-prefill-tool-json"


def test_cockpit_preview_preserves_risky_gate(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "controller-risky-test" / tmp_path.name

    result = run_cockpit_preview(
        CockpitPreviewRequest(
            sweep_path=Path("config/sweeps/qwen-kv-cache-memory-tradeoff.json"),
            out_dir=out_dir,
        )
    )

    preview = read_json(Path(result["preview_path"]))
    assert preview["blocked"] is True
    assert result["preview_exit_code"] == 2


def test_cockpit_preview_rejects_output_outside_artifacts(tmp_path: Path) -> None:
    with pytest.raises(CockpitControllerError, match="out_dir must stay under artifacts"):
        run_cockpit_preview(
            CockpitPreviewRequest(
                sweep_path=Path("config/sweeps/qwen-prefix-prefill-tool-json.json"),
                out_dir=tmp_path / "outside",
            )
        )


def test_cockpit_live_run_requires_confirmation(tmp_path: Path) -> None:
    with pytest.raises(CockpitControllerError, match="requires --confirm-live-run"):
        run_cockpit_live(
            CockpitRunRequest(
                sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
                config_path=Path("config/gx10.example.json"),
                out_dir=Path("artifacts") / "live-controller-test" / tmp_path.name,
            )
        )


def test_cockpit_live_run_invokes_pipeline_with_confirmation(tmp_path: Path) -> None:
    calls = []
    out_dir = Path("artifacts") / "live-controller-test" / tmp_path.name

    def pipeline_runner(request):
        calls.append(request)
        return {
            "mode": request.mode,
            "completed_stages": ["plan", "preview", "run"],
            "artifacts": {"pipeline_summary": (request.out_dir / "pipeline-summary.json").as_posix()},
            "promotion": {"automatic": False},
        }

    result = run_cockpit_live(
        CockpitRunRequest(
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            config_path=Path("config/gx10.example.json"),
            out_dir=out_dir,
            confirm_live_run=True,
            pipeline_runner=pipeline_runner,
        )
    )

    assert result["action"] == "run"
    assert result["status"] == "submitted"
    assert result["remote_execution"] is True
    assert result["promotion"] is False
    assert Path(result["result_path"]).exists()
    assert calls[0].mode == "run"
    assert calls[0].sweep_path == Path("config/sweeps/qwen-small-sweep.json")
    assert calls[0].config_path == Path("config/gx10.example.json")
