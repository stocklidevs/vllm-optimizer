from pathlib import Path

import pytest

from vllm_optimizer.artifacts import write_json
from vllm_optimizer.workload_report import (
    WorkloadInput,
    WorkloadReportError,
    WorkloadReportInputs,
    build_workload_leaderboard_report,
)


def test_workload_report_summarizes_winners_and_failures(tmp_path: Path) -> None:
    ranking = _write_ranking(tmp_path)
    profile = _write_profile(tmp_path)

    report = build_workload_leaderboard_report(
        WorkloadReportInputs(
            workloads=(
                WorkloadInput(
                    label="concurrent interactive",
                    ranking_path=ranking,
                    promoted_profile_path=profile,
                ),
            )
        )
    )

    workload = report["workloads"][0]
    assert workload["winner"]["candidate_id"] == "winner"
    assert workload["recommendation"]["status"] == "promoted"
    assert workload["baseline_delta"]["mean_latency_ms"]["percent"] == pytest.approx(-10.0)
    assert report["promoted_profiles"][0]["profile_id"] == "concurrent-profile"
    assert "ninja" in report["failed_candidate_findings"][0]["failure_summary"]
    assert any("ninja" in action for action in report["next_actions"])
    assert "Workload Leaderboard" in report["markdown"]


def test_workload_report_requires_workloads() -> None:
    with pytest.raises(WorkloadReportError, match="at least one"):
        build_workload_leaderboard_report(WorkloadReportInputs(workloads=()))


def test_workload_report_classifies_unsupported_fp8_e5m2(tmp_path: Path) -> None:
    ranking = _write_ranking(tmp_path)
    log = tmp_path / "server-log.json"
    write_json(log, {"log": "ValueError: fp8_e5m2 kv-cache is not supported with fp8 checkpoints."})

    report = build_workload_leaderboard_report(
        WorkloadReportInputs(workloads=(WorkloadInput(label="fp8", ranking_path=ranking),))
    )

    summary = report["failed_candidate_findings"][0]["failure_summary"]
    assert "fp8_e5m2" in summary
    assert "unsupported" in summary


def _write_ranking(tmp_path: Path) -> Path:
    log = tmp_path / "server-log.json"
    write_json(log, {"log": "FileNotFoundError: [Errno 2] No such file or directory: 'ninja'"})
    path = tmp_path / "ranking.json"
    write_json(
        path,
        {
            "sweep_id": "fixture-sweep",
            "ranked_candidate_count": 1,
            "source_trial_count": 4,
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": "winner",
                        "rank": 1,
                        "score": 1.0,
                        "metrics": {
                            "mean_latency_ms": 900.0,
                            "aggregate_tokens_per_second": 55.0,
                            "failure_count": 0,
                            "failure_rate": 0.0,
                            "success_count": 2,
                            "overrides": {"gpu_memory_utilization": 0.92},
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
                    "success_count": 2,
                    "overrides": {"gpu_memory_utilization": 0.9},
                    "source_trials": [],
                },
                {
                    "candidate_id": "winner",
                    "order": 1,
                    "mean_latency_ms": 900.0,
                    "mean_tokens_per_second": 55.0,
                    "failure_count": 0,
                    "failure_rate": 0.0,
                    "success_count": 2,
                    "overrides": {"gpu_memory_utilization": 0.92},
                    "source_trials": [],
                },
                {
                    "candidate_id": "fp8-failure",
                    "order": 2,
                    "mean_latency_ms": None,
                    "mean_tokens_per_second": None,
                    "failure_count": 2,
                    "failure_rate": 1.0,
                    "success_count": 0,
                    "overrides": {"kv_cache_dtype": "fp8"},
                    "source_trials": [{"failure_reason": "benchmark failure", "artifact_paths": {"server_log": str(log)}}],
                },
            ],
        },
    )
    return path


def _write_profile(tmp_path: Path) -> Path:
    path = tmp_path / "profile.json"
    write_json(
        path,
        {
            "profile_id": "concurrent-profile",
            "gpu_memory_utilization": 0.92,
            "performance_mode": "interactivity",
            "optional_flags": {"block_size": 16},
            "promotion": {"candidate_id": "winner", "confirmation": {"decision": {"status": "switch-to-recommended"}}},
        },
    )
    return path
