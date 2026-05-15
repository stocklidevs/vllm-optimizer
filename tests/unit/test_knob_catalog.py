from pathlib import Path

from vllm_optimizer.knob_catalog import build_knob_catalog, classify_group, render_knob_catalog_html


def test_classify_group_marks_risky_and_session_tuning() -> None:
    risky = classify_group(Path("config/sweeps/qwen-risky-session-small.json"))
    session = classify_group(Path("config/session-tuning-sweeps/qwen-runtime-env-sweep.json"))
    concurrency = classify_group(Path("config/sweeps/qwen-concurrency-saturation-c8.json"))

    assert risky["safety_tier"] == "risky-session"
    assert risky["requires_opt_in"] is True
    assert session["safety_tier"] == "session-tuning"
    assert session["command_kind"] == "session-tuning-sweep"
    assert concurrency["family"] == "concurrency"


def test_build_knob_catalog_includes_expected_families() -> None:
    catalog = build_knob_catalog(Path("config"))

    families = {group["family"] for group in catalog["groups"]}
    assert {"safe-vllm", "concurrency", "workload", "fp8", "session-tuning", "read-only-discovery"} <= families
    assert catalog["group_count"] == len(catalog["groups"])
    assert all("config_path" in group for group in catalog["groups"])


def test_render_knob_catalog_html_contains_groups_and_safety() -> None:
    html = render_knob_catalog_html(
        {
            "groups": [
                {
                    "id": "qwen-risky-session-small",
                    "label": "Qwen Risky Session Small",
                    "family": "risky-session",
                    "safety_tier": "risky-session",
                    "config_path": "config/sweeps/qwen-risky-session-small.json",
                    "command_kind": "sweep",
                    "requires_opt_in": True,
                    "description": "Risky session flags",
                }
            ]
        }
    )

    assert "Knob Group Selector" in html
    assert "Qwen Risky Session Small" in html
    assert "risky-session" in html
    assert "requires opt-in" in html
