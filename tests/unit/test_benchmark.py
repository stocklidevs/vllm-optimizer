from pathlib import Path

import pytest

from vllm_optimizer.benchmark import (
    BenchmarkError,
    build_vllm_bin_path_export,
    build_benchmark_plan,
    load_prompt_set,
    metric_from_response,
    parse_remote_benchmark_output,
    summarize_metrics,
)
from vllm_optimizer.serve_profiles import load_serve_profile


def test_load_prompt_set_fixture() -> None:
    prompts = load_prompt_set(Path("config/prompts/qwen-baseline.json"))

    assert prompts.prompt_set_id == "qwen-baseline-v1"
    assert len(prompts.cases) == 3
    assert prompts.concurrency == 1


def test_load_workload_prompt_sets() -> None:
    prompt_paths = [
        Path("config/prompts/qwen-coding-interactive.json"),
        Path("config/prompts/qwen-coding-long.json"),
        Path("config/prompts/qwen-tool-json.json"),
    ]

    loaded = [load_prompt_set(path) for path in prompt_paths]

    assert [prompt.prompt_set_id for prompt in loaded] == [
        "qwen-coding-interactive-v1",
        "qwen-coding-long-v1",
        "qwen-tool-json-v1",
    ]
    assert all(len(prompt.cases) == 3 for prompt in loaded)
    assert loaded[1].cases[0].max_tokens > loaded[0].cases[0].max_tokens


def test_load_concurrent_prompt_set() -> None:
    prompts = load_prompt_set(Path("config/prompts/qwen-coding-interactive-concurrent.json"))

    assert prompts.prompt_set_id == "qwen-coding-interactive-concurrent-v1"
    assert prompts.concurrency == 3
    assert len(prompts.cases) == 3


def test_load_prompt_set_rejects_empty_cases(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"prompt_set_id":"bad","cases":[]}', encoding="utf-8")

    with pytest.raises(BenchmarkError, match="cases"):
        load_prompt_set(path)


def test_build_benchmark_plan_is_dry_run() -> None:
    profile = load_serve_profile(Path("config/profiles/qwen3-coder-next-awq.json"))
    prompts = load_prompt_set(Path("config/prompts/qwen-baseline.json"))

    plan = build_benchmark_plan(profile, prompts)

    assert plan["will_execute"] is False
    assert len(plan["request_sequence"]) == 3
    assert plan["concurrency"] == 1


def test_build_vllm_bin_path_export_adds_venv_bin_to_path() -> None:
    export = build_vllm_bin_path_export("$HOME/qwen3next-venv/bin/vllm")

    assert 'dirname "$HOME/qwen3next-venv/bin/vllm"' in export
    assert 'export PATH="$VLLM_BIN_DIR:$PATH"' in export


def test_build_vllm_bin_path_export_ignores_pathless_executable() -> None:
    assert build_vllm_bin_path_export("vllm") == ""


def test_summarize_metrics() -> None:
    summary = summarize_metrics(
        [
            {"status": "success", "duration_ms": 1000, "total_tokens": 10},
            {"status": "success", "duration_ms": 2000, "total_tokens": 20},
            {"status": "failed", "duration_ms": 50},
        ]
    )

    assert summary["success_count"] == 2
    assert summary["failure_count"] == 1
    assert summary["mean_latency_ms"] == 1500
    assert summary["total_tokens"] == 30
    assert summary["aggregate_tokens_per_second"] == 10


def test_summarize_metrics_uses_batch_duration_when_present() -> None:
    summary = summarize_metrics(
        [
            {"status": "success", "duration_ms": 1000, "batch_duration_ms": 2000, "total_tokens": 10},
            {"status": "success", "duration_ms": 2000, "batch_duration_ms": 2000, "total_tokens": 20},
        ]
    )

    assert summary["mean_latency_ms"] == 1500
    assert summary["aggregate_tokens_per_second"] == 15


def test_metric_from_response_extracts_usage() -> None:
    metric = metric_from_response(
        {
            "case_id": "ok",
            "duration_ms": 500,
            "exit_code": 0,
            "stdout": '{"usage":{"prompt_tokens":1,"completion_tokens":2,"total_tokens":3}}\nHTTP_STATUS:200\n',
        }
    )

    assert metric["status"] == "success"
    assert metric["tokens_per_second"] == 6


def test_metric_from_response_preserves_batch_duration() -> None:
    metric = metric_from_response(
        {
            "case_id": "ok",
            "duration_ms": 500,
            "batch_duration_ms": 900,
            "exit_code": 0,
            "stdout": '{"usage":{"total_tokens":3}}\nHTTP_STATUS:200\n',
        }
    )

    assert metric["batch_duration_ms"] == 900


def test_parse_remote_benchmark_output() -> None:
    parsed = parse_remote_benchmark_output(
        """
__VLLM_BENCHMARK_RESPONSES_START__
{"case_id":"ok","duration_ms":500,"exit_code":0,"stdout":"{\\"usage\\":{\\"total_tokens\\":3}}\\nHTTP_STATUS:200\\n","stderr":""}
__VLLM_BENCHMARK_CLEANUP_START__
{"cleaned":true,"ready":1,"pid":"123"}
__VLLM_BENCHMARK_LOG_START__
log
"""
    )

    assert parsed["cleanup"]["cleaned"] is True
    assert parsed["metrics"][0]["status"] == "success"
    assert parsed["server_log"] == "log"
