from pathlib import Path

import pytest

from vllm_optimizer.artifacts import write_json
from vllm_optimizer.report import ReportError, ReportInputs, build_comparison_report


def test_build_report_prefers_repeated_balanced_winner(tmp_path: Path) -> None:
    baseline = _write_baseline(tmp_path)
    sweep_ranking = _write_sweep_ranking(tmp_path)
    repeated_ranking = _write_repeated_ranking(tmp_path)

    report = build_comparison_report(
        ReportInputs(
            baseline=baseline,
            sweep_ranking=sweep_ranking,
            repeated_ranking=repeated_ranking,
        )
    )

    recommendation = report["recommendation"]
    assert recommendation["source"] == "repeated"
    assert recommendation["objective"] == "balanced"
    assert recommendation["candidate_id"] == "qwen-top2-repeated-c002-52947e71"
    assert "failure rate" in recommendation["tradeoffs"]
    assert "vLLM Optimization Report" in report["markdown"]


def test_build_report_allows_repeated_only(tmp_path: Path) -> None:
    repeated_ranking = _write_repeated_ranking(tmp_path)

    report = build_comparison_report(
        ReportInputs(
            repeated_ranking=repeated_ranking
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
        build_comparison_report(ReportInputs())


def _write_baseline(tmp_path: Path) -> Path:
    path = tmp_path / "baseline-summary.json"
    write_json(
        path,
        {
            "aggregate_tokens_per_second": 47.5,
            "mean_latency_ms": 1000.0,
            "failure_rate": 0.0,
        },
    )
    return path


def _write_sweep_ranking(tmp_path: Path) -> Path:
    path = tmp_path / "sweep-ranking.json"
    write_json(
        path,
        {
            "sweep_id": "qwen-small-sweep",
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": "qwen-small-c001",
                        "rank": 1,
                        "score": 0.75,
                        "metrics": {
                            "mean_latency_ms": 980.0,
                            "aggregate_tokens_per_second": 48.0,
                            "failure_rate": 0.0,
                        },
                    }
                ]
            },
        },
    )
    return path


def _write_repeated_ranking(tmp_path: Path) -> Path:
    path = tmp_path / "repeated-ranking.json"
    write_json(
        path,
        {
            "sweep_id": "qwen-top2-repeated",
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": "qwen-top2-repeated-c002-52947e71",
                        "rank": 1,
                        "score": 0.91,
                        "metrics": {
                            "mean_latency_ms": 950.0,
                            "aggregate_tokens_per_second": 49.5,
                            "failure_rate": 0.0,
                            "latency_spread_ms": 15.0,
                            "tokens_per_second_spread": 0.4,
                        },
                        "baseline_delta": {
                            "aggregate_tokens_per_second": {
                                "absolute": 2.0,
                                "percent": 4.2,
                            }
                        },
                    }
                ]
            },
        },
    )
    return path
