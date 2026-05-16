from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_cockpit_preview_writes_artifacts(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "cli-controller-test" / tmp_path.name
    result_path = tmp_path / "result.json"

    assert (
        main(
            [
                "cockpit-preview",
                "--sweep",
                "config/sweeps/qwen-prefix-prefill-tool-json.json",
                "--out-dir",
                str(out_dir),
                "--result-out",
                str(result_path),
            ]
        )
        == 0
    )

    result = read_json(result_path)
    assert result["action"] == "preview"
    assert Path(result["plan_path"]).exists()
    assert Path(result["preview_path"]).exists()


def test_cli_cockpit_run_requires_confirmation(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "cli-live-controller-test" / tmp_path.name

    assert (
        main(
            [
                "cockpit-run",
                "--sweep",
                "config/sweeps/qwen-small-sweep.json",
                "--config",
                "config/gx10.example.json",
                "--out-dir",
                str(out_dir),
            ]
        )
        == 2
    )
