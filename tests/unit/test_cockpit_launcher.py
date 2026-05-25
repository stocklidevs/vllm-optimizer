from pathlib import Path

from vllm_optimizer.cockpit_launcher import CockpitLaunchRequest, prepare_cockpit_launch


def test_prepare_cockpit_launch_generates_default_artifacts(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "launcher-test" / tmp_path.name

    result = prepare_cockpit_launch(
        CockpitLaunchRequest(
            out_dir=out_dir,
            catalog_path=out_dir / "catalog" / "knob-groups.json",
            run_index_path=out_dir / "catalog" / "run-index.json",
        )
    )

    assert result["url"] == "http://127.0.0.1:8787"
    assert result["sweep_path"] == "config/sweeps/qwen-concurrency-saturation-c8.json"
    assert result["group_id"] == "qwen-concurrency-saturation-c8"
    assert result["config_path"] in {
        "config/local.gx10.json",
        "config/gx10.example.json",
    }
    assert Path(result["catalog_path"]).exists()
    assert Path(result["manifest_path"]).exists()
    assert Path(result["run_index_path"]).exists()
    assert result["profile_paths"]
    assert result["server_config"].sweep_path == Path("config/sweeps/qwen-concurrency-saturation-c8.json")
    assert result["server_config"].out_dir == out_dir
    assert result["server_config"].profile_paths


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


def test_prepare_cockpit_launch_accepts_profile_overrides(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "launcher-profile-test" / tmp_path.name
    profile = Path("config/profiles/qwen3-coder-next-awq.json")

    result = prepare_cockpit_launch(
        CockpitLaunchRequest(
            out_dir=out_dir,
            catalog_path=out_dir / "catalog" / "knob-groups.json",
            manifest_path=out_dir / "catalog" / "qwen-small-sweep-control.json",
            run_index_path=out_dir / "catalog" / "run-index.json",
            profile_paths=(profile,),
        )
    )

    assert result["profile_paths"] == [profile.as_posix()]
    assert result["server_config"].profile_paths == (profile,)


def test_prepare_cockpit_launch_passes_promotion_gate(tmp_path: Path) -> None:
    out_dir = Path("artifacts") / "launcher-promotion-test" / tmp_path.name

    result = prepare_cockpit_launch(
        CockpitLaunchRequest(
            out_dir=out_dir,
            catalog_path=out_dir / "catalog" / "knob-groups.json",
            run_index_path=out_dir / "catalog" / "run-index.json",
            allow_promotion=True,
        )
    )

    assert result["allow_promotion"] is True
    assert result["server_config"].allow_promotion is True
