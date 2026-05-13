from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_smoke_serve_plan_writes_plan(tmp_path: Path) -> None:
    out = tmp_path / "smoke-plan.json"

    code = main(
        [
            "smoke-serve-plan",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--out",
            str(out),
        ]
    )

    assert code == 0
    plan = read_json(out)
    assert plan["mode"] == "dry-run"
    assert plan["readiness"]["url"] == "http://127.0.0.1:8001/v1/models"
