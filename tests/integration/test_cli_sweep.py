from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_sweep_plan_cli_writes_plan(tmp_path: Path) -> None:
    out = tmp_path / "plan.json"

    exit_code = main(
        [
            "sweep-plan",
            "--sweep",
            "config/sweeps/qwen-small-sweep.json",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    plan = read_json(out)
    assert plan["trial_count"] == 4
    assert plan["will_execute"] is False


def test_sweep_preview_cli_writes_preview(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    preview_path = tmp_path / "preview.json"
    assert main(["sweep-plan", "--sweep", "config/sweeps/qwen-small-sweep.json", "--out", str(plan_path)]) == 0

    exit_code = main(["sweep-preview", "--plan", str(plan_path), "--out", str(preview_path)])

    assert exit_code == 0
    preview = read_json(preview_path)
    assert preview["blocked"] is False
    assert preview["trial_count"] == 4


def test_sweep_rank_cli_writes_ranking(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    results_path = tmp_path / "results.json"
    ranking_path = tmp_path / "ranking.json"
    assert main(["sweep-plan", "--sweep", "config/sweeps/qwen-small-sweep.json", "--out", str(plan_path)]) == 0
    plan = read_json(plan_path)
    trial_id = plan["trials"][0]["trial_id"]
    results_path.write_text(
        f"""{{
  "results": [
    {{
      "trial_id": "{trial_id}",
      "status": "completed",
      "summary": {{
        "mean_latency_ms": 900,
        "aggregate_tokens_per_second": 45,
        "failure_count": 0
      }},
      "artifact_paths": {{"summary": "summary.json"}}
    }}
  ]
}}""",
        encoding="utf-8",
    )

    exit_code = main(["sweep-rank", "--plan", str(plan_path), "--results", str(results_path), "--out", str(ranking_path)])

    assert exit_code == 0
    ranking = read_json(ranking_path)
    assert ranking["objectives"]["throughput"][0]["trial_id"] == trial_id
