from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.optimizer_pipeline import (
    OptimizerPipelineError,
    OptimizerPipelineRequest,
    run_optimizer_pipeline,
)


def test_pipeline_plan_mode_writes_stage_paths(tmp_path: Path) -> None:
    result = run_optimizer_pipeline(
        OptimizerPipelineRequest(
            mode="plan",
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=tmp_path,
        )
    )

    plan = read_json(tmp_path / "pipeline-plan.json")
    assert result["mode"] == "plan"
    assert result["artifacts"]["pipeline_plan"] == (tmp_path / "pipeline-plan.json").as_posix()
    assert plan["stages"][0]["name"] == "plan"
    assert plan["artifacts"]["sweep_plan"] == (tmp_path / "sweep-plan.json").as_posix()
    assert plan["remote_actions"] == []


def test_pipeline_preview_mode_writes_sweep_plan_and_preview(tmp_path: Path) -> None:
    result = run_optimizer_pipeline(
        OptimizerPipelineRequest(
            mode="preview",
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=tmp_path,
        )
    )

    assert result["completed_stages"] == ["plan", "preview"]
    assert (tmp_path / "sweep-plan.json").exists()
    assert (tmp_path / "sweep-preview.json").exists()
    preview = read_json(tmp_path / "sweep-preview.json")
    assert preview["blocked"] is False


def test_pipeline_report_mode_ranks_existing_results_and_writes_report(tmp_path: Path) -> None:
    run_optimizer_pipeline(
        OptimizerPipelineRequest(
            mode="preview",
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=tmp_path,
        )
    )
    plan = read_json(tmp_path / "sweep-plan.json")
    trial = plan["trials"][0]
    live = tmp_path / "live"
    live.mkdir()
    (live / "results.jsonl").write_text(
        "\n".join(
            [
                _result_row(
                    trial_id=trial["trial_id"],
                    candidate_id=trial["candidate_id"],
                    latency=900.0,
                    throughput=45.0,
                )
            ]
        ),
        encoding="utf-8",
    )

    result = run_optimizer_pipeline(
        OptimizerPipelineRequest(
            mode="report",
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=tmp_path,
        )
    )

    assert result["completed_stages"] == ["plan", "preview", "report"]
    assert (tmp_path / "live" / "ranking.json").exists()
    assert (tmp_path / "report.json").exists()
    report = read_json(tmp_path / "report.json")
    assert report["recommendation"]["candidate_id"] == trial["candidate_id"]


def test_pipeline_run_mode_requires_remote_config(tmp_path: Path) -> None:
    with pytest.raises(OptimizerPipelineError, match="remote config"):
        run_optimizer_pipeline(
            OptimizerPipelineRequest(
                mode="run",
                sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
                out_dir=tmp_path,
            )
        )


def _result_row(trial_id: str, candidate_id: str, latency: float, throughput: float) -> str:
    return (
        "{"
        f'"trial_id":"{trial_id}",'
        f'"candidate_id":"{candidate_id}",'
        '"status":"completed",'
        f'"summary":{{"mean_latency_ms":{latency},"aggregate_tokens_per_second":{throughput},"success_count":1,"failure_count":0}},'
        '"artifact_paths":{"summary":"summary.json"}'
        "}"
    )
