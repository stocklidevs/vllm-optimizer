from pathlib import Path

import pytest

from vllm_optimizer.artifacts import write_json
from vllm_optimizer.saturation_report import (
    SaturationInput,
    SaturationReportError,
    SaturationReportInputs,
    build_saturation_report,
)


def test_saturation_report_recommends_highest_stable_throughput(tmp_path: Path) -> None:
    c2 = _write_ranking(tmp_path, "c2", latency=5200.0, throughput=70.0, failure_rate=0.0)
    c3 = _write_ranking(tmp_path, "c3", latency=6700.0, throughput=96.0, failure_rate=0.0)
    c4 = _write_ranking(tmp_path, "c4", latency=9000.0, throughput=99.0, failure_rate=0.25)

    report = build_saturation_report(
        SaturationReportInputs(
            rankings=(
                SaturationInput(concurrency=2, ranking_path=c2),
                SaturationInput(concurrency=3, ranking_path=c3),
                SaturationInput(concurrency=4, ranking_path=c4),
            )
        )
    )

    assert [level["concurrency"] for level in report["levels"]] == [2, 3, 4]
    assert report["recommendation"]["concurrency"] == 3
    assert report["recommendation"]["candidate_id"] == "c3-winner"
    assert not any("do not yet have rankings" in action for action in report["next_actions"])
    assert "96.000 tokens/sec" in report["markdown"]


def test_saturation_report_requires_rankings() -> None:
    with pytest.raises(SaturationReportError, match="at least one"):
        build_saturation_report(SaturationReportInputs(rankings=()))


def _write_ranking(tmp_path: Path, label: str, latency: float, throughput: float, failure_rate: float) -> Path:
    path = tmp_path / f"{label}.json"
    write_json(
        path,
        {
            "sweep_id": f"{label}-sweep",
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": f"{label}-winner",
                        "rank": 1,
                        "score": throughput,
                        "metrics": {
                            "mean_latency_ms": latency,
                            "aggregate_tokens_per_second": throughput,
                            "failure_count": 1 if failure_rate else 0,
                            "failure_rate": failure_rate,
                            "success_count": 2,
                            "overrides": {
                                "gpu_memory_utilization": 0.92,
                                "max_num_batched_tokens": 4096,
                            },
                        },
                    }
                ]
            },
            "candidate_aggregates": [],
        },
    )
    return path
