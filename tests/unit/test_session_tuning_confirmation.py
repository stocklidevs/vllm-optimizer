from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.discovery import DiscoveryTarget
from vllm_optimizer.session_tuning_confirmation import (
    SessionTuningConfirmationError,
    SessionTuningConfirmationRequest,
    run_session_tuning_confirmation,
)


def test_session_tuning_confirmation_writes_repetitions_and_report(tmp_path: Path) -> None:
    profile = tmp_path / "profile.json"
    prompts = tmp_path / "prompts.json"
    tuning = tmp_path / "tuning.json"
    _write_profile(profile)
    _write_prompts(prompts)
    _write_tuning(tuning)
    calls = []

    def runner(_target, _profile, _prompt_set, out_dir, _timeout_seconds, session_tuning=None):
        calls.append((out_dir.name, session_tuning is not None))
        if session_tuning is None:
            _write_summary(out_dir / "summary.json", latency=1000, throughput=50)
        else:
            _write_summary(out_dir / "summary.json", latency=970, throughput=53)
        return {"summary": read_json(out_dir / "summary.json")}

    result = run_session_tuning_confirmation(
        SessionTuningConfirmationRequest(
            target=DiscoveryTarget("mock", "mock@example", ()),
            profile_path=profile,
            prompts_path=prompts,
            session_tuning_path=tuning,
            out_dir=tmp_path / "out",
            repetitions=2,
            current_label="current",
            tuned_label="tuned",
            allow_session_tuning=True,
            benchmark_runner=runner,
        )
    )

    assert calls == [
        ("current-r1", False),
        ("tuned-r1", True),
        ("current-r2", False),
        ("tuned-r2", True),
    ]
    assert result["decision"]["status"] == "switch-to-recommended"
    assert (tmp_path / "out" / "confirmation-report.json").exists()
    assert (tmp_path / "out" / "confirmation-report.md").exists()
    assert (tmp_path / "out" / "summary.json").exists()


def test_session_tuning_confirmation_requires_approval(tmp_path: Path) -> None:
    with pytest.raises(SessionTuningConfirmationError, match="--allow-session-tuning"):
        run_session_tuning_confirmation(
            SessionTuningConfirmationRequest(
                target=DiscoveryTarget("mock", "mock@example", ()),
                profile_path=tmp_path / "profile.json",
                prompts_path=tmp_path / "prompts.json",
                session_tuning_path=tmp_path / "tuning.json",
                out_dir=tmp_path / "out",
                allow_session_tuning=False,
            )
        )


def _write_profile(path: Path) -> None:
    write_json(
        path,
        {
            "profile_id": "profile",
            "vllm_executable": "vllm",
            "model": "model",
            "served_model_name": "served",
            "host": "0.0.0.0",
            "port": 8001,
            "max_model_len": 32768,
            "gpu_memory_utilization": 0.9,
            "enable_auto_tool_choice": True,
            "tool_call_parser": "qwen3_coder",
            "performance_mode": "interactivity",
            "optional_flags": {},
        },
    )


def _write_prompts(path: Path) -> None:
    write_json(
        path,
        {
            "prompt_set_id": "prompts",
            "concurrency": 1,
            "cases": [
                {
                    "case_id": "case-1",
                    "messages": [{"role": "user", "content": "hello"}],
                    "max_tokens": 8,
                    "temperature": 0,
                }
            ],
        },
    )


def _write_tuning(path: Path) -> None:
    write_json(
        path,
        {
            "profile_id": "tuning",
            "classification": "session-mutating",
            "environment": {"CUDA_MODULE_LOADING": "LAZY"},
            "ulimits": {"nofile": 500000},
        },
    )


def _write_summary(path: Path, latency: float, throughput: float) -> None:
    write_json(
        path,
        {
            "mean_latency_ms": latency,
            "aggregate_tokens_per_second": throughput,
            "success_count": 1,
            "failure_count": 0,
        },
    )
