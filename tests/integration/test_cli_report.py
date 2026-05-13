from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_report_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    markdown = tmp_path / "report.md"

    exit_code = main(
        [
            "report",
            "--baseline",
            "artifacts/benchmarks/qwen-baseline/summary.json",
            "--sweep-ranking",
            "artifacts/sweeps/qwen-small/live/ranking.json",
            "--repeated-ranking",
            "artifacts/sweeps/qwen-top2-repeated/live/ranking.json",
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
    exit_code = main(
        [
            "report",
            "--baseline",
            "artifacts/benchmarks/qwen-baseline/summary.json",
            "--out",
            str(tmp_path / "report.json"),
        ]
    )

    assert exit_code == 2
