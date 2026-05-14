from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_recommended_profile_benchmark_plan_cli(tmp_path: Path) -> None:
    out = tmp_path / "plan.json"

    exit_code = main(
        [
            "benchmark-plan",
            "--profile",
            "config/profiles/qwen3-coder-next-awq-recommended.json",
            "--prompts",
            "config/prompts/qwen-baseline.json",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    plan = read_json(out)
    assert plan["profile_id"] == "qwen3-coder-next-awq-recommended"
    assert plan["prompt_set_id"] == "qwen-baseline-v1"
    assert "tokens_per_second" in plan["metrics"]


def test_recommended_report_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    paths = _write_report_fixture(tmp_path)
    out = tmp_path / "report.json"
    markdown = tmp_path / "report.md"

    exit_code = main(
        [
            "recommended-report",
            "--baseline",
            str(paths["baseline"]),
            "--recommended",
            str(paths["recommended"]),
            "--profile",
            str(paths["profile"]),
            "--source-ranking",
            str(paths["ranking"]),
            "--out",
            str(out),
            "--markdown-out",
            str(markdown),
        ]
    )

    assert exit_code == 0
    report = read_json(out)
    assert report["decision"]["status"] == "keep"
    assert report["provenance"]["candidate_id"] == "candidate-1"
    assert "candidate-1" in markdown.read_text(encoding="utf-8")


def test_recommended_report_cli_rejects_missing_input(tmp_path: Path) -> None:
    paths = _write_report_fixture(tmp_path)

    exit_code = main(
        [
            "recommended-report",
            "--baseline",
            str(paths["baseline"]),
            "--recommended",
            str(tmp_path / "missing.json"),
            "--profile",
            str(paths["profile"]),
            "--out",
            str(tmp_path / "report.json"),
        ]
    )

    assert exit_code == 2


def _write_report_fixture(tmp_path: Path) -> dict[str, Path]:
    baseline = tmp_path / "baseline.json"
    recommended = tmp_path / "recommended.json"
    profile = tmp_path / "profile.json"
    ranking = tmp_path / "ranking.json"
    write_json(
        baseline,
        {"success_count": 3, "failure_count": 0, "mean_latency_ms": 1000, "aggregate_tokens_per_second": 48},
    )
    write_json(
        recommended,
        {"success_count": 3, "failure_count": 0, "mean_latency_ms": 990, "aggregate_tokens_per_second": 49},
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
            "promotion": {"candidate_id": "candidate-1", "sweep_id": "sweep-1", "source_trial_ids": ["trial-1"]},
        },
    )
    write_json(
        ranking,
        {"objectives": {"balanced": [{"candidate_id": "candidate-1", "rank": 1, "metrics": {}}]}},
    )
    return {"baseline": baseline, "recommended": recommended, "profile": profile, "ranking": ranking}
