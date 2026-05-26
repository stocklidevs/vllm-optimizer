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


def test_build_report_prefers_single_user_responsiveness_when_present(tmp_path: Path) -> None:
    ranking = tmp_path / "single-user-ranking.json"
    ranking.write_text(
        """{
  "sweep_id": "single-user-report",
  "objectives": {
    "single_user": [
      {
        "candidate_id": "responsive-candidate",
        "rank": 1,
        "score": 700,
        "metrics": {"mean_latency_ms": 700, "aggregate_tokens_per_second": 50, "failure_rate": 0}
      }
    ],
    "throughput": [
      {
        "candidate_id": "aggregate-candidate",
        "rank": 1,
        "score": 90,
        "metrics": {"mean_latency_ms": 1200, "aggregate_tokens_per_second": 90, "failure_rate": 0}
      }
    ]
  }
}""",
        encoding="utf-8",
    )

    report = build_comparison_report(ReportInputs(sweep_ranking=ranking))

    assert report["recommendation"]["objective"] == "single_user"
    assert report["recommendation"]["candidate_id"] == "responsive-candidate"


def test_build_report_requires_ranking_input() -> None:
    with pytest.raises(ReportError, match="ranking input"):
        build_comparison_report(ReportInputs(baseline=Path("artifacts/benchmarks/qwen-baseline/summary.json")))
