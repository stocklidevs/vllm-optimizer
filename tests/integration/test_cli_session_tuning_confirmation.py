from pathlib import Path

from vllm_optimizer.cli import main


def test_session_tuning_confirm_requires_approval(tmp_path: Path) -> None:
    exit_code = main(
        [
            "session-tuning-confirm",
            "--config",
            "config/gx10.example.json",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--prompts",
            "config/prompts/qwen-baseline.json",
            "--session-tuning",
            "config/session-tuning/qwen-runtime-env.json",
            "--out",
            str(tmp_path),
        ]
    )

    assert exit_code == 2
