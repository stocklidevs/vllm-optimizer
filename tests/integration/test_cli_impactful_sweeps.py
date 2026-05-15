from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_kv_cache_memory_tradeoff_requires_risky_preview_opt_in(tmp_path: Path) -> None:
    plan = tmp_path / "kv-plan.json"
    preview = tmp_path / "kv-preview.json"

    assert main(["sweep-plan", "--sweep", "config/sweeps/qwen-kv-cache-memory-tradeoff.json", "--out", str(plan)]) == 0
    exit_code = main(["sweep-preview", "--plan", str(plan), "--out", str(preview)])

    data = read_json(preview)
    assert exit_code == 2
    assert data["blocked"] is True
    assert any("risky-session" in reason["reason"] for reason in data["blocked_reasons"])


def test_tool_json_prefill_sweep_plans_safe_candidates(tmp_path: Path) -> None:
    plan = tmp_path / "tool-plan.json"
    preview = tmp_path / "tool-preview.json"

    assert main(["sweep-plan", "--sweep", "config/sweeps/qwen-prefix-prefill-tool-json.json", "--out", str(plan)]) == 0
    assert main(["sweep-preview", "--plan", str(plan), "--out", str(preview)]) == 0

    data = read_json(plan)
    assert data["prompt_set_id"] == "qwen-tool-json-v1"
    assert data["candidate_count"] >= 4
    assert data["has_risky_session_flags"] is False
