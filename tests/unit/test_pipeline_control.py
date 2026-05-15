from vllm_optimizer.pipeline_control import (
    PipelineControlError,
    build_pipeline_control_manifest,
    render_pipeline_control_html,
)

import pytest


def test_pipeline_control_manifest_for_risky_sweep_has_opt_in_gate() -> None:
    manifest = build_pipeline_control_manifest(_catalog(), "risky")

    assert manifest["group"]["id"] == "risky"
    assert manifest["promotion"]["automatic"] is False
    run_stage = next(stage for stage in manifest["stages"] if stage["name"] == "run")
    assert run_stage["remote"] is True
    assert "--allow-risky-session-flags" in run_stage["required_gates"]
    assert len(manifest["stages"]) >= 4


def test_pipeline_control_manifest_for_read_only_discovery_has_no_promotion() -> None:
    manifest = build_pipeline_control_manifest(_catalog(), "discovery")

    assert [stage["name"] for stage in manifest["stages"]] == ["discover"]
    assert manifest["stages"][0]["remote"] is True
    assert manifest["promotion"]["available"] is False


def test_pipeline_control_manifest_rejects_unknown_group() -> None:
    with pytest.raises(PipelineControlError, match="group id not found"):
        build_pipeline_control_manifest(_catalog(), "missing")


def test_render_pipeline_control_html_contains_stages_and_gates() -> None:
    html = render_pipeline_control_html(build_pipeline_control_manifest(_catalog(), "session"))

    assert "Pipeline Control" in html
    assert "session-tuning-sweep-run" in html
    assert "--allow-session-tuning" in html


def _catalog() -> dict:
    return {
        "groups": [
            {
                "id": "safe",
                "label": "Safe Sweep",
                "family": "safe-vllm",
                "safety_tier": "safe-session",
                "config_path": "config/sweeps/qwen-small-sweep.json",
                "command_kind": "sweep",
                "requires_opt_in": False,
            },
            {
                "id": "risky",
                "label": "Risky Sweep",
                "family": "risky-session",
                "safety_tier": "risky-session",
                "config_path": "config/sweeps/qwen-risky-session-small.json",
                "command_kind": "sweep",
                "requires_opt_in": True,
            },
            {
                "id": "session",
                "label": "Session Tuning",
                "family": "session-tuning",
                "safety_tier": "session-tuning",
                "config_path": "config/session-tuning-sweeps/qwen-runtime-env-sweep.json",
                "command_kind": "session-tuning-sweep",
                "requires_opt_in": True,
            },
            {
                "id": "discovery",
                "label": "Discovery",
                "family": "read-only-discovery",
                "safety_tier": "read-only",
                "config_path": "config/local.gx10.json",
                "command_kind": "system-tuning-discover",
                "requires_opt_in": False,
            },
        ]
    }
