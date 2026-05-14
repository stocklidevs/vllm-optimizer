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


def test_pipeline_confirm_mode_writes_candidate_and_report_without_promotion(tmp_path: Path) -> None:
    ranking = _write_confirm_fixture(tmp_path)
    current_profile = tmp_path / "current-profile.json"
    prompts = tmp_path / "prompts.json"
    _write_profile(current_profile, profile_id="current")
    prompts.write_text('{"prompt_set_id":"confirm-prompts","concurrency":1,"cases":[]}', encoding="utf-8")
    _write_summary(tmp_path / "confirmation" / "current-r1" / "summary.json", latency=1000, throughput=50)
    _write_summary(tmp_path / "confirmation" / "candidate-r1" / "summary.json", latency=980, throughput=52)

    result = run_optimizer_pipeline(
        OptimizerPipelineRequest(
            mode="confirm",
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=tmp_path,
            current_profile_path=current_profile,
            prompts_path=prompts,
            candidate_profile_out=tmp_path / "candidate.json",
            confirmed_profile_out=tmp_path / "confirmed.json",
            confirmation_repetitions=1,
            original_label="current",
            recommended_label="candidate",
        )
    )

    assert result["completed_stages"] == ["plan", "preview", "report", "confirm"]
    assert (tmp_path / "candidate.json").exists()
    assert (tmp_path / "confirmation" / "confirmation-report.json").exists()
    assert not (tmp_path / "confirmed.json").exists()
    assert result["promotion"]["automatic"] is False
    assert result["promotion"]["allowed"] is False


def test_pipeline_confirm_mode_promotes_only_when_allowed(tmp_path: Path) -> None:
    _write_confirm_fixture(tmp_path)
    current_profile = tmp_path / "current-profile.json"
    prompts = tmp_path / "prompts.json"
    _write_profile(current_profile, profile_id="current")
    prompts.write_text('{"prompt_set_id":"confirm-prompts","concurrency":1,"cases":[]}', encoding="utf-8")
    _write_summary(tmp_path / "confirmation" / "current-r1" / "summary.json", latency=1000, throughput=50)
    _write_summary(tmp_path / "confirmation" / "candidate-r1" / "summary.json", latency=980, throughput=52)

    result = run_optimizer_pipeline(
        OptimizerPipelineRequest(
            mode="confirm",
            sweep_path=Path("config/sweeps/qwen-small-sweep.json"),
            out_dir=tmp_path,
            current_profile_path=current_profile,
            prompts_path=prompts,
            candidate_profile_out=tmp_path / "candidate.json",
            confirmed_profile_out=tmp_path / "confirmed.json",
            confirmation_repetitions=1,
            original_label="current",
            recommended_label="candidate",
            allow_promotion=True,
        )
    )

    assert (tmp_path / "confirmed.json").exists()
    confirmed = read_json(tmp_path / "confirmed.json")
    assert confirmed["promotion"]["confirmation"]["decision"]["status"] == "switch-to-recommended"
    assert result["promotion"]["allowed"] is True
    assert result["promotion"]["promoted"] is True


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


def _write_confirm_fixture(tmp_path: Path) -> Path:
    live = tmp_path / "live"
    trial_dir = live / "trial-1"
    trial_dir.mkdir(parents=True)
    _write_profile(tmp_path / "source-profile.json", profile_id="source")
    plan_path = trial_dir / "plan.json"
    plan_path.write_text(
        """{
  "serve_plan": {
    "serve_command": [
      "$HOME/qwen3next-venv/bin/vllm",
      "serve",
      "model",
      "--host",
      "0.0.0.0",
      "--port",
      "8001",
      "--served-model-name",
      "served",
      "--max-model-len",
      "32768",
      "--gpu-memory-utilization",
      "0.90",
      "--enable-auto-tool-choice",
      "--tool-call-parser",
      "qwen3_coder",
      "--performance-mode",
      "interactivity",
      "--block-size",
      "16",
      "--max-num-batched-tokens",
      "4096",
      "--max-num-seqs",
      "16"
    ]
  }
}""",
        encoding="utf-8",
    )
    ranking = {
        "sweep_id": "confirm-fixture",
        "objectives": {
            "balanced": [
                {
                    "candidate_id": "candidate-1",
                    "rank": 1,
                    "metrics": {
                        "mean_latency_ms": 980,
                        "aggregate_tokens_per_second": 52,
                        "failure_count": 0,
                        "failure_rate": 0.0,
                        "success_count": 1,
                        "overrides": {"gpu_memory_utilization": 0.9},
                    },
                }
            ]
        },
        "candidate_aggregates": [
            {
                "candidate_id": "candidate-1",
                "order": 0,
                "overrides": {"gpu_memory_utilization": 0.9},
                "success_count": 1,
                "failure_count": 0,
                "source_trials": [
                    {
                        "trial_id": "trial-1",
                        "status": "completed",
                        "artifact_paths": {"plan": plan_path.as_posix()},
                    }
                ],
            }
        ],
    }
    from vllm_optimizer.artifacts import write_json

    write_json(live / "ranking.json", ranking)
    return live / "ranking.json"


def _write_profile(path: Path, profile_id: str) -> None:
    from vllm_optimizer.artifacts import write_json

    write_json(
        path,
        {
            "profile_id": profile_id,
            "vllm_executable": "$HOME/qwen3next-venv/bin/vllm",
            "model": "model",
            "served_model_name": "served",
            "host": "0.0.0.0",
            "port": 8001,
            "max_model_len": 32768,
            "gpu_memory_utilization": 0.9,
            "enable_auto_tool_choice": True,
            "tool_call_parser": "qwen3_coder",
            "performance_mode": "interactivity",
            "optional_flags": {"block_size": 16},
        },
    )


def _write_summary(path: Path, latency: float, throughput: float) -> None:
    from vllm_optimizer.artifacts import write_json

    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        path,
        {
            "mean_latency_ms": latency,
            "aggregate_tokens_per_second": throughput,
            "success_count": 1,
            "failure_count": 0,
        },
    )
