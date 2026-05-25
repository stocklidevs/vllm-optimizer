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

    assert "vLLM Command Center" in html
    assert "Optimize for the outcome you care about." in html
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
    assert "Optimization Target" in html
    assert "Model/Profile" in html
    assert "Advanced tuning recipe" in html


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
    assert 'data-search="safe a safe-vllm safe-a safe-session safe sweep. sweep config/sweeps/safe-a.json"' in html
    assert 'id="visible-group-count"' in html
    assert 'id="group-empty-state"' in html
    assert "function applyGroupFilters()" in html
    assert "function selectObjectiveTarget" in html
    assert "function selectProfileCard" in html
    assert 'id="selected-objective-label"' in html
    assert 'id="auto-flow-selected-target"' in html
    assert "data-controller-command" in html
    assert "function openDetailPanel" in html


def test_web_cockpit_renders_model_profile_selector() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        profiles=[
            {
                "path": "config/profiles/model-a.json",
                "profile_id": "model-a-recommended",
                "model": "org/model-a",
                "served_model_name": "Model A",
                "tool_call_parser": "qwen3_coder",
                "optional_flags": {"max_num_seqs": 16},
                "role": "Recommended",
            }
        ],
    )

    assert "Model/Profile" in html
    assert "model-a-recommended" in html
    assert "Model A" in html
    assert "qwen3_coder" in html
    assert "max_num_seqs=16" in html
    assert 'data-profile-card' in html
    assert 'data-objective-target="performance"' in html
    assert 'data-objective-target="stability"' in html
    assert 'data-objective-target="tool_use"' in html


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
    assert 'id="pipeline-overall-progress-bar"' in html
    assert 'id="pipeline-overall-progress-label"' in html
    assert 'id="pipeline-caption"' in html
    assert 'id="next-action-headline"' in html
    assert 'id="next-action-button"' in html
    assert 'id="live-execution-progress-bar"' in html
    assert 'id="live-execution-title"' in html
    assert 'id="operation-cancel"' in html
    assert "I made the plan" in html
    assert "Click Preview to check if it is safe" in html
    assert "function renderOperationResult" in html
    assert "function updatePipelineFromJob" in html
    assert "function updateNextActionFromJob" in html
    assert "function resetWorkflowForNewOperation" in html
    assert "function setRunningOptimizationAction" in html
    assert "Prior run state has been cleared for this run" in html
    assert "Progress and stages now reflect this run" in html
    assert "progressLabel.textContent = '8%'" in html
    assert "progressLabel.textContent = progress + '%'" in html
    assert "Review Report" in html
    assert "tabJump" in html
    assert "refreshTab" in html
    assert "cockpit-tab-after-reload" in html
    assert "function safeSessionSet" in html
    assert "function safeSessionGet" in html
    assert "event.target.closest('[data-tab-jump]')" in html
    assert "completed_stages" in html
    assert "live-execution-title" in html
    assert "live-execution-elapsed" in html
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
    assert "Decision Story" in html
    assert "Current recommendation" in html
    assert "Improvement" in html
    assert "Performance Evidence" in html
    assert "Baseline vs Winner" in html
    assert "Latency / Throughput" in html
    assert "Stability Band" in html
    assert "Failure Heatmap" in html
    assert "Metric visualizer" in html
    assert "Failure summary" in html
    assert "Continue From Report" in html
    assert "Decision path" in html
    assert "Confirmation gate" in html
    assert "Open Promotion Gate" in html
    assert "optimize-workload --mode confirm" in html
    assert "candidate-fast" in html
    assert "candidate-risky" in html
    assert "data-report-bar=\"throughput\"" in html
    assert "data-report-bar=\"latency\"" in html
    assert "25.000%" in html
    assert "candidate has failed trials" in html
    assert "Run repeated A/B confirmation before promotion." in html


def test_web_cockpit_renders_premium_analytics_empty_state() -> None:
    html = render_web_cockpit(catalog={"groups": []}, report=None)

    assert "Decision Story" in html
    assert "Current recommendation" in html
    assert "Awaiting data" in html
    assert "Performance Evidence" in html
    assert "Waiting for report data" in html
    assert "No report yet" in html
    assert "baseline comparison, latency/throughput position" in html


def test_web_cockpit_renders_candidate_list_reports() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        report={
            "recommendation": {
                "status": "requires-confirmation",
                "objective": "throughput",
                "candidate_id": "candidate-list-fast",
            },
            "candidates": [
                {
                    "candidate_id": "candidate-list-baseline",
                    "is_baseline": True,
                    "metrics": {
                        "aggregate_tokens_per_second": 50.0,
                        "mean_latency_ms": 1200.0,
                        "failure_rate": 0.0,
                    },
                },
                {
                    "candidate_id": "candidate-list-fast",
                    "recommendable": True,
                    "metrics": {
                        "aggregate_tokens_per_second": 75.0,
                        "mean_latency_ms": 900.0,
                        "failure_rate": 0.0,
                    },
                },
            ],
        },
    )

    assert "candidate-list-fast" in html
    assert "+50.0%" in html
    assert "Performance Evidence" in html


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


def test_web_cockpit_renders_guided_mission_workflow() -> None:
    html = render_web_cockpit(
        catalog={
            "groups": [
                {
                    "id": "qwen-concurrency-c1",
                    "label": "Qwen Concurrency Saturation C1",
                    "family": "concurrency",
                    "safety_tier": "safe-session",
                    "requires_opt_in": False,
                    "description": "Concurrency sweep.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/qwen-concurrency-saturation-c1.json",
                }
            ]
        },
        manifest={
            "group": {"id": "qwen-concurrency-c1", "label": "Qwen Concurrency Saturation C1"},
            "stages": [
                {
                    "name": "plan",
                    "command_hint": "uv run vllm-optimizer optimize-workload --mode plan",
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

    assert "vLLM Command Center" in html
    assert 'class="objective-cockpit"' in html
    assert "Automatic Pipeline Progress" in html
    assert 'data-pipeline-stage="plan"' in html
    assert 'data-pipeline-stage="promote"' in html
    assert "Show knobs, commands, artifacts, runs, and gates" in html
    assert "Next action" in html
    assert "Start Optimization" in html
    assert "No execution" in html
    assert "Plans automatically" in html
    assert "Stops at real gates" in html
    assert "Artifact status and controller commands" in html


def test_web_cockpit_omits_old_right_rail_and_deprecated_panels() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        manifest={
            "stages": [
                {
                    "name": "run",
                    "command_hint": "uv run vllm-optimizer cockpit-run --confirm-live-run",
                    "required_gates": ["--confirm-live-run"],
                }
            ],
            "promotion": {"required_gate": "--allow-promotion"},
        },
    )

    assert '<aside class="right-rail">' not in html
    assert "Next action" in html
    assert "Live execution" in html
    assert "Safety Gates" not in html
    assert "<h2>Controller</h2>" not in html
    assert 'id="controller-feedback"' in html
    assert "Artifact status and controller commands" in html


def test_web_cockpit_uses_start_optimization_as_primary_cta() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        manifest={
            "stages": [
                {
                    "name": "plan",
                    "command_hint": "uv run vllm-optimizer optimize-workload --mode plan",
                },
                {
                    "name": "run",
                    "command_hint": "uv run vllm-optimizer cockpit-run --confirm-live-run",
                    "remote": True,
                    "required_gates": ["--confirm-live-run"],
                },
            ],
            "promotion": {"required_gate": "--allow-promotion"},
        },
    )

    assert '<aside class="right-rail">' not in html
    assert "Start Optimization" in html
    assert 'id="next-action-button"' in html
    assert 'data-controller-action="run"' in html
    assert 'data-controller-command="uv run vllm-optimizer cockpit-run --confirm-live-run"' in html
    assert "Runs plan and preview first" in html
    assert 'data-pipeline-stage="plan"' in html
    assert "Automatic Pipeline Progress" in html


def test_web_cockpit_overview_explains_end_to_end_flow() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        status={
            "overall_status": "completed",
            "trial_counts": {"completed": 4, "failed": 0, "total": 4},
        },
    )

    assert "Automatic Pipeline Progress" in html
    assert 'data-pipeline-stage="run"' in html
    assert 'data-pipeline-stage="report"' in html
    assert "Start Optimization" in html
    assert "Generate & Review Report" in html
    assert "Confirm Candidate" in html
    assert "Promote Profile" in html
    assert "Run complete. Reporting can be generated automatically." in html


def test_web_cockpit_report_ready_primary_action_reviews_report_not_confirm_endpoint() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        report={
            "recommendation": {
                "status": "requires-confirmation",
                "objective": "balanced",
                "candidate_id": "candidate-fast",
            }
        },
    )
    primary_card = html.split('<article class="command-panel primary-command-card">', 1)[1].split("</article>", 1)[0]

    assert "Review Report" in primary_card
    assert "Decision Story" in html
    assert "Report review" in html
    assert 'data-tab-jump="reports"' in primary_card
    assert 'data-controller-action="confirm"' not in primary_card
    assert 'data-controller-endpoint="/api/controller/confirm"' not in primary_card
    assert "No unsupported endpoint" in html


def test_web_cockpit_loaded_report_can_be_closed_or_replaced_with_new_run() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        manifest={
            "stages": [
                {
                    "name": "run",
                    "command_hint": "uv run vllm-optimizer cockpit-run --confirm-live-run",
                    "remote": True,
                    "required_gates": ["--confirm-live-run"],
                }
            ]
        },
        report={
            "recommendation": {
                "status": "requires-confirmation",
                "objective": "balanced",
                "candidate_id": "candidate-fast",
            }
        },
    )

    assert "Loaded run history" in html
    assert "Close Loaded Run" in html
    assert 'data-loaded-run-action="close"' in html
    assert "Start New Optimization" in html
    assert 'data-controller-action="run"' in html
    assert 'data-controller-endpoint="/api/controller/run"' in html
    assert 'data-controller-command="uv run vllm-optimizer cockpit-run --confirm-live-run"' in html
    assert "function closeLoadedRunHistory" in html
    assert "Loaded run closed. Ready to start a new optimization." in html
    assert "command-report-state" in html
    assert "Start a fresh optimization from the selected model, target, and tuning area." in html
    assert "Loaded run closed. Start New Optimization is ready." in html


def test_web_cockpit_loaded_history_close_keeps_future_report_loading_available() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        manifest={
            "stages": [
                {
                    "name": "run",
                    "command_hint": "uv run vllm-optimizer cockpit-run --confirm-live-run",
                },
                {
                    "name": "report",
                    "command_hint": "uv run vllm-optimizer cockpit-report",
                },
            ]
        },
        report={"recommendation": {"status": "requires-confirmation", "candidate_id": "candidate-fast"}},
    )

    assert "configureControllerButton(button, 'report', '/api/controller/report', reportCommand, 'Generate & Review Report')" in html
    assert "configureControllerButton(nextButton, 'run', '/api/controller/run', runCommand, 'Start Optimization')" in html
    assert "button.classList.remove('hidden')" in html
    assert "event.target.closest('[data-controller-command]')" in html
    assert "event.target.closest('[data-tab-jump]')" in html


def test_web_cockpit_one_click_report_review_and_single_main_action() -> None:
    html = render_web_cockpit(
        catalog={"groups": []},
        manifest={
            "stages": [
                {"name": "run", "command_hint": "uv run vllm-optimizer optimize-workload --mode run"},
                {"name": "report", "command_hint": "uv run vllm-optimizer optimize-workload --mode report"},
            ]
        },
        status={"overall_status": "completed", "trial_counts": {"completed": 4, "total": 4}},
    )

    assert "Generate & Review Report" in html
    assert "autoOpenReportAfterCompletion(job)" in html
    assert "Report opens automatically after generation" in html
    assert "recipe-action" not in html
    assert html.count('id="next-action-button"') == 1


def test_web_cockpit_renders_candidate_selection_and_gated_promotion_controls() -> None:
    report = {
        "recommendation": {
            "status": "requires-confirmation",
            "objective": "throughput",
            "candidate_id": "candidate-fast",
        },
        "candidates": [
            {
                "candidate_id": "candidate-safe",
                "metrics": {
                    "aggregate_tokens_per_second": 49.0,
                    "mean_latency_ms": 1000.0,
                    "failure_rate": 0.0,
                },
            },
            {
                "candidate_id": "candidate-fast",
                "metrics": {
                    "aggregate_tokens_per_second": 99.0,
                    "mean_latency_ms": 700.0,
                    "failure_rate": 0.0,
                },
            },
        ],
    }
    html = render_web_cockpit(
        catalog={"groups": []},
        manifest={"promotion": {"required_gate": "--allow-promotion"}},
        report=report,
        promotion_allowed=True,
    )

    assert "Select Candidate" in html
    assert 'data-candidate-select="candidate-fast"' in html
    assert 'data-candidate-select="candidate-safe"' in html
    assert 'data-selected-candidate-id="candidate-fast"' in html
    assert 'data-controller-action="promote"' in html
    assert 'data-controller-endpoint="/api/controller/promote"' in html
    assert "Promote Selected Candidate" in html
    assert "function selectPromotionCandidate" in html
    assert "payload.candidate_id = selectedCandidateId()" in html


def test_web_cockpit_tab_jump_false_does_not_reload() -> None:
    html = render_web_cockpit(catalog={"groups": []}, report={"recommendation": {}, "candidates": {}})

    assert 'data-tab-jump="promotion" data-refresh-tab="false"' in html
    assert "button.dataset.refreshTab === 'true'" in html


def test_web_cockpit_renders_selectable_tuning_areas() -> None:
    html = render_web_cockpit(
        catalog={
            "groups": [
                {
                    "id": "qwen-fp8-rerun-interactive",
                    "label": "Qwen FP8 Rerun Interactive",
                    "display_label": "FP8 KV Cache - Interactive Coding",
                    "display_family": "FP8 KV Cache",
                    "family": "fp8",
                    "safety_tier": "safe-session",
                    "requires_opt_in": False,
                    "description": "Explore FP8 cache dtype.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/qwen-fp8-rerun-interactive.json",
                    "knobs_tuned": ["kv_cache_dtype", "block_size"],
                },
                {
                    "id": "qwen-concurrency-saturation-c8",
                    "label": "Qwen Concurrency Saturation C8",
                    "display_label": "Concurrency - 8 Requests",
                    "display_family": "Concurrency",
                    "family": "concurrency",
                    "safety_tier": "safe-session",
                    "requires_opt_in": False,
                    "description": "Explore concurrency.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/qwen-concurrency-saturation-c8.json",
                    "knobs_tuned": ["request_concurrency", "max_num_seqs"],
                },
            ]
        }
    )

    assert "Tuning Areas" in html
    assert "Selected Tuning Area" in html
    assert "Included knobs" in html
    assert "FP8 KV Cache - Interactive Coding" in html
    assert "Concurrency - 8 Requests" in html
    assert 'data-tuning-area-id="qwen-fp8-rerun-interactive"' in html
    assert 'data-tuning-area-label="FP8 KV Cache - Interactive Coding"' in html
    assert 'data-knobs-tuned="kv_cache_dtype|block_size"' in html
    assert "function selectTuningArea" in html
    assert "Rerun Interactive" not in html


def test_web_cockpit_family_filters_left_rail_and_grid() -> None:
    html = render_web_cockpit(
        catalog={
            "groups": [
                {
                    "id": "safe-a",
                    "display_label": "Safe A",
                    "display_family": "Safe vLLM",
                    "family": "safe-vllm",
                    "safety_tier": "safe-session",
                    "requires_opt_in": False,
                    "description": "Safe sweep.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/safe-a.json",
                    "knobs_tuned": ["gpu_memory_utilization"],
                },
                {
                    "id": "risky-b",
                    "display_label": "Risky B",
                    "display_family": "Risky Session Flags",
                    "family": "risky-session",
                    "safety_tier": "risky-session",
                    "requires_opt_in": True,
                    "description": "Risky sweep.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/risky-b.json",
                    "knobs_tuned": ["risky_vllm_flags"],
                },
            ]
        }
    )

    assert 'class="mini-card tuning-area-option safe-session"' in html
    assert 'data-family="safe-vllm"' in html
    assert 'data-family="risky-session"' in html
    assert 'id="rail-empty-state"' in html
    assert "document.querySelectorAll('.group-card, .tuning-area-option')" in html
    assert "function syncSelectedTuningArea()" in html
    assert "selectTuningArea(firstVisible)" in html
    assert 'id="auto-flow-selected-area"' in html
    assert "autoFlowTarget.textContent = label" in html
    assert ".hidden { display: none !important; }" in html


def test_web_cockpit_renders_automatic_pipeline_progress() -> None:
    html = render_web_cockpit(
        catalog={
            "groups": [
                {
                    "id": "qwen-concurrency-c1",
                    "display_label": "Concurrency - 1 Request",
                    "display_family": "Concurrency",
                    "family": "concurrency",
                    "safety_tier": "safe-session",
                    "requires_opt_in": False,
                    "description": "Explore concurrency.",
                    "command_kind": "sweep",
                    "config_path": "config/sweeps/qwen-concurrency-saturation-c1.json",
                    "knobs_tuned": ["request_concurrency", "max_num_seqs"],
                }
            ]
        },
        manifest={
            "group": {"id": "qwen-concurrency-c1", "display_label": "Concurrency - 1 Request"},
            "stages": [
                {"name": "plan", "command_hint": "uv run vllm-optimizer optimize-workload --mode plan"},
                {"name": "preview", "command_hint": "uv run vllm-optimizer optimize-workload --mode preview"},
                {
                    "name": "run",
                    "command_hint": "uv run vllm-optimizer optimize-workload --mode run",
                    "remote": True,
                    "required_gates": ["--confirm-live-run"],
                },
                {"name": "report", "command_hint": "uv run vllm-optimizer optimize-workload --mode report"},
                {"name": "confirm", "command_hint": "uv run vllm-optimizer optimize-workload --mode confirm"},
                {"name": "promote", "command_hint": "uv run vllm-optimizer promote-confirmed-profile"},
            ],
            "promotion": {"automatic": False, "required_gate": "--allow-promotion"},
        },
        status={
            "overall_status": "running",
            "trial_counts": {"completed": 2, "failed": 0, "total": 5},
        },
    )

    assert "Start Optimization" in html
    assert "Automatic Pipeline Progress" in html
    assert "Overall progress" in html
    assert "Running trial 2 of 5" in html
    assert 'data-pipeline-stage="plan"' in html
    assert 'data-pipeline-stage="preview"' in html
    assert 'data-pipeline-stage="run"' in html
    assert "Manual gate" in html
    assert "Live GX10 execution" in html
    assert "--confirm-live-run" in html
    assert "Promotion remains manual" in html


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
    assert "Promote Selected Candidate" in html
    assert "Restart the cockpit with --allow-promotion" in html


def test_web_cockpit_renders_promotion_empty_state() -> None:
    html = render_web_cockpit(catalog={"groups": []}, manifest=None, report=None)

    assert 'data-tab-target="promotion"' in html
    assert "No promotion workflow loaded" in html
