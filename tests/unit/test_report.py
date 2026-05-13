from pathlib import Path

import pytest

from vllm_optimizer.report import ReportError, ReportInputs, build_comparison_report


def test_build_report_prefers_repeated_balanced_winner() -> None:
    report = build_comparison_report(
        ReportInputs(
            baseline=Path("artifacts/benchmarks/qwen-baseline/summary.json"),
            sweep_ranking=Path("artifacts/sweeps/qwen-small/live/ranking.json"),
            repeated_ranking=Path("artifacts/sweeps/qwen-top2-repeated/live/ranking.json"),
        )
    )

    recommendation = report["recommendation"]
    assert recommendation["source"] == "repeated"
    assert recommendation["objective"] == "balanced"
    assert recommendation["candidate_id"] == "qwen-top2-repeated-c002-52947e71"
    assert "failure rate" in recommendation["tradeoffs"]
    assert "vLLM Optimization Report" in report["markdown"]


def test_build_report_allows_repeated_only() -> None:
    report = build_comparison_report(
        ReportInputs(
            repeated_ranking=Path("artifacts/sweeps/qwen-top2-repeated/live/ranking.json")
        )
    )

    assert report["recommendation"]["candidate_id"] == "qwen-top2-repeated-c002-52947e71"
    assert "baseline" in report["inputs"]["missing"]
    assert any("Baseline summary" in note for note in report["notes"])


def test_build_report_requires_ranking_input() -> None:
    with pytest.raises(ReportError, match="ranking input"):
        build_comparison_report(ReportInputs(baseline=Path("artifacts/benchmarks/qwen-baseline/summary.json")))
