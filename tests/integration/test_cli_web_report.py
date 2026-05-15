from pathlib import Path

from vllm_optimizer.artifacts import write_json
from vllm_optimizer.cli import main


def test_report_viewer_cli_writes_html(tmp_path: Path) -> None:
    report = tmp_path / "canonical-report.json"
    html = tmp_path / "viewer.html"
    write_json(report, _canonical_report())

    exit_code = main(["report-viewer", "--report", str(report), "--out", str(html)])

    assert exit_code == 0
    content = html.read_text(encoding="utf-8")
    assert "Canonical vLLM Report" in content
    assert "requires-confirmation" in content
    assert "candidate-a" in content


def test_report_viewer_cli_rejects_missing_report(tmp_path: Path) -> None:
    exit_code = main(["report-viewer", "--report", str(tmp_path / "missing.json"), "--out", str(tmp_path / "viewer.html")])

    assert exit_code == 2


def _canonical_report() -> dict:
    return {
        "schema_version": "1.0",
        "source": {"family": "sweep", "label": "safe sweep", "action_scope": "local-only"},
        "recommendation": {
            "status": "requires-confirmation",
            "candidate_id": "candidate-a",
            "objective": "balanced",
            "summary": "Candidate `candidate-a` leads `balanced` and requires repeated confirmation before promotion.",
            "rationale": ["Throughput: 101.000 tokens/sec."],
            "next_actions": ["Run repeated A/B confirmation before promotion."],
        },
        "objectives": {"balanced": {"winner_candidate_id": "candidate-a", "ranked_candidate_count": 1, "rows": []}},
        "candidates": {
            "candidate-a": {
                "candidate_id": "candidate-a",
                "is_baseline": False,
                "recommendable": True,
                "metrics": {
                    "aggregate_tokens_per_second": 101.0,
                    "mean_latency_ms": 6100.0,
                    "failure_rate": 0.0,
                },
                "objectives": {"balanced": {"rank": 1, "score": 1.0}},
            }
        },
        "chart_datasets": {"candidate_ranking": {"kind": "ranking", "rows": []}},
        "provenance": {"ranking_path": "artifacts/example/ranking.json"},
    }
