from pathlib import Path

from vllm_optimizer.serve_profiles import load_serve_profile
from vllm_optimizer.smoke import build_smoke_serve_plan, parse_remote_smoke_output


def test_build_smoke_serve_plan_is_dry_run() -> None:
    profile = load_serve_profile(Path("config/profiles/qwen3-coder-next-awq.json"))

    plan = build_smoke_serve_plan(profile)

    assert plan["will_execute"] is False
    assert "port 8001 must be free" in plan["preflight_checks"]
    assert plan["serve_command"][0] == "$HOME/qwen3next-venv/bin/vllm"


def test_parse_remote_smoke_output_sections() -> None:
    parsed = parse_remote_smoke_output(
        """
__VLLM_SMOKE_SUMMARY_START__
{"pid":"123","ready":1,"cleaned":true}
__VLLM_SMOKE_RESPONSE_START__
{"ok": true}
HTTP_STATUS:200
__VLLM_SMOKE_CLEANUP_START__
{"cleaned":true}
__VLLM_SMOKE_LOG_START__
server log
"""
    )

    assert parsed["summary"]["pid"] == "123"
    assert "HTTP_STATUS:200" in parsed["response"]["raw"]
    assert parsed["cleanup"]["cleaned"] is True
    assert parsed["server_log"] == "server log"
