from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_session_tuning_preview_cli_writes_preview(tmp_path: Path) -> None:
    out = tmp_path / "preview.json"

    exit_code = main(
        [
            "session-tuning-preview",
            "--profile",
            "config/session-tuning/qwen-runtime-env.json",
            "--catalog",
            "artifacts/system-tuning/gx10-live/catalog.json",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    preview = read_json(out)
    assert preview["profile_id"] == "qwen-runtime-env-v1"
    assert preview["actions"][0]["classification"] == "session-mutating"


def test_benchmark_plan_session_tuning_requires_allow_flag(tmp_path: Path) -> None:
    exit_code = main(
        [
            "benchmark-plan",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--prompts",
            "config/prompts/qwen-baseline.json",
            "--session-tuning",
            "config/session-tuning/qwen-runtime-env.json",
            "--out",
            str(tmp_path / "plan.json"),
        ]
    )

    assert exit_code == 2


def test_benchmark_plan_records_session_tuning_when_allowed(tmp_path: Path) -> None:
    out = tmp_path / "plan.json"

    exit_code = main(
        [
            "benchmark-plan",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--prompts",
            "config/prompts/qwen-baseline.json",
            "--session-tuning",
            "config/session-tuning/qwen-runtime-env.json",
            "--allow-session-tuning",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    plan = read_json(out)
    assert plan["session_tuning"]["profile_id"] == "qwen-runtime-env-v1"
    assert "ulimit -n 500000" in plan["session_tuning"]["prelude"]
