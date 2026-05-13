from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_serve_plan_writes_dry_run_command(tmp_path: Path) -> None:
    out = tmp_path / "serve-plan.json"

    code = main(
        [
            "serve-plan",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--out",
            str(out),
        ]
    )

    assert code == 0
    plan = read_json(out)
    assert plan["will_execute"] is False
    assert plan["command"][:3] == [
        "$HOME/qwen3next-venv/bin/vllm",
        "serve",
        "cyankiwi/Qwen3-Coder-Next-AWQ-4bit",
    ]
