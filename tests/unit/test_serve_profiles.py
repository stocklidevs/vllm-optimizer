from pathlib import Path

import pytest

from vllm_optimizer.serve_profiles import (
    ServeProfileError,
    build_serve_plan,
    load_serve_profile,
    parse_serve_profile,
    render_vllm_serve_command,
)


def test_load_qwen_profile_renders_user_command() -> None:
    profile = load_serve_profile(Path("config/profiles/qwen3-coder-next-awq.json"))

    command = render_vllm_serve_command(profile)

    assert command == [
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
    ]


def test_build_serve_plan_is_dry_run_only() -> None:
    profile = load_serve_profile(Path("config/profiles/qwen3-coder-next-awq.json"))

    plan = build_serve_plan(profile)

    assert plan["mode"] == "dry-run"
    assert plan["classification"] == "session-mutating"
    assert plan["will_execute"] is False


def test_parse_serve_profile_validates_memory_utilization() -> None:
    with pytest.raises(ServeProfileError, match="gpu_memory_utilization"):
        parse_serve_profile(
            {
                "profile_id": "bad",
                "model": "m",
                "served_model_name": "m",
                "host": "0.0.0.0",
                "port": 8001,
                "max_model_len": 32768,
                "gpu_memory_utilization": 1.5,
                "enable_auto_tool_choice": True,
                "tool_call_parser": "qwen3_coder",
                "performance_mode": "interactivity",
                "vllm_executable": "vllm",
            }
        )


def test_optional_flags_render_when_approved() -> None:
    profile = parse_serve_profile(
        {
            "profile_id": "scheduler",
            "model": "m",
            "served_model_name": "m",
            "host": "0.0.0.0",
            "port": 8001,
            "max_model_len": 32768,
            "gpu_memory_utilization": 0.9,
            "enable_auto_tool_choice": True,
            "tool_call_parser": "qwen3_coder",
            "performance_mode": "interactivity",
            "vllm_executable": "vllm",
            "optional_flags": {
                "max_num_batched_tokens": 8192,
                "max_num_seqs": 32,
                "enable_chunked_prefill": True,
                "enable_prefix_caching": False,
            },
        }
    )

    command = render_vllm_serve_command(profile)

    assert "--max-num-batched-tokens" in command
    assert "8192" in command
    assert "--max-num-seqs" in command
    assert "32" in command
    assert "--enable-chunked-prefill" in command
    assert "--enable-prefix-caching" not in command


def test_optional_flags_reject_unknown_flags() -> None:
    with pytest.raises(ServeProfileError, match="not approved"):
        parse_serve_profile(
            {
                "profile_id": "bad",
                "model": "m",
                "served_model_name": "m",
                "host": "0.0.0.0",
                "port": 8001,
                "max_model_len": 32768,
                "gpu_memory_utilization": 0.9,
                "enable_auto_tool_choice": True,
                "tool_call_parser": "qwen3_coder",
                "performance_mode": "interactivity",
                "vllm_executable": "vllm",
                "optional_flags": {"download_dir": "/tmp/cache"},
            }
        )


def test_risky_session_flags_render_when_approved() -> None:
    profile = parse_serve_profile(
        {
            "profile_id": "risky",
            "model": "m",
            "served_model_name": "m",
            "host": "0.0.0.0",
            "port": 8001,
            "max_model_len": 32768,
            "gpu_memory_utilization": 0.9,
            "enable_auto_tool_choice": True,
            "tool_call_parser": "qwen3_coder",
            "performance_mode": "interactivity",
            "vllm_executable": "vllm",
            "optional_flags": {
                "block_size": 32,
                "enforce_eager": True,
                "kv_cache_dtype": "auto",
            },
        }
    )

    command = render_vllm_serve_command(profile)

    assert "--block-size" in command
    assert "32" in command
    assert "--enforce-eager" in command
    assert "--kv-cache-dtype" in command
    assert "auto" in command


def test_risky_session_flags_validate_allowed_values() -> None:
    with pytest.raises(ServeProfileError, match="block_size"):
        parse_serve_profile(
            {
                "profile_id": "bad",
                "model": "m",
                "served_model_name": "m",
                "host": "0.0.0.0",
                "port": 8001,
                "max_model_len": 32768,
                "gpu_memory_utilization": 0.9,
                "enable_auto_tool_choice": True,
                "tool_call_parser": "qwen3_coder",
                "performance_mode": "interactivity",
                "vllm_executable": "vllm",
                "optional_flags": {"block_size": 7},
            }
        )
