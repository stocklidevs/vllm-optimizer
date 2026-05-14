from pathlib import Path

import pytest

from vllm_optimizer.artifacts import write_json
from vllm_optimizer.default_report import (
    DefaultReportError,
    DefaultReportInputs,
    build_default_decision_report,
    decide_default_status,
    metric_delta,
)


def test_metric_delta_marks_lower_latency_as_improved() -> None:
    delta = metric_delta(1000, 950, lower_is_better=True)

    assert delta["absolute"] == -50
    assert delta["percent"] == -5
    assert delta["improved"] is True


def test_default_report_keeps_profile_when_not_worse(tmp_path: Path) -> None:
    paths = _write_default_report_fixture(tmp_path, recommended_latency=990, recommended_tps=49)

    report = build_default_decision_report(
        DefaultReportInputs(
            baseline=paths["baseline"],
            recommended=paths["recommended"],
            profile=paths["profile"],
            source_ranking=paths["ranking"],
        )
    )

    assert report["decision"]["status"] == "keep"
    assert report["deltas"]["mean_latency_ms"]["improved"] is True
    assert report["deltas"]["aggregate_tokens_per_second"]["improved"] is True
    assert report["provenance"]["candidate_id"] == "candidate-1"
    assert report["provenance"]["source_rank"]["objective"] == "balanced"
    assert "Recommended Profile Default Decision" in report["markdown"]


def test_default_report_rejects_profile_worse_on_both_metrics(tmp_path: Path) -> None:
    paths = _write_default_report_fixture(tmp_path, recommended_latency=1200, recommended_tps=40)

    report = build_default_decision_report(
        DefaultReportInputs(
            baseline=paths["baseline"],
            recommended=paths["recommended"],
            profile=paths["profile"],
        )
    )

    assert report["decision"]["status"] == "reject"
    assert "worse" in report["decision"]["reason"]


def test_default_report_is_inconclusive_inside_noise_band(tmp_path: Path) -> None:
    paths = _write_default_report_fixture(tmp_path, recommended_latency=1007, recommended_tps=47.7)

    report = build_default_decision_report(
        DefaultReportInputs(
            baseline=paths["baseline"],
            recommended=paths["recommended"],
            profile=paths["profile"],
        )
    )

    assert report["decision"]["status"] == "inconclusive"
    assert report["deltas"]["mean_latency_ms"]["materially_worse"] is False
    assert report["deltas"]["aggregate_tokens_per_second"]["materially_worse"] is False


def test_default_report_returns_inconclusive_for_mixed_metrics() -> None:
    decision = decide_default_status(
        {"success_count": 3, "failure_count": 0},
        {
            "mean_latency_ms": {"improved": True},
            "aggregate_tokens_per_second": {"improved": False},
        },
    )

    assert decision["status"] == "inconclusive"


def test_default_report_rejects_missing_metric(tmp_path: Path) -> None:
    paths = _write_default_report_fixture(tmp_path, recommended_latency=990, recommended_tps=49)
    write_json(paths["recommended"], {"success_count": 3, "failure_count": 0})

    with pytest.raises(DefaultReportError, match="recommended.mean_latency_ms"):
        build_default_decision_report(
            DefaultReportInputs(
                baseline=paths["baseline"],
                recommended=paths["recommended"],
                profile=paths["profile"],
            )
        )


def _write_default_report_fixture(tmp_path: Path, recommended_latency: float, recommended_tps: float) -> dict[str, Path]:
    baseline = tmp_path / "baseline.json"
    recommended = tmp_path / "recommended.json"
    profile = tmp_path / "profile.json"
    ranking = tmp_path / "ranking.json"
    write_json(
        baseline,
        {
            "success_count": 3,
            "failure_count": 0,
            "mean_latency_ms": 1000,
            "total_tokens": 145,
            "aggregate_tokens_per_second": 48,
        },
    )
    write_json(
        recommended,
        {
            "success_count": 3,
            "failure_count": 0,
            "mean_latency_ms": recommended_latency,
            "total_tokens": 145,
            "aggregate_tokens_per_second": recommended_tps,
        },
    )
    write_json(
        profile,
        {
            "profile_id": "recommended",
            "vllm_executable": "vllm",
            "model": "model",
            "served_model_name": "model",
            "host": "0.0.0.0",
            "port": 8001,
            "max_model_len": 32768,
            "gpu_memory_utilization": 0.9,
            "enable_auto_tool_choice": True,
            "tool_call_parser": "qwen3_coder",
            "performance_mode": "interactivity",
            "optional_flags": {"enable_chunked_prefill": True, "max_num_batched_tokens": 4096},
            "promotion": {
                "candidate_id": "candidate-1",
                "sweep_id": "sweep-1",
                "objective": "balanced",
                "ranking_path": "artifacts/ranking.json",
                "source_trial_ids": ["trial-1", "trial-2"],
            },
        },
    )
    write_json(
        ranking,
        {
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": "candidate-1",
                        "rank": 1,
                        "metrics": {"mean_latency_ms": recommended_latency},
                    }
                ]
            }
        },
    )
    return {"baseline": baseline, "recommended": recommended, "profile": profile, "ranking": ranking}
