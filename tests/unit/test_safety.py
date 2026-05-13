from pathlib import Path

from vllm_optimizer.experiments import load_experiment
from vllm_optimizer.planner import build_trial_plan
from vllm_optimizer.safety import build_dry_run_preview, is_allowed, render_vllm_params


def test_allowlist_blocks_unknown_commands() -> None:
    assert is_allowed("nvidia-smi --query-gpu=name")
    assert not is_allowed("sudo apt upgrade")


def test_render_vllm_params_is_sorted_and_cli_shaped() -> None:
    rendered = render_vllm_params(
        {"max_num_batched_tokens": 4096, "gpu_memory_utilization": 0.9}
    )

    assert rendered == "--gpu-memory-utilization 0.9 --max-num-batched-tokens 4096"


def test_dry_run_preview_contains_actions_without_blocking_fixture() -> None:
    experiment = load_experiment(Path("tests/fixtures/experiments/throughput.json"))
    plan = build_trial_plan(experiment)

    preview = build_dry_run_preview(plan)

    assert preview["execution_mode"] == "dry-run"
    assert preview["blocked_action_count"] == 0
    assert preview["actions"][0]["kind"] == "prepare-artifact-dir"
