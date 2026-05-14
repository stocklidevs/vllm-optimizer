from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_workload_report_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    ranking = tmp_path / "ranking.json"
    write_json(
        ranking,
        {
            "sweep_id": "fixture",
            "ranked_candidate_count": 1,
            "source_trial_count": 2,
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": "winner",
                        "rank": 1,
                        "metrics": {
                            "mean_latency_ms": 950.0,
                            "aggregate_tokens_per_second": 51.0,
                            "failure_count": 0,
                            "failure_rate": 0.0,
                            "overrides": {},
                        },
                    }
                ]
            },
            "candidate_aggregates": [
                {
                    "candidate_id": "baseline",
                    "order": 0,
                    "mean_latency_ms": 1000.0,
                    "mean_tokens_per_second": 50.0,
                    "failure_count": 0,
                    "failure_rate": 0.0,
                    "overrides": {},
                }
            ],
        },
    )
    out = tmp_path / "leaderboard.json"
    markdown = tmp_path / "leaderboard.md"

    exit_code = main(
        [
            "workload-report",
            "--workload",
            f"interactive={ranking}",
            "--out",
            str(out),
            "--markdown-out",
            str(markdown),
        ]
    )

    assert exit_code == 0
    report = read_json(out)
    assert report["workloads"][0]["label"] == "interactive"
    assert "winner" in markdown.read_text(encoding="utf-8")
