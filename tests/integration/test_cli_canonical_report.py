from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_canonical_report_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    ranking = tmp_path / "ranking.json"
    out = tmp_path / "canonical-report.json"
    markdown = tmp_path / "report.md"
    write_json(
        ranking,
        {
            "sweep_id": "fixture",
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": "baseline",
                        "rank": 1,
                        "score": 1.0,
                        "metrics": {
                            "aggregate_tokens_per_second": 99.1,
                            "mean_latency_ms": 6531.0,
                            "failure_count": 0,
                            "failure_rate": 0.0,
                            "success_count": 2,
                        },
                    }
                ]
            },
            "candidate_aggregates": [
                {
                    "candidate_id": "baseline",
                    "order": 0,
                    "mean_tokens_per_second": 99.1,
                    "mean_latency_ms": 6531.0,
                    "failure_count": 0,
                    "failure_rate": 0.0,
                    "success_count": 2,
                }
            ],
        },
    )

    exit_code = main(
        [
            "canonical-report",
            "--family",
            "session-tuning-sweep",
            "--label",
            "fixture report",
            "--ranking",
            str(ranking),
            "--out",
            str(out),
            "--markdown-out",
            str(markdown),
        ]
    )

    assert exit_code == 0
    report = read_json(out)
    assert report["recommendation"]["status"] == "keep-baseline"
    assert report["chart_datasets"]["candidate_ranking"]["kind"] == "ranking"
    assert "Canonical vLLM Optimization Report" in markdown.read_text(encoding="utf-8")


def test_canonical_report_cli_rejects_missing_ranking(tmp_path: Path) -> None:
    exit_code = main(
        [
            "canonical-report",
            "--family",
            "sweep",
            "--label",
            "missing",
            "--ranking",
            str(tmp_path / "missing.json"),
            "--out",
            str(tmp_path / "report.json"),
        ]
    )

    assert exit_code == 2
