from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_session_tuning_sweep_plan_and_preview_cli(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    preview_path = tmp_path / "preview.json"

    plan_exit = main(
        [
            "session-tuning-sweep-plan",
            "--sweep",
            "config/session-tuning-sweeps/qwen-runtime-env-sweep.json",
            "--out",
            str(plan_path),
        ]
    )
    preview_exit = main(
        [
            "session-tuning-sweep-preview",
            "--plan",
            str(plan_path),
            "--out",
            str(preview_path),
        ]
    )

    assert plan_exit == 0
    assert preview_exit == 0
    plan = read_json(plan_path)
    preview = read_json(preview_path)
    assert plan["sweep_id"] == "qwen-runtime-env-session-sweep"
    assert preview["blocked"] is False
