import re

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
    assert "data-controller-command" in html


def test_web_cockpit_controller_buttons_copy_commands() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        manifest={
            "stages": [
                {
                    "name": "preview",
                    "command_hint": "uv run vllm-optimizer cockpit-preview --sweep config/sweeps/qwen-small-sweep.json",
                },
                {
                    "name": "run",
                    "command_hint": "uv run vllm-optimizer cockpit-run --confirm-live-run",
                    "remote": True,
                    "required_gates": ["--confirm-live-run"],
                },
            ],
            "promotion": {"automatic": False, "required_gate": "--allow-promotion"},
        },
    )

    assert 'data-controller-action="preview"' in html
    assert 'data-controller-action="run"' in html
    assert 'data-controller-command="uv run vllm-optimizer cockpit-run --confirm-live-run"' in html
    assert 'id="controller-feedback"' in html
    assert "function copyControllerCommand" in html
    assert not re.search(r'<button[^>]+data-controller-action="run"[^>]+disabled', html)


def test_web_cockpit_renders_help_tooltips_and_how_to_use() -> None:
    html = render_web_cockpit(catalog={"groups": []})

    assert 'data-tab-target="how-to-use"' in html
    assert 'data-help-key="plan"' in html
    assert 'aria-label="What is Plan?"' in html
    assert 'aria-label="What is Preview?"' in html
    assert "How to Use" in html
    assert "Plan creates the deterministic run blueprint" in html
    assert "Preview validates the blueprint" in html


def test_web_cockpit_controller_buttons_have_active_api_hooks() -> None:
    html = render_web_cockpit(catalog={"groups": []})

    assert 'data-controller-endpoint="/api/controller/plan"' in html
    assert 'data-controller-endpoint="/api/controller/preview"' in html
    assert 'data-controller-endpoint="/api/controller/run"' in html
    assert "async function runControllerAction" in html
    assert "fetch(endpoint" in html


def test_web_cockpit_renders_operation_result_progress_and_cancel() -> None:
    html = render_web_cockpit(catalog={"groups": []})

    assert "Operation Result" in html
    assert 'id="operation-progress-bar"' in html
    assert 'id="operation-cancel"' in html
    assert "I made the plan" in html
    assert "Click Preview to check if it is safe" in html
    assert "function renderOperationResult" in html
    assert "async function pollControllerJob" in html
    assert "async function cancelControllerJob" in html


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


def test_web_cockpit_renders_run_browser_tab() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        run_index={
            "runs": [
                {
                    "run_id": "demo-live",
                    "relative_dir": "sweeps/demo/live",
                    "artifact_types": ["summary", "ranking"],
                    "artifact_paths": {
                        "summary": "artifacts/sweeps/demo/live/summary.json",
                        "ranking": "artifacts/sweeps/demo/live/ranking.json",
                    },
                    "modified_at": "2026-05-16T00:00:00Z",
                }
            ],
            "run_count": 1,
        },
    )

    assert 'data-tab-target="runs"' in html
    assert "Run browser" in html
    assert "demo-live" in html
    assert "artifacts/sweeps/demo/live/ranking.json" in html


def test_web_cockpit_renders_promotion_workflow() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        manifest={
            "promotion": {
                "automatic": False,
                "available": True,
                "required_gate": "--allow-promotion",
            }
        },
        report={
            "recommendation": {
                "status": "requires-confirmation",
                "objective": "balanced",
                "candidate_id": "candidate-promote",
            }
        },
    )

    assert 'data-tab-target="promotion"' in html
    assert "Promotion workflow" in html
    assert "candidate-promote" in html
    assert "requires-confirmation" in html
    assert "--allow-promotion" in html
    assert "promote-preview" in html
    assert "promote-confirmed-profile" in html
    assert "Promote disabled" in html


def test_web_cockpit_renders_promotion_empty_state() -> None:
    html = render_web_cockpit(catalog={"groups": []}, manifest=None, report=None)

    assert 'data-tab-target="promotion"' in html
    assert "No promotion workflow loaded" in html
