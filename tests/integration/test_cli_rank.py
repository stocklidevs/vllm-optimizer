from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_rank_writes_report(tmp_path: Path) -> None:
    plan_path = tmp_path / "trial-plan.json"
    report_path = tmp_path / "report.json"
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

    code = main(
        [
            "rank",
            "--plan",
            str(plan_path),
            "--results",
            "tests/fixtures/results/throughput.jsonl",
            "--out",
            str(report_path),
        ]
    )

    assert code == 0
    report = read_json(report_path)
    assert report["ranked_trials"][0]["rank"] == 1
    assert report["artifact_refs"]
