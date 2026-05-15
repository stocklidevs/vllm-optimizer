from pathlib import Path

import pytest

from vllm_optimizer.artifacts import write_json
from vllm_optimizer.web_report import WebReportError, render_web_report, write_web_report


def test_render_web_report_shows_recommendation_candidates_and_provenance() -> None:
    html = render_web_report(_canonical_report())

    assert "Canonical vLLM Report" in html
    assert "keep-baseline" in html
    assert "Keep baseline" in html
    assert "baseline-candidate" in html
    assert "challenger-candidate" in html
    assert "99.100" in html
    assert "ranking.json" in html
    assert "Metric map" in html


def test_write_web_report_is_deterministic(tmp_path: Path) -> None:
    report_path = tmp_path / "canonical.json"
    first = tmp_path / "first.html"
    second = tmp_path / "second.html"
    write_json(report_path, _canonical_report())

    write_web_report(report_path, first)
    write_web_report(report_path, second)

    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")


def test_render_web_report_requires_canonical_sections() -> None:
    with pytest.raises(WebReportError, match="missing canonical report section"):
        render_web_report({"schema_version": "1.0"})


def _canonical_report() -> dict:
    return {
        "schema_version": "1.0",
        "source": {"family": "session-tuning-sweep", "label": "runtime env", "action_scope": "local-only"},
        "recommendation": {
            "status": "keep-baseline",
            "candidate_id": "baseline-candidate",
            "objective": "balanced",
            "summary": "Keep baseline `baseline-candidate` for `balanced`.",
            "rationale": [
                "Throughput: 99.100 tokens/sec.",
                "Top ranked candidate is the configured baseline/current behavior.",
            ],
            "next_actions": ["Do not promote a tuned profile from this report."],
        },
        "objectives": {
            "balanced": {
                "winner_candidate_id": "baseline-candidate",
                "ranked_candidate_count": 2,
                "rows": [
                    {"candidate_id": "baseline-candidate", "rank": 1, "score": 1.0},
                    {"candidate_id": "challenger-candidate", "rank": 2, "score": 0.8},
                ],
            }
        },
        "candidates": {
            "baseline-candidate": {
                "candidate_id": "baseline-candidate",
                "is_baseline": True,
                "recommendable": True,
                "metrics": {
                    "aggregate_tokens_per_second": 99.1,
                    "mean_latency_ms": 6531.0,
                    "failure_rate": 0.0,
                    "tokens_per_second_spread": 0.2,
                    "latency_spread_ms": 23.8,
                },
                "objectives": {"balanced": {"rank": 1, "score": 1.0}},
            },
            "challenger-candidate": {
                "candidate_id": "challenger-candidate",
                "is_baseline": False,
                "recommendable": True,
                "metrics": {
                    "aggregate_tokens_per_second": 98.5,
                    "mean_latency_ms": 6587.0,
                    "failure_rate": 0.0,
                },
                "objectives": {"balanced": {"rank": 2, "score": 0.8}},
            },
        },
        "chart_datasets": {
            "candidate_ranking": {
                "kind": "ranking",
                "rows": [
                    {
                        "objective": "balanced",
                        "candidate_id": "baseline-candidate",
                        "rank": 1,
                        "score": 1.0,
                        "tokens_per_second": 99.1,
                        "mean_latency_ms": 6531.0,
                    }
                ],
            }
        },
        "provenance": {"ranking_path": "artifacts/example/ranking.json"},
    }
