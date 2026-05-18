from pathlib import Path

from vllm_optimizer.cockpit_launcher import CockpitLaunchRequest, prepare_cockpit_launch


def test_prepare_cockpit_launch_generates_default_artifacts(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "launcher-test" / tmp_path.name

    result = prepare_cockpit_launch(
        CockpitLaunchRequest(
            out_dir=out_dir,
            catalog_path=out_dir / "catalog" / "knob-groups.json",
            manifest_path=out_dir / "catalog" / "qwen-small-sweep-control.json",
            run_index_path=out_dir / "catalog" / "run-index.json",
        )
    )

    assert result["url"] == "http://127.0.0.1:8787"
    assert result["sweep_path"] == "config/sweeps/qwen-small-sweep.json"
    assert result["config_path"] in {
        "config/local.gx10.json",
        "config/gx10.example.json",
    }
    assert Path(result["catalog_path"]).exists()
    assert Path(result["manifest_path"]).exists()
    assert Path(result["run_index_path"]).exists()
    assert result["server_config"].sweep_path == Path("config/sweeps/qwen-small-sweep.json")
    assert result["server_config"].out_dir == out_dir


def test_prepare_cockpit_launch_accepts_sweep_override(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "launcher-override-test" / tmp_path.name
    sweep = Path("config/sweeps/qwen-prefix-prefill-tool-json.json")

    result = prepare_cockpit_launch(
        CockpitLaunchRequest(
            sweep_path=sweep,
            out_dir=out_dir,
            catalog_path=out_dir / "catalog" / "knob-groups.json",
            manifest_path=out_dir / "catalog" / "qwen-prefix-prefill-tool-json-control.json",
            run_index_path=out_dir / "catalog" / "run-index.json",
            port=8790,
        )
    )

    assert result["url"] == "http://127.0.0.1:8790"
    assert result["sweep_path"] == sweep.as_posix()
    assert result["group_id"] == "qwen-prefix-prefill-tool-json"
