from vllm_optimizer.web_cockpit import render_web_cockpit


def test_web_cockpit_renders_knobs_pipeline_status_and_report() -> None:
    html = render_web_cockpit(
        catalog={
            "groups": [
                {
                    "id": "qwen-prefix-prefill-tool-json",
                    "label": "Prefix Prefill Tool JSON",
                    "family": "workload",
                    "safety_tier": "safe-session",
                    "requires_opt_in": False,
                    "description": "Tool JSON prefill sweep.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/qwen-prefix-prefill-tool-json.json",
                }
            ]
        },
        manifest={
            "group": {"id": "qwen-prefix-prefill-tool-json", "label": "Prefix Prefill Tool JSON"},
            "stages": [
                {
                    "name": "run",
                    "remote": True,
                    "required_gates": ["--allow-risky-session-flags"],
                    "artifact": "ARTIFACT_DIR/live/results.jsonl",
                    "command_hint": "uv run vllm-optimizer optimize-workload --mode run",
                }
            ],
            "promotion": {"automatic": False, "required_gate": "--allow-promotion"},
        },
        status={
            "overall_status": "running",
            "trial_counts": {"completed": 2, "failed": 0, "total": 5},
            "artifacts": {"ranking": {"exists": True}},
        },
        report={
            "source": {"label": "tool-json"},
            "recommendation": {
                "status": "requires-confirmation",
                "objective": "balanced",
                "candidate_id": "candidate-1",
            },
            "candidates": {"candidate-1": {"metrics": {"aggregate_tokens_per_second": 96.5}}},
        },
        sources={
            "catalog": "artifacts/catalog/knob-groups.json",
            "manifest": "artifacts/catalog/control.json",
            "status": "artifacts/run/status.json",
            "report": "artifacts/reports/canonical-report.json",
        },
    )

    assert "vLLM Mission Control" in html
    assert "Prefix Prefill Tool JSON" in html
    assert "--allow-risky-session-flags" in html
    assert "--allow-promotion" in html
    assert "requires-confirmation" in html
    assert "disabled" in html
    assert "artifacts/catalog/knob-groups.json" in html


def test_web_cockpit_renders_empty_states_for_optional_artifacts() -> None:
    html = render_web_cockpit(catalog={"groups": []}, manifest=None, status=None, report=None)

    assert "No pipeline manifest loaded" in html
    assert "No execution status loaded" in html
    assert "No canonical report loaded" in html


def test_web_cockpit_includes_local_interaction_hooks() -> None:
    html = render_web_cockpit(
        catalog={
            "groups": [
                {
                    "id": "safe-a",
                    "label": "Safe A",
                    "family": "safe-vllm",
                    "safety_tier": "safe-session",
                    "requires_opt_in": False,
                    "description": "Safe sweep.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/safe-a.json",
                },
                {
                    "id": "risky-b",
                    "label": "Risky B",
                    "family": "risky-session",
                    "safety_tier": "risky-session",
                    "requires_opt_in": True,
                    "description": "Risky sweep.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/risky-b.json",
                },
            ]
        }
    )

    assert 'data-tab-target="knobs"' in html
    assert 'id="knob-search"' in html
    assert 'data-family-filter="safe-vllm"' in html
    assert 'data-family-filter="risky-session"' in html
    assert 'data-family="safe-vllm"' in html
    assert 'data-search="safe a safe-a safe-vllm safe-session safe sweep. sweep config/sweeps/safe-a.json"' in html
    assert 'id="visible-group-count"' in html
    assert 'id="group-empty-state"' in html
    assert "function applyGroupFilters()" in html
    assert "button disabled" in html


def test_web_cockpit_renders_report_visuals() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        report={
            "source": {"label": "visual-report"},
            "recommendation": {
                "status": "requires-confirmation",
                "objective": "balanced",
                "candidate_id": "candidate-fast",
                "rationale": ["Throughput: 100.000 tokens/sec.", "Failure rate: 0.000%."],
                "next_actions": ["Run repeated A/B confirmation before promotion."],
            },
            "candidates": {
                "candidate-fast": {
                    "recommendable": True,
                    "is_baseline": False,
                    "metrics": {
                        "aggregate_tokens_per_second": 100.0,
                        "mean_latency_ms": 900.0,
                        "failure_rate": 0.0,
                    },
                },
                "candidate-risky": {
                    "recommendable": False,
                    "exclusion_reason": "candidate has failed trials",
                    "metrics": {
                        "aggregate_tokens_per_second": 80.0,
                        "mean_latency_ms": 1200.0,
                        "failure_rate": 0.25,
                    },
                },
            },
        },
    )

    assert "Recommendation detail" in html
    assert "Metric visualizer" in html
    assert "Failure summary" in html
    assert "candidate-fast" in html
    assert "candidate-risky" in html
    assert "data-report-bar=\"throughput\"" in html
    assert "data-report-bar=\"latency\"" in html
    assert "25.000%" in html
    assert "candidate has failed trials" in html
    assert "Run repeated A/B confirmation before promotion." in html
