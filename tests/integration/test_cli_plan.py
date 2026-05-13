from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_plan_writes_deterministic_plan(tmp_path: Path) -> None:
    out = tmp_path / "trial-plan.json"

    code = main(
        [
            "plan",
            "--experiment",
            "tests/fixtures/experiments/throughput.json",
            "--out",
            str(out),
        ]
    )

    assert code == 0
    data = read_json(out)
    assert data["experiment_id"] == "demo-throughput"
    assert [trial["trial_id"] for trial in data["trials"]][:2] == [
        "demo-throughput-t001",
        "demo-throughput-t002",
    ]
