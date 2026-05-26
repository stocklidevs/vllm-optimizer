from pathlib import Path

from vllm_optimizer.serve_profiles import load_serve_profile
from vllm_optimizer.smoke import (
    build_remote_smoke_script,
    build_smoke_serve_plan,
    classify_smoke_summary,
    parse_remote_smoke_output,
)


def test_build_smoke_serve_plan_is_dry_run() -> None:
    profile = load_serve_profile(Path("config/profiles/qwen3-coder-next-awq.json"))

    plan = build_smoke_serve_plan(profile)

    assert plan["will_execute"] is False
    assert "port 8001 must be free" in plan["preflight_checks"]
    assert plan["serve_command"][0] == "$HOME/qwen3next-venv/bin/vllm"
    assert plan["readiness_categories"] == ["serve", "chat", "tool", "cleanup"]
    assert plan["tool_request"]["required"] is True


def test_parse_remote_smoke_output_sections() -> None:
    parsed = parse_remote_smoke_output(
        """
__VLLM_SMOKE_SUMMARY_START__
{"pid":"123","ready":1,"cleaned":true}
__VLLM_SMOKE_RESPONSE_START__
{"ok": true}
HTTP_STATUS:200
__VLLM_SMOKE_TOOL_RESPONSE_START__
{"choices":[{"message":{"tool_calls":[{"function":{"name":"report_status"}}]}}]}
HTTP_STATUS:200
__VLLM_SMOKE_CLEANUP_START__
{"cleaned":true}
__VLLM_SMOKE_LOG_START__
server log
"""
    )

    assert parsed["summary"]["pid"] == "123"
    assert "HTTP_STATUS:200" in parsed["response"]["raw"]
    assert "tool_calls" in parsed["tool_response"]["raw"]
    assert parsed["cleanup"]["cleaned"] is True
    assert parsed["server_log"] == "server log"


def test_classify_smoke_summary_requires_successful_readiness_for_chat_and_tools() -> None:
    profile = load_serve_profile(Path("config/profiles/qwen3-coder-next-awq.json"))
    summary = classify_smoke_summary(
        profile=profile,
        exit_code=1,
        stderr="",
        preflight={"safe": True},
        parsed={
            "summary": {"ready": 0, "cleaned": True},
            "response": {"raw": '{"ok":true}\nHTTP_STATUS:200'},
            "tool_response": {"raw": '{"choices":[{"message":{"tool_calls":[{}]}}]}\nHTTP_STATUS:200'},
            "cleanup": {"cleaned": True},
        },
        model_context={"model_id": "qwen3-coder-next-awq"},
        tool_probe_required=True,
    )

    assert summary["serve_ready"] is False
    assert summary["chat_ready"] is False
    assert summary["tool_ready"] == "failed"
    assert summary["status"] == "failed"


def test_remote_smoke_script_removes_stale_response_files_before_probing() -> None:
    profile = load_serve_profile(Path("config/profiles/qwen3-coder-next-awq.json"))

    script = build_remote_smoke_script(profile, timeout_seconds=30)

    assert "rm -f /tmp/vllm-smoke-response.json" in script
    assert "/tmp/vllm-smoke-tool-response.json" in script


def test_remote_smoke_script_exports_profile_environment() -> None:
    profile = load_serve_profile(Path("config/profiles/glm-4-7-flash.json"))

    script = build_remote_smoke_script(profile, timeout_seconds=30)

    assert "export HF_HOME=$HOME/.cache/huggingface-vllm-optimizer" in script
