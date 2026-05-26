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

    assert first["candidate_count"] == 4
    assert first["trial_count"] == 4
    assert [trial["trial_id"] for trial in first["trials"]] == [
        trial["trial_id"] for trial in second["trials"]
    ]
    assert [candidate["candidate_id"] for candidate in first["candidates"]] == [
        candidate["candidate_id"] for candidate in second["candidates"]
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


def test_sweep_definition_rejects_bool_for_integer_parameter(tmp_path: Path) -> None:
    path = tmp_path / "bad-int.json"
    path.write_text(
        """{
  "sweep_id": "bad",
  "profile": "config/profiles/qwen3-coder-next-awq.json",
  "prompts": "config/prompts/qwen-baseline.json",
  "objectives": ["throughput"],
  "parameters": {"max_num_seqs": [true]}
}""",
        encoding="utf-8",
    )

    with pytest.raises(SweepError, match="invalid type"):
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

    assert report["objectives"]["throughput"][0]["candidate_id"] == plan["trials"][0]["candidate_id"]
    assert report["objectives"]["latency"][0]["candidate_id"] == plan["trials"][1]["candidate_id"]
    assert report["ranked_candidate_count"] == 2
    failed_candidate = plan["trials"][2]["candidate_id"]
    assert {"candidate_id": failed_candidate, "reason": "no successful repetitions"} in report["excluded_trials"]


def test_single_user_objective_ranks_latency_before_aggregate_throughput() -> None:
    plan = build_sweep_plan(load_sweep_definition(Path("config/sweeps/qwen-small-sweep.json")))
    plan["objectives"] = ["single_user", "throughput"]
    trial_ids = [trial["trial_id"] for trial in plan["trials"]]
    rows = [
        {
            "trial_id": trial_ids[0],
            "status": "completed",
            "summary": {"mean_latency_ms": 1200, "aggregate_tokens_per_second": 90, "failure_count": 0},
            "artifact_paths": {"summary": "aggregate-fast.json"},
        },
        {
            "trial_id": trial_ids[1],
            "status": "completed",
            "summary": {"mean_latency_ms": 700, "aggregate_tokens_per_second": 50, "failure_count": 0},
            "artifact_paths": {"summary": "responsive.json"},
        },
    ]

    report = rank_sweep_results(plan, rows)

    assert report["objectives"]["throughput"][0]["candidate_id"] == plan["trials"][0]["candidate_id"]
    assert report["objectives"]["single_user"][0]["candidate_id"] == plan["trials"][1]["candidate_id"]


def test_repeated_sweep_plan_adds_candidate_and_repetition_metadata() -> None:
    definition = load_sweep_definition(Path("config/sweeps/qwen-top2-repeated.json"))

    plan = build_sweep_plan(definition)

    assert plan["candidate_count"] == 2
    assert plan["trial_count"] == 6
    assert [trial["repetition_index"] for trial in plan["trials"]] == [0, 1, 2, 0, 1, 2]
    assert len({trial["candidate_id"] for trial in plan["trials"]}) == 2


def test_repeated_sweep_rejects_invalid_repetitions(tmp_path: Path) -> None:
    path = tmp_path / "bad-repetitions.json"
    path.write_text(
        """{
  "sweep_id": "bad",
  "profile": "config/profiles/qwen3-coder-next-awq.json",
  "prompts": "config/prompts/qwen-baseline.json",
  "repetitions": 0,
  "objectives": ["throughput"],
  "parameters": {"gpu_memory_utilization": [0.86]}
}""",
        encoding="utf-8",
    )

    with pytest.raises(SweepError, match="repetitions"):
        load_sweep_definition(path)


def test_repeated_sweep_ranking_aggregates_by_candidate() -> None:
    plan = build_sweep_plan(load_sweep_definition(Path("config/sweeps/qwen-top2-repeated.json")))
    candidate_ids = [candidate["candidate_id"] for candidate in plan["candidates"]]
    rows = []
    for trial in plan["trials"]:
        throughput = 48 if trial["candidate_id"] == candidate_ids[0] else 47
        latency = 1000 if trial["candidate_id"] == candidate_ids[0] else 1010
        rows.append(
            {
                "trial_id": trial["trial_id"],
                "candidate_id": trial["candidate_id"],
                "repetition_index": trial["repetition_index"],
                "status": "completed",
                "summary": {
                    "mean_latency_ms": latency + trial["repetition_index"],
                    "aggregate_tokens_per_second": throughput - trial["repetition_index"],
                    "failure_count": 0,
                },
                "artifact_paths": {"summary": f"{trial['trial_id']}.json"},
            }
        )
    rows[-1]["status"] = "failed"
    rows[-1]["failure_reason"] = "readiness timeout"
    rows[-1]["summary"] = {}

    report = rank_sweep_results(plan, rows)

    assert report["candidate_aggregates"][0]["success_count"] == 3
    assert report["candidate_aggregates"][1]["failure_count"] == 1
    assert report["objectives"]["throughput"][0]["candidate_id"] == candidate_ids[0]


def test_expanded_qwen_sweep_plan_shape() -> None:
    definition = load_sweep_definition(Path("config/sweeps/qwen-expanded-safe.json"))

    plan = build_sweep_plan(definition)
    preview = build_sweep_preview(plan)

    assert plan["candidate_count"] == 6
    assert plan["trial_count"] == 18
    assert plan["repetitions"] == 3
    assert preview["blocked"] is False
    assert {candidate["overrides"]["gpu_memory_utilization"] for candidate in plan["candidates"]} == {
        0.88,
        0.9,
        0.92,
    }
    assert {candidate["overrides"]["performance_mode"] for candidate in plan["candidates"]} == {
        "interactivity",
        "throughput",
    }


def test_scheduler_sweep_plan_shape_and_flags() -> None:
    definition = load_sweep_definition(Path("config/sweeps/qwen-scheduler-safe.json"))

    plan = build_sweep_plan(definition)
    preview = build_sweep_preview(plan)

    assert plan["candidate_count"] == 8
    assert plan["trial_count"] == 24
    assert plan["repetitions"] == 3
    assert preview["blocked"] is False
    assert preview["trials"][0]["order"] == 0
    assert {"max_num_batched_tokens", "max_num_seqs", "enable_chunked_prefill", "enable_prefix_caching"} <= set(
        plan["safe_parameters"]
    )
    first_profile = plan["trials"][0]["profile"]
    assert first_profile["optional_flags"]["max_num_batched_tokens"] == 4096
    assert first_profile["optional_flags"]["max_num_seqs"] == 16
    assert "--max-num-batched-tokens 4096" in plan["trials"][0]["serve_plan"]["command_line"]
    assert "--max-num-seqs 16" in plan["trials"][0]["serve_plan"]["command_line"]


def test_risky_session_sweep_preview_blocks_without_allowance() -> None:
    definition = load_sweep_definition(Path("config/sweeps/qwen-risky-session-small.json"))

    plan = build_sweep_plan(definition)
    preview = build_sweep_preview(plan)

    assert plan["candidate_count"] == 4
    assert plan["has_risky_session_flags"] is True
    assert plan["risk_tiers"]["block_size"] == "risky-session"
    assert preview["blocked"] is True
    assert "risky-session" in preview["blocked_reasons"][0]["reason"]


def test_risky_session_sweep_preview_allows_with_explicit_allowance() -> None:
    definition = load_sweep_definition(Path("config/sweeps/qwen-risky-session-small.json"))

    plan = build_sweep_plan(definition, allow_risky_session_flags=True)
    preview = build_sweep_preview(plan)

    assert plan["allow_risky_session_flags"] is True
    assert preview["blocked"] is False
    assert "--block-size" in preview["trials"][0]["command_line"]


def test_sweep_definition_rejects_blocked_parameter(tmp_path: Path) -> None:
    path = tmp_path / "blocked.json"
    path.write_text(
        """{
  "sweep_id": "bad",
  "profile": "config/profiles/qwen3-coder-next-awq-recommended.json",
  "prompts": "config/prompts/qwen-baseline.json",
  "objectives": ["throughput"],
  "parameters": {"download_dir": ["/tmp/cache"]}
}""",
        encoding="utf-8",
    )

    with pytest.raises(SweepError, match="blocked"):
        load_sweep_definition(path)


def test_explicit_candidate_sweep_plan_shape() -> None:
    definition = load_sweep_definition(Path("config/sweeps/qwen-high-impact-interactive.json"))

    plan = build_sweep_plan(definition)
    preview = build_sweep_preview(plan)

    assert plan["candidate_source"] == "explicit"
    assert plan["candidate_count"] == 8
    assert plan["trial_count"] == 16
    assert plan["prompt_set_id"] == "qwen-coding-interactive-v1"
    assert plan["has_risky_session_flags"] is True
    assert plan["allow_risky_session_flags"] is True
    assert preview["blocked"] is False
    assert any(candidate["overrides"].get("kv_cache_dtype") == "fp8" for candidate in plan["candidates"])


def test_explicit_candidate_sweep_rejects_bad_candidate(tmp_path: Path) -> None:
    path = tmp_path / "bad-candidates.json"
    path.write_text(
        """{
  "sweep_id": "bad",
  "profile": "config/profiles/qwen3-coder-next-awq-recommended.json",
  "prompts": "config/prompts/qwen-coding-interactive.json",
  "objectives": ["throughput"],
  "candidates": [{"download_dir": "/tmp/cache"}]
}""",
        encoding="utf-8",
    )

    with pytest.raises(SweepError, match="blocked"):
        load_sweep_definition(path)


def test_high_impact_workload_sweeps_are_distinct() -> None:
    paths = [
        Path("config/sweeps/qwen-high-impact-interactive.json"),
        Path("config/sweeps/qwen-high-impact-long.json"),
        Path("config/sweeps/qwen-high-impact-tool-json.json"),
    ]

    plans = [build_sweep_plan(load_sweep_definition(path)) for path in paths]

    assert [plan["prompt_set_id"] for plan in plans] == [
        "qwen-coding-interactive-v1",
        "qwen-coding-long-v1",
        "qwen-tool-json-v1",
    ]
    assert {plan["sweep_id"] for plan in plans} == {
        "qwen-high-impact-interactive",
        "qwen-high-impact-long",
        "qwen-high-impact-tool-json",
    }


def test_concurrent_workload_sweep_plan_shape() -> None:
    plan = build_sweep_plan(load_sweep_definition(Path("config/sweeps/qwen-high-impact-interactive-concurrent.json")))

    assert plan["prompt_set_id"] == "qwen-coding-interactive-concurrent-v1"
    assert plan["candidate_count"] == 4
    assert plan["trial_count"] == 8
    assert plan["trials"][0]["benchmark_plan"]["concurrency"] == 3


def test_fp8_rerun_sweeps_are_risky_session_only() -> None:
    paths = [
        Path("config/sweeps/qwen-fp8-rerun-interactive.json"),
        Path("config/sweeps/qwen-fp8-rerun-long.json"),
        Path("config/sweeps/qwen-fp8-rerun-tool-json.json"),
    ]

    plans = [build_sweep_plan(load_sweep_definition(path)) for path in paths]

    assert [plan["candidate_count"] for plan in plans] == [2, 1, 1]
    assert all(plan["has_risky_session_flags"] for plan in plans)
    assert all(plan["allow_risky_session_flags"] for plan in plans)
    assert all("kv_cache_dtype" in plan["risk_tiers"] for plan in plans)


def test_concurrency_saturation_sweep_plan_shapes() -> None:
    levels = [1, 2, 3, 4, 6, 8]
    paths = [Path(f"config/sweeps/qwen-concurrency-saturation-c{level}.json") for level in levels]

    plans = [build_sweep_plan(load_sweep_definition(path)) for path in paths]

    assert [plan["prompt_set_id"] for plan in plans] == [
        f"qwen-coding-interactive-concurrency-{level}-v1" for level in levels
    ]
    assert [plan["candidate_count"] for plan in plans] == [5, 5, 5, 5, 5, 5]
    assert [plan["trial_count"] for plan in plans] == [10, 10, 10, 10, 10, 10]
    assert [plan["trials"][0]["benchmark_plan"]["concurrency"] for plan in plans] == levels


def test_single_user_sweep_plan_uses_one_request_workload() -> None:
    plan = build_sweep_plan(load_sweep_definition(Path("config/sweeps/qwen-single-user-interactive.json")))

    assert plan["prompt_set_id"] == "qwen-coding-interactive-concurrency-1-v1"
    assert "single_user" in plan["objectives"]
    assert plan["trials"][0]["benchmark_plan"]["concurrency"] == 1
    assert plan["candidate_count"] >= 2
