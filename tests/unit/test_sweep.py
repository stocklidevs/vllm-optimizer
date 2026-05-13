from pathlib import Path

import pytest

from vllm_optimizer.sweep import (
    SweepError,
    build_sweep_plan,
    build_sweep_preview,
    load_sweep_definition,
    rank_sweep_results,
)


def test_build_sweep_plan_is_deterministic() -> None:
    definition = load_sweep_definition(Path("config/sweeps/qwen-small-sweep.json"))

    first = build_sweep_plan(definition)
    second = build_sweep_plan(definition)

    assert first["trial_count"] == 4
    assert [trial["trial_id"] for trial in first["trials"]] == [
        trial["trial_id"] for trial in second["trials"]
    ]
    assert first["trials"][0]["overrides"] == {
        "gpu_memory_utilization": 0.86,
        "max_model_len": 16384,
    }
    assert first["trials"][0]["serve_plan"]["will_execute"] is False


def test_sweep_definition_rejects_unsafe_parameter(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.json"
    path.write_text(
        """{
  "sweep_id": "bad",
  "profile": "config/profiles/qwen3-coder-next-awq.json",
  "prompts": "config/prompts/qwen-baseline.json",
  "objectives": ["throughput"],
  "parameters": {"nvidia_persistence_mode": [true]}
}""",
        encoding="utf-8",
    )

    with pytest.raises(SweepError, match="not allowed"):
        load_sweep_definition(path)


def test_sweep_definition_rejects_out_of_bounds_value(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.json"
    path.write_text(
        """{
  "sweep_id": "bad",
  "profile": "config/profiles/qwen3-coder-next-awq.json",
  "prompts": "config/prompts/qwen-baseline.json",
  "objectives": ["throughput"],
  "parameters": {"gpu_memory_utilization": [0.99]}
}""",
        encoding="utf-8",
    )

    with pytest.raises(SweepError, match="safe maximum"):
        load_sweep_definition(path)


def test_build_sweep_preview_lists_trials_without_execution() -> None:
    plan = build_sweep_plan(load_sweep_definition(Path("config/sweeps/qwen-small-sweep.json")))

    preview = build_sweep_preview(plan)

    assert preview["will_execute"] is False
    assert preview["blocked"] is False
    assert preview["trial_count"] == 4
    assert preview["trials"][0]["cleanup"].startswith("stop vLLM")


def test_build_sweep_preview_blocks_unsafe_trial() -> None:
    plan = build_sweep_plan(load_sweep_definition(Path("config/sweeps/qwen-small-sweep.json")))
    plan["trials"][0]["classification"] = "persistent-mutating"

    preview = build_sweep_preview(plan)

    assert preview["blocked"] is True
    assert "classification" in preview["blocked_reasons"][0]["reason"]


def test_rank_sweep_results_reports_objective_rankings() -> None:
    plan = build_sweep_plan(load_sweep_definition(Path("config/sweeps/qwen-small-sweep.json")))
    trial_ids = [trial["trial_id"] for trial in plan["trials"]]
    rows = [
        {
            "trial_id": trial_ids[0],
            "status": "completed",
            "summary": {"mean_latency_ms": 1000, "aggregate_tokens_per_second": 40, "failure_count": 0},
            "artifact_paths": {"summary": "a.json"},
        },
        {
            "trial_id": trial_ids[1],
            "status": "completed",
            "summary": {"mean_latency_ms": 800, "aggregate_tokens_per_second": 35, "failure_count": 0},
            "artifact_paths": {"summary": "b.json"},
        },
        {
            "trial_id": trial_ids[2],
            "status": "failed",
            "summary": {},
            "failure_reason": "readiness timeout",
        },
    ]

    report = rank_sweep_results(plan, rows)

    assert report["objectives"]["throughput"][0]["trial_id"] == trial_ids[0]
    assert report["objectives"]["latency"][0]["trial_id"] == trial_ids[1]
    assert report["ranked_trial_count"] == 2
    assert {"trial_id": trial_ids[2], "reason": "readiness timeout"} in report["excluded_trials"]
