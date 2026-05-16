from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cockpit_server import (
    CockpitServerConfig,
    CockpitServerError,
    handle_controller_action,
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
