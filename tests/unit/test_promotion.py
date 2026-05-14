from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.promotion import (
    PromotionError,
    build_promotion_preview,
    render_promotion_summary,
    write_promoted_profile,
)
from vllm_optimizer.serve_profiles import parse_serve_profile


def test_build_promotion_preview_selects_balanced_candidate(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)

    preview = build_promotion_preview(
        ranking_path,
        "balanced",
        "qwen3-coder-next-awq-recommended",
    )

    assert preview["candidate_id"] == "qwen-scheduler-safe-c005-8b1dabfa"
    assert preview["proposed_profile"]["profile_id"] == "qwen3-coder-next-awq-recommended"
    assert preview["proposed_profile"]["optional_flags"] == {
        "enable_chunked_prefill": True,
        "enable_prefix_caching": False,
        "max_num_batched_tokens": 4096,
        "max_num_seqs": 16,
    }
    assert preview["proposed_profile"]["promotion"]["source_trial_ids"] == [
        "qwen-scheduler-safe-c005-r01-b2b9fb46",
        "qwen-scheduler-safe-c005-r02-8795b069",
        "qwen-scheduler-safe-c005-r03-fbbfebca",
    ]
    parse_serve_profile(preview["proposed_profile"])


def test_build_promotion_preview_is_deterministic(tmp_path: Path) -> None:
    ranking = _write_ranking_fixture(tmp_path)

    first = build_promotion_preview(ranking)
    second = build_promotion_preview(ranking)

    assert first == second


def test_write_promoted_profile_writes_profile_and_summary(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    profile_out = tmp_path / "recommended.json"
    summary_out = tmp_path / "recommended.md"

    result = write_promoted_profile(
        ranking_path,
        profile_out,
        summary_out,
    )

    profile = read_json(profile_out)
    summary = summary_out.read_text(encoding="utf-8")
    assert result["profile_path"] == str(profile_out)
    assert profile["promotion"]["candidate_id"] == "qwen-scheduler-safe-c005-8b1dabfa"
    assert profile["promotion"]["objective"] == "balanced"
    assert profile["optional_flags"]["enable_chunked_prefill"] is True
    assert "qwen-scheduler-safe-c005-8b1dabfa" in summary
    assert "qwen-scheduler-safe-c005-r01-b2b9fb46" in summary
    parse_serve_profile(profile)


def test_write_promoted_profile_refuses_overwrite(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    profile_out = tmp_path / "recommended.json"
    summary_out = tmp_path / "recommended.md"
    profile_out.write_text("{}", encoding="utf-8")

    with pytest.raises(PromotionError, match="already exists"):
        write_promoted_profile(
            ranking_path,
            profile_out,
            summary_out,
        )

    assert not summary_out.exists()


def test_promotion_rejects_missing_objective(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)

    with pytest.raises(PromotionError, match="not present"):
        build_promotion_preview(ranking_path, "memory")


def test_promotion_rejects_zero_success_candidate(tmp_path: Path) -> None:
    plan_path = tmp_path / "trial-plan.json"
    write_json(
        plan_path,
        {
            "serve_plan": {
                "serve_command": [
                    "vllm",
                    "serve",
                    "model",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8001",
                    "--served-model-name",
                    "model",
                    "--max-model-len",
                    "32768",
                    "--gpu-memory-utilization",
                    "0.90",
                    "--tool-call-parser",
                    "qwen3_coder",
                    "--performance-mode",
                    "interactivity",
                ]
            }
        },
    )
    ranking_path = tmp_path / "ranking.json"
    write_json(
        ranking_path,
        {
            "sweep_id": "bad",
            "objectives": {"balanced": [{"candidate_id": "candidate-1", "rank": 1, "metrics": {}}]},
            "candidate_aggregates": [
                {
                    "candidate_id": "candidate-1",
                    "success_count": 0,
                    "source_trials": [
                        {
                            "trial_id": "trial-1",
                            "status": "completed",
                            "artifact_paths": {"plan": str(plan_path)},
                        }
                    ],
                }
            ],
        },
    )

    with pytest.raises(PromotionError, match="no successful"):
        build_promotion_preview(ranking_path)


def test_render_promotion_summary_mentions_required_provenance(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    preview = build_promotion_preview(ranking_path)

    summary = render_promotion_summary(preview, Path("config/profiles/recommended.json"))

    assert ranking_path.as_posix() in summary
    assert "balanced" in summary
    assert "qwen-scheduler-safe-c005-8b1dabfa" in summary
    assert "qwen-scheduler-safe-c005-r01-b2b9fb46" in summary


def _write_ranking_fixture(tmp_path: Path) -> Path:
    plan_path = tmp_path / "trial-plan.json"
    write_json(
        plan_path,
        {
            "serve_plan": {
                "serve_command": [
                    "$HOME/qwen3next-venv/bin/vllm",
                    "serve",
                    "cyankiwi/Qwen3-Coder-Next-AWQ-4bit",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8001",
                    "--served-model-name",
                    "Qwen3-Coder-Next",
                    "--max-model-len",
                    "32768",
                    "--gpu-memory-utilization",
                    "0.90",
                    "--enable-auto-tool-choice",
                    "--tool-call-parser",
                    "qwen3_coder",
                    "--performance-mode",
                    "interactivity",
                    "--enable-chunked-prefill",
                    "--max-num-batched-tokens",
                    "4096",
                    "--max-num-seqs",
                    "16",
                ]
            }
        },
    )
    ranking_path = tmp_path / "ranking.json"
    write_json(
        ranking_path,
        {
            "sweep_id": "qwen-scheduler-safe",
            "objectives": {
                "balanced": [
                    {
                        "candidate_id": "qwen-scheduler-safe-c005-8b1dabfa",
                        "rank": 1,
                        "metrics": {
                            "aggregate_tokens_per_second": 48.16487104955972,
                            "failure_count": 0,
                            "failure_rate": 0.0,
                            "latency_spread_ms": 22.291004663067316,
                            "mean_latency_ms": 1004.0,
                            "success_count": 3,
                            "tokens_per_second_spread": 1.0855277897005222,
                        },
                        "baseline_delta": {},
                    }
                ]
            },
            "candidate_aggregates": [
                {
                    "candidate_id": "qwen-scheduler-safe-c005-8b1dabfa",
                    "success_count": 3,
                    "failure_count": 0,
                    "failure_rate": 0.0,
                    "overrides": {
                        "enable_chunked_prefill": True,
                        "enable_prefix_caching": False,
                        "gpu_memory_utilization": 0.9,
                        "max_model_len": 32768,
                        "max_num_batched_tokens": 4096,
                        "max_num_seqs": 16,
                        "performance_mode": "interactivity",
                    },
                    "source_trials": [
                        {
                            "trial_id": "qwen-scheduler-safe-c005-r01-b2b9fb46",
                            "repetition_index": 0,
                            "status": "completed",
                            "artifact_paths": {"plan": str(plan_path)},
                        },
                        {
                            "trial_id": "qwen-scheduler-safe-c005-r02-8795b069",
                            "repetition_index": 1,
                            "status": "completed",
                            "artifact_paths": {"plan": str(plan_path)},
                        },
                        {
                            "trial_id": "qwen-scheduler-safe-c005-r03-fbbfebca",
                            "repetition_index": 2,
                            "status": "completed",
                            "artifact_paths": {"plan": str(plan_path)},
                        },
                    ],
                }
            ],
        },
    )
    return ranking_path
