from pathlib import Path

import pytest

from vllm_optimizer.artifacts import write_json
from vllm_optimizer.canonical_report import (
    CanonicalReportError,
    CanonicalReportInputs,
    build_canonical_report,
)


def test_canonical_report_keeps_baseline_when_baseline_wins(tmp_path: Path) -> None:
    ranking = _write_ranking(tmp_path, winner_order=0)
    summary = tmp_path / "summary.json"
    write_json(summary, {"trial_count": 4, "success_count": 4, "failure_count": 0})

    report = build_canonical_report(
        CanonicalReportInputs(
            family="session-tuning-sweep",
            label="runtime env",
            ranking_path=ranking,
            summary_path=summary,
            baseline_candidate_order=0,
        )
    )

    assert report["schema_version"] == "1.0"
    assert report["source"]["family"] == "session-tuning-sweep"
    assert report["recommendation"]["status"] == "keep-baseline"
    assert report["recommendation"]["candidate_id"] == "baseline"
    assert "baseline" in report["recommendation"]["summary"].lower()
    assert report["candidates"]["baseline"]["is_baseline"] is True
    assert report["candidates"]["winner"]["is_baseline"] is False
    assert report["chart_datasets"]["candidate_ranking"]["rows"][0]["candidate_id"] == "baseline"
    assert report["provenance"]["summary_path"] == summary.as_posix()
    assert "Keep baseline" in report["markdown"]


def test_canonical_report_requires_confirmation_for_non_baseline_winner(tmp_path: Path) -> None:
    ranking = _write_ranking(tmp_path, winner_order=1)

    report = build_canonical_report(
        CanonicalReportInputs(
            family="sweep",
            label="safe flags",
            ranking_path=ranking,
            baseline_candidate_order=0,
        )
    )

    assert report["recommendation"]["status"] == "requires-confirmation"
    assert report["recommendation"]["candidate_id"] == "winner"
    assert report["candidates"]["failed"]["recommendable"] is False
    assert report["candidates"]["failed"]["exclusion_reason"] == "candidate has failed trials"
    assert report["objectives"]["balanced"]["winner_candidate_id"] == "winner"


def test_canonical_report_requires_rankable_candidates(tmp_path: Path) -> None:
    ranking = tmp_path / "ranking.json"
    write_json(ranking, {"sweep_id": "empty", "objectives": {"balanced": []}, "candidate_aggregates": []})

    with pytest.raises(CanonicalReportError, match="no rankable candidates"):
        build_canonical_report(
            CanonicalReportInputs(
                family="sweep",
                label="empty",
                ranking_path=ranking,
            )
        )


def _write_ranking(tmp_path: Path, winner_order: int) -> Path:
    baseline_tps = 99.0 if winner_order == 0 else 90.0
    winner_tps = 96.0 if winner_order == 0 else 101.0
    balanced_rows = [
        {
            "candidate_id": "baseline" if winner_order == 0 else "winner",
            "rank": 1,
            "score": 1.0,
            "metrics": {
                "aggregate_tokens_per_second": baseline_tps if winner_order == 0 else winner_tps,
                "mean_latency_ms": 6500.0 if winner_order == 0 else 6100.0,
                "failure_count": 0,
                "failure_rate": 0.0,
                "success_count": 2,
                "tokens_per_second_spread": 0.2,
                "latency_spread_ms": 20.0,
            },
            "artifact_paths": {"summary": "winner-summary.json"},
        },
        {
            "candidate_id": "winner" if winner_order == 0 else "baseline",
            "rank": 2,
            "score": 0.8,
            "metrics": {
                "aggregate_tokens_per_second": winner_tps if winner_order == 0 else baseline_tps,
                "mean_latency_ms": 6600.0 if winner_order == 0 else 6700.0,
                "failure_count": 0,
                "failure_rate": 0.0,
                "success_count": 2,
            },
            "artifact_paths": {"summary": "runner-up-summary.json"},
        },
    ]
    path = tmp_path / "ranking.json"
    write_json(
        path,
        {
            "sweep_id": "fixture-sweep",
            "objectives": {"balanced": balanced_rows, "throughput": balanced_rows},
            "candidate_aggregates": [
                {
                    "candidate_id": "baseline",
                    "order": 0,
                    "mean_latency_ms": 6500.0 if winner_order == 0 else 6700.0,
                    "mean_tokens_per_second": baseline_tps,
                    "failure_count": 0,
                    "failure_rate": 0.0,
                    "success_count": 2,
                    "source_trials": [],
                },
                {
                    "candidate_id": "winner",
                    "order": 1,
                    "mean_latency_ms": 6600.0 if winner_order == 0 else 6100.0,
                    "mean_tokens_per_second": winner_tps,
                    "failure_count": 0,
                    "failure_rate": 0.0,
                    "success_count": 2,
                    "source_trials": [],
                },
                {
                    "candidate_id": "failed",
                    "order": 2,
                    "failure_count": 2,
                    "failure_rate": 1.0,
                    "success_count": 0,
                    "source_trials": [{"failure_reason": "benchmark failure"}],
                },
            ],
        },
    )
    return path
