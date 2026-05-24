from pathlib import Path

from vllm_optimizer.artifacts import write_json
from vllm_optimizer.cli import main


def test_cli_web_cockpit_writes_standalone_html(tmp_path: Path) -> None:
    catalog = tmp_path / "knobs.json"
    manifest = tmp_path / "control.json"
    status = tmp_path / "status.json"
    report = tmp_path / "report.json"
    profile = tmp_path / "profile.json"
    html = tmp_path / "cockpit.html"
    write_json(
        catalog,
        {
            "groups": [
                {
                    "id": "safe",
                    "label": "Safe Sweep",
                    "family": "safe-vllm",
                    "safety_tier": "safe-session",
                    "requires_opt_in": False,
                    "description": "Safe sweep.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/qwen-small-sweep.json",
                }
            ]
        },
    )
    write_json(manifest, {"group": {"id": "safe"}, "stages": [], "promotion": {"automatic": False}})
    write_json(status, {"overall_status": "idle", "trial_counts": {"completed": 0, "failed": 0, "total": 0}})
    write_json(report, {"source": {"label": "safe"}, "recommendation": {"status": "keep-baseline"}, "candidates": {}})
    write_json(
        profile,
        {
            "profile_id": "fixture-profile",
            "model": "org/fixture",
            "served_model_name": "Fixture Model",
            "host": "0.0.0.0",
            "port": 8001,
            "vllm_executable": "vllm",
            "max_model_len": 32768,
            "gpu_memory_utilization": 0.9,
            "enable_auto_tool_choice": True,
            "tool_call_parser": "qwen3_coder",
            "performance_mode": "interactivity",
            "optional_flags": {"max_num_seqs": 16},
        },
    )

    assert (
        main(
            [
                "web-cockpit",
                "--catalog",
                str(catalog),
                "--manifest",
                str(manifest),
                "--status",
                str(status),
                "--report",
                str(report),
                "--profile",
                str(profile),
                "--out",
                str(html),
            ]
        )
        == 0
    )

    content = html.read_text(encoding="utf-8")
    assert "<!doctype html>" in content
    assert "vLLM Mission Control" in content
    assert "Safe Sweep" in content
    assert "Fixture Model" in content
    assert "Optimization Target" in content
