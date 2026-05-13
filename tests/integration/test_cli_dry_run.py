from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_dry_run_writes_preview(tmp_path: Path) -> None:
    plan_path = tmp_path / "trial-plan.json"
    preview_path = tmp_path / "dry-run.json"
    assert (
        main(
            [
                "plan",
                "--experiment",
                "tests/fixtures/experiments/throughput.json",
                "--out",
                str(plan_path),
            ]
        )
        == 0
    )

    code = main(["dry-run", "--plan", str(plan_path), "--out", str(preview_path)])

    assert code == 0
    preview = read_json(preview_path)
    assert preview["blocked_action_count"] == 0
    assert any(action["kind"] == "probe-gpu" for action in preview["actions"])
