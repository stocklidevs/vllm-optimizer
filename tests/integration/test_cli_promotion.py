from pathlib import Path

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.cli import main


def test_promote_preview_cli_writes_preview(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    out = tmp_path / "preview.json"

    exit_code = main(
        [
            "promote-preview",
            "--ranking",
            str(ranking_path),
            "--objective",
            "balanced",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    preview = read_json(out)
    assert preview["candidate_id"] == "qwen-scheduler-safe-c005-8b1dabfa"
    assert preview["eligible"] is True


def test_promote_preview_cli_can_select_candidate(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    data = read_json(ranking_path)
    data["objectives"]["balanced"].append(
        {
            "candidate_id": "qwen-scheduler-safe-c009-selected",
            "rank": 2,
            "metrics": {"aggregate_tokens_per_second": 97.0, "mean_latency_ms": 720.0},
        }
    )
    data["candidate_aggregates"].append(
        {
            "candidate_id": "qwen-scheduler-safe-c009-selected",
            "success_count": 1,
            "source_trials": data["candidate_aggregates"][0]["source_trials"],
        }
    )
    write_json(ranking_path, data)
    out = tmp_path / "preview-selected.json"

    exit_code = main(
        [
            "promote-preview",
            "--ranking",
            str(ranking_path),
            "--candidate-id",
            "qwen-scheduler-safe-c009-selected",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    assert read_json(out)["candidate_id"] == "qwen-scheduler-safe-c009-selected"


def test_promote_profile_cli_writes_profile_and_summary(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    profile_out = tmp_path / "recommended.json"
    summary_out = tmp_path / "recommended.md"

    exit_code = main(
        [
            "promote-profile",
            "--ranking",
            str(ranking_path),
            "--profile-out",
            str(profile_out),
            "--summary-out",
            str(summary_out),
        ]
    )

    assert exit_code == 0
    profile = read_json(profile_out)
    assert profile["profile_id"] == "qwen3-coder-next-awq-recommended"
    assert profile["promotion"]["candidate_id"] == "qwen-scheduler-safe-c005-8b1dabfa"
    assert "qwen-scheduler-safe-c005-r01-b2b9fb46" in summary_out.read_text(encoding="utf-8")


def test_promote_profile_cli_refuses_existing_output(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    profile_out = tmp_path / "recommended.json"
    summary_out = tmp_path / "recommended.md"
    profile_out.write_text("{}", encoding="utf-8")

    exit_code = main(
        [
            "promote-profile",
            "--ranking",
            str(ranking_path),
            "--profile-out",
            str(profile_out),
            "--summary-out",
            str(summary_out),
        ]
    )

    assert exit_code == 2
    assert not summary_out.exists()


def test_promote_confirmed_profile_cli_writes_only_after_ab_switch(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    confirmation_path = _write_confirmation_report(tmp_path, "switch-to-recommended")
    profile_out = tmp_path / "recommended.json"
    summary_out = tmp_path / "recommended.md"

    exit_code = main(
        [
            "promote-confirmed-profile",
            "--confirmation-report",
            str(confirmation_path),
            "--ranking",
            str(ranking_path),
            "--profile-out",
            str(profile_out),
            "--summary-out",
            str(summary_out),
            "--expected-recommended-label",
            "risky-winner",
        ]
    )

    assert exit_code == 0
    profile = read_json(profile_out)
    assert profile["promotion"]["confirmation"]["decision"]["status"] == "switch-to-recommended"
    assert profile["promotion"]["confirmation"]["recommended"]["label"] == "risky-winner"


def test_promote_confirmed_profile_cli_rejects_inconclusive_ab_report(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    confirmation_path = _write_confirmation_report(tmp_path, "inconclusive")
    profile_out = tmp_path / "recommended.json"

    exit_code = main(
        [
            "promote-confirmed-profile",
            "--confirmation-report",
            str(confirmation_path),
            "--ranking",
            str(ranking_path),
            "--profile-out",
            str(profile_out),
            "--summary-out",
            str(tmp_path / "recommended.md"),
        ]
    )

    assert exit_code == 2
    assert not profile_out.exists()


def test_promote_preview_cli_rejects_missing_objective(tmp_path: Path) -> None:
    ranking_path = _write_ranking_fixture(tmp_path)
    out = tmp_path / "preview.json"

    exit_code = main(
        [
            "promote-preview",
            "--ranking",
            str(ranking_path),
            "--objective",
            "memory",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 2
    assert not out.exists()


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
                        "metrics": {"mean_latency_ms": 1004.0, "aggregate_tokens_per_second": 48.16},
                    }
                ]
            },
            "candidate_aggregates": [
                {
                    "candidate_id": "qwen-scheduler-safe-c005-8b1dabfa",
                    "success_count": 3,
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
                            "status": "completed",
                            "artifact_paths": {"plan": str(plan_path)},
                        }
                    ],
                }
            ],
        },
    )
    return ranking_path


def _write_confirmation_report(tmp_path: Path, status: str) -> Path:
    path = tmp_path / "ab-report.json"
    write_json(
        path,
        {
            "prompt_set_id": "qwen-baseline-v1",
            "noise_percent": 1.0,
            "decision": {"status": status, "reason": "fixture decision"},
            "aggregates": {
                "original": {
                    "label": "current-recommended",
                    "repetition_count": 3,
                    "failure_rate": 0.0,
                    "mean_latency_ms": 1000.0,
                    "latency_spread_ms": 3.0,
                    "mean_tokens_per_second": 48.0,
                    "tokens_per_second_spread": 0.1,
                },
                "recommended": {
                    "label": "risky-winner",
                    "repetition_count": 3,
                    "failure_rate": 0.0,
                    "mean_latency_ms": 950.0,
                    "latency_spread_ms": 2.0,
                    "mean_tokens_per_second": 50.0,
                    "tokens_per_second_spread": 0.2,
                },
            },
            "deltas": {
                "mean_latency_ms": {"absolute": -50.0, "percent": -5.0},
                "mean_tokens_per_second": {"absolute": 2.0, "percent": 4.1667},
                "failure_rate": {"absolute": 0.0},
            },
            "inputs": {
                "original_label": "current-recommended",
                "recommended_label": "risky-winner",
            },
        },
    )
    return path
