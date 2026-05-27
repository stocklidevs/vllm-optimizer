from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_report_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    baseline = _write_baseline(tmp_path)
    sweep_ranking = _write_ranking(tmp_path, "sweep-ranking.json", "sweep-candidate")
    repeated_ranking = _write_ranking(
        tmp_path,
        "repeated-ranking.json",
        "qwen-top2-repeated-c002-52947e71",
        latency_spread=15.0,
    )
    out = tmp_path / "report.json"
    markdown = tmp_path / "report.md"

    exit_code = main(
        [
            "report",
            "--baseline",
            str(baseline),
            "--sweep-ranking",
            str(sweep_ranking),
            "--repeated-ranking",
            str(repeated_ranking),
            "--out",
            str(out),
            "--markdown-out",
            str(markdown),
        ]
    )

    assert exit_code == 0
    report = read_json(out)
    assert report["recommendation"]["candidate_id"] == "qwen-top2-repeated-c002-52947e71"
    assert "qwen-top2-repeated-c002-52947e71" in markdown.read_text(encoding="utf-8")


def test_report_cli_returns_error_without_ranking(tmp_path: Path) -> None:
    baseline = _write_baseline(tmp_path)
    exit_code = main(
        [
            "report",
            "--baseline",
            str(baseline),
            "--out",
            str(tmp_path / "report.json"),
        ]
    )

    assert exit_code == 2


def _write_baseline(tmp_path: Path) -> Path:
    path = tmp_path / "baseline-summary.json"
    write_json(path, {"aggregate_tokens_per_second": 47.5, "mean_latency_ms": 1000.0})
    return path


def _write_ranking(tmp_path: Path, name: str, candidate_id: str, latency_spread: float | None = None) -> Path:
    path = tmp_path / name
    metrics = {
        "mean_latency_ms": 950.0,
        "aggregate_tokens_per_second": 49.5,
        "failure_rate": 0.0,
    }
    if latency_spread is not None:
        metrics["latency_spread_ms"] = latency_spread
    write_json(
        path,
        {
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": candidate_id,
                        "rank": 1,
                        "score": 0.9,
                        "metrics": metrics,
                    }
                ]
            }
        },
    )
    return path
