from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_saturation_report_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    ranking = tmp_path / "ranking.json"
    write_json(
        ranking,
        {
            "sweep_id": "fixture",
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": "winner",
                        "rank": 1,
                        "metrics": {
                            "mean_latency_ms": 1000.0,
                            "aggregate_tokens_per_second": 80.0,
                            "failure_rate": 0.0,
                            "failure_count": 0,
                            "success_count": 2,
                            "overrides": {"max_num_seqs": 16},
                        },
                    }
                ]
            },
            "candidate_aggregates": [],
        },
    )
    out = tmp_path / "saturation.json"
    markdown = tmp_path / "saturation.md"

    exit_code = main(
        [
            "saturation-report",
            "--ranking",
            f"3={ranking}",
            "--out",
            str(out),
            "--markdown-out",
            str(markdown),
        ]
    )

    assert exit_code == 0
    report = read_json(out)
    assert report["recommendation"]["concurrency"] == 3
    assert "Concurrency Saturation" in markdown.read_text(encoding="utf-8")
