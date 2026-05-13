from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_benchmark_plan_writes_plan(tmp_path: Path) -> None:
    out = tmp_path / "benchmark-plan.json"

    code = main(
        [
            "benchmark-plan",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--prompts",
            "config/prompts/qwen-baseline.json",
            "--out",
            str(out),
        ]
    )

    assert code == 0
    plan = read_json(out)
    assert plan["prompt_set_id"] == "qwen-baseline-v1"
    assert len(plan["request_sequence"]) == 3


def test_cli_benchmark_run_requires_valid_prompt_set(tmp_path: Path) -> None:
    prompts = tmp_path / "bad.json"
    prompts.write_text('{"prompt_set_id":"bad","cases":[]}', encoding="utf-8")

    code = main(
        [
            "benchmark-run",
            "--config",
            "tests/fixtures/discovery/local.gx10.mock.json",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--prompts",
            str(prompts),
            "--out",
            str(tmp_path / "out"),
        ]
    )

    assert code == 2
