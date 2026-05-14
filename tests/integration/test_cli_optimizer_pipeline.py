from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_optimize_workload_cli_preview_writes_pipeline_artifacts(tmp_path: Path) -> None:
    exit_code = main(
        [
            "optimize-workload",
            "--mode",
            "preview",
            "--sweep",
            "config/sweeps/qwen-small-sweep.json",
            "--out",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    summary = read_json(tmp_path / "pipeline-summary.json")
    assert summary["completed_stages"] == ["plan", "preview"]
    assert (tmp_path / "sweep-plan.json").exists()
    assert (tmp_path / "sweep-preview.json").exists()


def test_optimize_workload_cli_run_requires_config(tmp_path: Path) -> None:
    exit_code = main(
        [
            "optimize-workload",
            "--mode",
            "run",
            "--sweep",
            "config/sweeps/qwen-small-sweep.json",
            "--out",
            str(tmp_path),
        ]
    )

    assert exit_code == 2


def test_optimize_workload_cli_confirm_requires_inputs(tmp_path: Path) -> None:
    exit_code = main(
        [
            "optimize-workload",
            "--mode",
            "confirm",
            "--sweep",
            "config/sweeps/qwen-small-sweep.json",
            "--out",
            str(tmp_path),
        ]
    )

    assert exit_code == 2


def test_optimize_workload_cli_full_requires_config(tmp_path: Path) -> None:
    exit_code = main(
        [
            "optimize-workload",
            "--mode",
            "full",
            "--sweep",
            "config/sweeps/qwen-small-sweep.json",
            "--out",
            str(tmp_path),
            "--current-profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--prompts",
            "config/prompts/qwen-baseline.json",
            "--candidate-profile-out",
            str(tmp_path / "candidate.json"),
            "--confirmed-profile-out",
            str(tmp_path / "confirmed.json"),
        ]
    )

    assert exit_code == 2
