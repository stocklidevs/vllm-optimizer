from pathlib import Path

import pytest

from vllm_optimizer.ab_confirmation import (
    AbConfirmationError,
    AbConfirmationInputs,
    build_ab_confirmation_report,
    decide_ab_default,
)
from vllm_optimizer.artifacts import write_json


def test_ab_report_switches_to_recommended_when_better(tmp_path: Path) -> None:
    original = _write_summaries(tmp_path, "original", [1000, 1010, 990], [45, 46, 45])
    recommended = _write_summaries(tmp_path, "recommended", [950, 960, 940], [49, 50, 49])

    report = build_ab_confirmation_report(
        AbConfirmationInputs(
            original_label="original",
            recommended_label="recommended",
            original_summaries=tuple(original),
            recommended_summaries=tuple(recommended),
            prompt_set_id="qwen-baseline-v1",
        )
    )

    assert report["decision"]["status"] == "switch-to-recommended"
    assert report["aggregates"]["recommended"]["repetition_count"] == 3
    assert report["aggregates"]["original"]["failure_rate"] == 0
    assert report["deltas"]["mean_latency_ms"]["recommended_better"] is True
    assert "A/B Benchmark Confirmation" in report["markdown"]


def test_ab_report_keeps_original_when_recommended_fails(tmp_path: Path) -> None:
    original = _write_summaries(tmp_path, "original", [1000, 1000, 1000], [48, 48, 48])
    recommended = _write_summaries(tmp_path, "recommended", [950, 950, 950], [50, 50, 50], failures=[0, 1, 0])

    report = build_ab_confirmation_report(
        AbConfirmationInputs(
            original_label="original",
            recommended_label="recommended",
            original_summaries=tuple(original),
            recommended_summaries=tuple(recommended),
            prompt_set_id="qwen-baseline-v1",
        )
    )

    assert report["decision"]["status"] == "keep-original"
    assert "failure rate" in report["decision"]["reason"]


def test_ab_report_is_inconclusive_inside_noise_band(tmp_path: Path) -> None:
    original = _write_summaries(tmp_path, "original", [1000, 1000, 1000], [48, 48, 48])
    recommended = _write_summaries(tmp_path, "recommended", [1005, 1005, 1005], [47.8, 47.8, 47.8])

    report = build_ab_confirmation_report(
        AbConfirmationInputs(
            original_label="original",
            recommended_label="recommended",
            original_summaries=tuple(original),
            recommended_summaries=tuple(recommended),
            prompt_set_id="qwen-baseline-v1",
        )
    )

    assert report["decision"]["status"] == "inconclusive"


def test_ab_report_rejects_malformed_summary(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    write_json(bad, {"success_count": 3, "failure_count": 0, "mean_latency_ms": 1000})
    good = _write_summaries(tmp_path, "recommended", [1000], [48])

    with pytest.raises(AbConfirmationError, match="aggregate_tokens_per_second"):
        build_ab_confirmation_report(
            AbConfirmationInputs(
                original_label="original",
                recommended_label="recommended",
                original_summaries=(bad,),
                recommended_summaries=tuple(good),
                prompt_set_id="qwen-baseline-v1",
            )
        )


def test_decide_ab_default_keeps_original_when_original_better() -> None:
    decision = decide_ab_default(
        {"failure_rate": 0},
        {"failure_rate": 0},
        {
            "mean_latency_ms": {"original_better": True, "recommended_better": False},
            "mean_tokens_per_second": {"original_better": True, "recommended_better": False},
        },
    )

    assert decision["status"] == "keep-original"


def _write_summaries(
    tmp_path: Path,
    label: str,
    latencies: list[float],
    throughputs: list[float],
    failures: list[int] | None = None,
) -> list[Path]:
    failures = failures or [0 for _ in latencies]
    paths = []
    for index, (latency, throughput, failure_count) in enumerate(zip(latencies, throughputs, failures, strict=True), start=1):
        path = tmp_path / f"{label}-{index}.json"
        write_json(
            path,
            {
                "success_count": 3 - failure_count,
                "failure_count": failure_count,
                "mean_latency_ms": latency,
                "total_tokens": 145,
                "aggregate_tokens_per_second": throughput,
            },
        )
        paths.append(path)
    return paths
