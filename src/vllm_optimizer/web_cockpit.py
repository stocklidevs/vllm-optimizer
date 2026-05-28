from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from .artifacts import read_json


class WebCockpitError(ValueError):
    """Raised when the static web cockpit cannot be generated."""


def write_web_cockpit(
    catalog_path: Path,
    out_path: Path,
    *,
    manifest_path: Path | None = None,
    status_path: Path | None = None,
    report_path: Path | None = None,
    run_index_path: Path | None = None,
    profile_paths: list[Path] | tuple[Path, ...] | None = None,
    model_catalog_path: Path | None = None,
) -> dict[str, str]:
    if not catalog_path.exists():
        raise WebCockpitError(f"catalog path does not exist: {catalog_path}")
    catalog = read_json(catalog_path)
    manifest = _read_optional(manifest_path, "manifest")
    status = _read_optional(status_path, "status")
    report = _read_optional(report_path, "report")
    run_index = _read_optional(run_index_path, "run index")
    profiles = read_profile_summaries(profile_paths or [])
    profiles.extend(read_model_catalog_profile_summaries(model_catalog_path))
    html = render_web_cockpit(
        catalog,
        manifest=manifest,
        status=status,
        report=report,
        run_index=run_index,
        profiles=profiles,
        sources={
            "catalog": catalog_path.as_posix(),
            "manifest": manifest_path.as_posix() if manifest_path else None,
            "status": status_path.as_posix() if status_path else None,
            "report": report_path.as_posix() if report_path else None,
            "run_index": run_index_path.as_posix() if run_index_path else None,
            "profiles": ", ".join(path.as_posix() for path in profile_paths or []) or None,
            "model_catalog": model_catalog_path.as_posix() if model_catalog_path else None,
        },
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return {"html_path": out_path.as_posix(), "catalog_path": catalog_path.as_posix()}


def render_web_cockpit(
    catalog: dict[str, Any],
    *,
    manifest: dict[str, Any] | None = None,
    status: dict[str, Any] | None = None,
    report: dict[str, Any] | None = None,
    run_index: dict[str, Any] | None = None,
    profiles: list[dict[str, Any]] | None = None,
    promotion_allowed: bool = False,
    sources: dict[str, str | None] | None = None,
) -> str:
    groups = _list_of_dicts(catalog.get("groups"))
    families = sorted({str(group.get("family") or "unknown") for group in groups})
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>vLLM Command Center</title>",
            f"  <style>{CSS}</style>",
            "</head>",
            "<body>",
            '<main class="objective-cockpit">',
            render_objective_command_center(
                groups,
                families,
                manifest,
                status,
                report,
                run_index,
                profiles or [],
                sources or {},
                promotion_allowed=promotion_allowed,
            ),
            f"<script>{JS}</script>",
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def render_objective_command_center(
    groups: list[dict[str, Any]],
    families: list[str],
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
    run_index: dict[str, Any] | None,
    profiles: list[dict[str, Any]],
    sources: dict[str, str | None],
    *,
    promotion_allowed: bool = False,
) -> str:
    return f"""
    {render_command_topbar(status, report)}
    <section class="command-hero" aria-label="Objective command center">
      <div class="command-hero-copy">
        <h1>Optimize for the outcome you care about.</h1>
        <p>Pick the model, choose the objective, start the safe automatic run, then review the decision story. The tuning recipe is still there when you want to inspect every knob.</p>
      </div>
      {render_command_decision_card(report)}
    </section>
    {render_command_setup(groups, manifest, status, report, profiles)}
    {render_command_operations(groups, manifest, status, report)}
    {render_command_report_story(report)}
    {render_advanced_command_center(groups, families, manifest, status, report, run_index, sources, promotion_allowed=promotion_allowed)}
    """


def render_command_topbar(status: dict[str, Any] | None, report: dict[str, Any] | None) -> str:
    overall = str((status or {}).get("overall_status") or "idle")
    report_state = "report loaded" if report is not None else "no report"
    return f"""
    <header class="command-topbar">
      <div class="command-brand">
        <span class="command-orb" aria-hidden="true"></span>
        <div>
          <strong>vLLM Command Center</strong>
          <small>Deterministic GX10 optimizer</small>
        </div>
      </div>
      <div class="command-status-strip" aria-label="Loaded artifact state">
        <span id="command-status-overall">{escape(overall)}</span>
        <span id="command-report-state">{escape(report_state)}</span>
        <span>local controller ready</span>
      </div>
    </header>"""


def render_command_decision_card(report: dict[str, Any] | None) -> str:
    summary = report_outcome_summary(report)
    return f"""
      <aside class="decision-story-card" data-loaded-history>
        <span>Current recommendation</span>
        <strong><code>{escape(summary['winner_id'])}</code></strong>
        <dl>
          <div><dt>Lift</dt><dd class="{escape(summary['delta_class'])}">{escape(summary['improvement'])}</dd></div>
          <div><dt>Status</dt><dd>{escape(summary['decision'])}</dd></div>
        </dl>
        <p>{escape(summary['winner_detail'])}</p>
      </aside>
      <aside class="decision-story-card fresh-run-card hidden" data-fresh-run-state>
        <span>Ready for a new run</span>
        <strong>Fresh optimization</strong>
        <dl>
          <div><dt>Progress</dt><dd>0%</dd></div>
          <div><dt>Status</dt><dd>idle</dd></div>
        </dl>
        <p>Loaded run history is closed locally. Start a new optimization when you are ready.</p>
      </aside>"""


def render_command_setup(
    groups: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
    profiles: list[dict[str, Any]],
) -> str:
    profile_cards = "".join(render_profile_card(profile, index == 0) for index, profile in enumerate(profiles))
    if not profile_cards:
        profile_cards = """
        <article class="profile-card empty-profile">
          <span>No profiles loaded</span>
          <strong>Add --profile PROFILE.json</strong>
          <small>The optimizer can still run, but the page cannot show model context.</small>
        </article>"""
    target_cards = "".join(render_target_card(target, index == 0) for index, target in enumerate(OPTIMIZATION_TARGETS))
    selected = selected_group_label(groups, manifest)
    description = selected_group_description(groups, manifest) or "The optimizer chooses candidates from the deterministic recipe."
    return f"""
    <section class="command-setup-grid" aria-label="Optimization setup">
      <article class="command-panel model-panel">
        <div class="command-section-head">
          <span>Model/Profile</span>
          <strong>Which model are we tuning?</strong>
        </div>
        <div class="profile-strip">{profile_cards}</div>
      </article>
      <article class="command-panel objective-panel">
        <div class="command-section-head">
          <span>Optimization Target</span>
          <strong>Best tweak for...</strong>
        </div>
        <div class="target-grid">{target_cards}</div>
        <div class="selected-objective-summary">
          <span>Selected</span>
          <strong id="selected-objective-label">Balanced</strong>
          <small id="selected-objective-description">Blend throughput, latency, failure rate, and safety.</small>
        </div>
      </article>
      <article class="command-panel recipe-panel">
        <div class="command-section-head">
          <span>Selected Tuning Area</span>
          <strong id="selected-tuning-area-label">{escape(selected)}</strong>
        </div>
        <p id="selected-tuning-area-description">{escape(description)}</p>
        <dl class="recipe-facts">
          <div><dt>Target</dt><dd id="auto-flow-selected-target">Balanced</dd></div>
          <div><dt>Tuning area</dt><dd id="auto-flow-selected-area">{escape(selected)}</dd></div>
        </dl>
        <div class="knobs-tuned-panel compact-knobs">
          <strong>Included knobs</strong>
          <ul id="selected-knobs-tuned">{render_selected_knob_items(groups, manifest)}</ul>
        </div>
        {render_loaded_run_controls(manifest, status, report)}
      </article>
    </section>"""


def render_command_operations(
    groups: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    action = current_workflow_action(status, report)
    primary = primary_cockpit_action(action)
    progress = pipeline_progress(status, report)
    rows = "".join(render_pipeline_progress_stage(stage, status, report) for stage in WORKFLOW_STEPS)
    facts = "".join(f"<li>{escape(item)}</li>" for item in primary["facts"])
    return f"""
    <section class="command-runway" aria-label="Optimization execution">
      <article class="command-panel primary-command-card">
        <div class="command-section-head">
          <span>Next action</span>
          <strong id="next-action-headline">{escape(primary['headline'])}</strong>
        </div>
        <p id="next-action-description">{escape(primary['description'])}</p>
        <ul id="next-action-facts" class="fact-list compact">{facts}</ul>
        {render_primary_action_button(primary, manifest, button_id="next-action-button")}
        {render_loaded_run_controls(manifest, status, report, compact=True)}
        <p id="controller-feedback" class="controller-feedback" aria-live="polite">Ready to run the selected objective from the cockpit server.</p>
      </article>
      <article class="command-panel progress-command-card">
        <div class="command-section-head progress-head">
          <span>Execution Pipeline</span>
          <em>Automatic Pipeline Progress</em>
          <strong id="pipeline-overall-progress-label">{progress}%</strong>
        </div>
        <div class="progress-track overall-progress" aria-label="Overall progress">
          <div id="pipeline-overall-progress-bar" class="progress-bar" style="width:{progress}%"></div>
        </div>
        <p id="pipeline-caption" class="progress-caption">{escape(pipeline_caption(status, report))}</p>
        <div class="command-stage-list">{rows}</div>
        <div class="command-gates">{render_human_gate_summary(manifest)}</div>
      </article>
      <article class="command-panel live-command-card">
        <div class="command-section-head">
          <span>Live execution</span>
          <strong>Operation Monitor</strong>
        </div>
        {render_live_execution_summary(status)}
        {render_operation_result_panel()}
      </article>
    </section>"""


def render_command_report_story(report: dict[str, Any] | None) -> str:
    summary = report_outcome_summary(report)
    rows = _candidate_metric_rows(report.get("candidates", {}) if isinstance(report, dict) else {})
    winner = summary.get("winner_row")
    baseline = summary.get("baseline_row")
    best_failure = _fmt_pct(winner["failure_rate"]) if isinstance(winner, dict) else "n/a"
    baseline_tps = _fmt(baseline["throughput"]) if isinstance(baseline, dict) else "n/a"
    winner_tps = _fmt(winner["throughput"]) if isinstance(winner, dict) else "n/a"
    return f"""
    <section class="decision-story" aria-label="Decision story" data-loaded-history>
      <div class="story-heading">
        <h2>Decision Story</h2>
        <p>Baseline, winner, confidence, and next action from the loaded canonical report.</p>
      </div>
      <div class="story-grid">
        <article>
          <span>Baseline</span>
          <strong>{escape(baseline_tps)} tok/s</strong>
          <small>{escape(summary['baseline_detail'])}</small>
        </article>
        <article class="winner-story">
          <span>Winner</span>
          <strong>{escape(winner_tps)} tok/s</strong>
          <small><code>{escape(summary['winner_id'])}</code></small>
        </article>
        <article>
          <span>Improvement</span>
          <strong class="{escape(summary['delta_class'])}">{escape(summary['improvement'])}</strong>
          <small>{escape(summary['decision_detail'])}</small>
        </article>
        <article>
          <span>Risk</span>
          <strong>{escape(best_failure)}</strong>
          <small>{escape(str(len(rows)))} candidates in report</small>
        </article>
      </div>
    </section>"""


def render_loaded_run_controls(
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
    *,
    compact: bool = False,
) -> str:
    if not is_loaded_artifact_state(status, report):
        return ""
    command = controller_commands(manifest).get("run", controller_commands(manifest).get("plan", ""))
    density = " compact" if compact else ""
    return f"""
    <div class="loaded-run-controls{density}">
      <span>Loaded run history</span>
      <div>
        <button type="button" class="secondary-action" data-loaded-run-action="close">Close Loaded Run</button>
        <button type="button" class="primary-action" data-controller-action="run" data-controller-endpoint="/api/controller/run" data-controller-command="{escape(command)}">Start New Optimization</button>
      </div>
    </div>"""


def render_advanced_command_center(
    groups: list[dict[str, Any]],
    families: list[str],
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
    run_index: dict[str, Any] | None,
    sources: dict[str, str | None],
    *,
    promotion_allowed: bool = False,
) -> str:
    return f"""
    <section class="advanced-command-center" aria-label="Advanced optimizer details">
      <details class="advanced-shell" id="advanced-cockpit-details">
        <summary>
          <span>Advanced tuning recipe</span>
          <strong>Show knobs, commands, artifacts, runs, and gates</strong>
        </summary>
        <div class="advanced-layout">
          <aside class="advanced-rail">
            {render_family_filter_controls(families)}
            {render_tuning_area_options(groups)}
          </aside>
          <div class="advanced-workspace">
            {render_tabs()}
            {render_advanced_summary_panel(manifest, status, report)}
            {render_advanced_tuning_panel(groups)}
            {render_pipeline(manifest)}
            {render_runs(run_index)}
            {render_performance_evidence(report)}
            {render_reporting(report, manifest, promotion_allowed=promotion_allowed)}
            {render_promotion_workflow(report, manifest, promotion_allowed=promotion_allowed)}
            {render_how_to_use()}
            {render_sources(sources)}
          </div>
        </div>
      </details>
    </section>"""


def render_advanced_summary_panel(
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    return f"""
    <section class="panel tab-panel active" id="overview" data-tab-panel="overview">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Advanced Overview</p>
          <h2>Artifact status and controller commands</h2>
        </div>
        <p>Use this view when you want the exact deterministic inputs behind the objective flow.</p>
      </div>
      <div class="flow-context">
        {render_status_summary(status)}
        {render_report_summary(report)}
      </div>
      {render_disabled_actions(manifest)}
    </section>"""


def render_advanced_tuning_panel(groups: list[dict[str, Any]]) -> str:
    return f"""
    <section class="panel tab-panel" id="knobs" data-tab-panel="knobs">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Tuning Areas</p>
          <h2>Advanced recipe controls</h2>
        </div>
        <p><span id="visible-group-count">{len(groups)}</span> of {len(groups)} tuning areas visible from the deterministic catalog.</p>
      </div>
      <div class="filter-bar">
        <label for="knob-search">Search tuning areas</label>
        <input id="knob-search" type="search" placeholder="Search by name, family, safety, or config">
      </div>
      <div class="group-grid">{''.join(render_group_card(group) for group in groups) or '<p class="empty">No tuning areas loaded.</p>'}</div>
      <p class="empty hidden" id="group-empty-state">No tuning areas match the current filter.</p>
    </section>"""


def render_family_filter_controls(families: list[str]) -> str:
    family_items = "".join(
        f'<button type="button" data-family-filter="{escape(family)}">{escape(family)}</button>' for family in families
    ) or '<span class="empty">No families</span>'
    return f"""
    <nav class="family-nav advanced-family-nav" aria-label="Tuning area family filters">
      <button type="button" class="active" data-family-filter="all">All families</button>
      {family_items}
    </nav>"""


def render_tuning_area_options(groups: list[dict[str, Any]]) -> str:
    group_items = []
    for group in groups:
        group_items.append(
            f"""
            <button type="button" class="mini-card tuning-area-option {escape(str(group.get('safety_tier') or 'unknown'))}" data-family="{escape(str(group.get('family') or 'unknown'))}" data-search="{escape(group_search_text(group))}" data-tuning-area-id="{escape(str(group.get('id') or ''))}" data-tuning-area-label="{escape(group_label(group))}" data-tuning-area-family="{escape(group_display_family(group))}" data-tuning-area-safety="{escape(str(group.get('safety_tier') or 'unknown'))}" data-tuning-area-description="{escape(str(group.get('description') or 'No description.'))}" data-tuning-area-config="{escape(str(group.get('config_path') or 'n/a'))}" data-knobs-tuned="{escape('|'.join(group_knobs(group)))}">
              <strong>{escape(group_label(group))}</strong>
              <span>{escape(str(group.get('safety_tier') or 'unknown'))}</span>
            </button>"""
        )
    return f"""
    <div class="rail-section advanced-recipe-list">
      <h2>Tuning Areas</h2>
      {''.join(group_items) or '<p class="empty">No tuning areas loaded.</p>'}
      <p class="empty hidden" id="rail-empty-state">No tuning areas match this family.</p>
    </div>"""


def render_left_rail(families: list[str], groups: list[dict[str, Any]]) -> str:
    family_items = "".join(
        f'<button type="button" data-family-filter="{escape(family)}">{escape(family)}</button>' for family in families
    ) or '<span class="empty">No families</span>'
    group_items = []
    for group in groups:
        group_items.append(
            f"""
            <button type="button" class="mini-card tuning-area-option {escape(str(group.get('safety_tier') or 'unknown'))}" data-family="{escape(str(group.get('family') or 'unknown'))}" data-search="{escape(group_search_text(group))}" data-tuning-area-id="{escape(str(group.get('id') or ''))}" data-tuning-area-label="{escape(group_label(group))}" data-tuning-area-family="{escape(group_display_family(group))}" data-tuning-area-safety="{escape(str(group.get('safety_tier') or 'unknown'))}" data-tuning-area-description="{escape(str(group.get('description') or 'No description.'))}" data-tuning-area-config="{escape(str(group.get('config_path') or 'n/a'))}" data-knobs-tuned="{escape('|'.join(group_knobs(group)))}">
              <strong>{escape(group_label(group))}</strong>
              <span>{escape(str(group.get('safety_tier') or 'unknown'))}</span>
            </button>"""
        )
    return f"""
    <aside class="left-rail">
      <div class="brand">
        <span class="pulse"></span>
        <div><strong>vLLM</strong><small>Optimizer</small></div>
      </div>
      <nav class="family-nav" aria-label="Tuning area family filters">
        <button type="button" class="active" data-family-filter="all">All families</button>
        {family_items}
      </nav>
      <div class="rail-section">
        <h2>Tuning Areas</h2>
        {''.join(group_items) or '<p class="empty">No tuning areas loaded.</p>'}
        <p class="empty hidden" id="rail-empty-state">No tuning areas match this family.</p>
      </div>
    </aside>"""


def render_hero(groups: list[dict[str, Any]], status: dict[str, Any] | None, report: dict[str, Any] | None) -> str:
    overall = str((status or {}).get("overall_status") or "read-only")
    recommendation = (report or {}).get("recommendation", {}) if isinstance((report or {}).get("recommendation"), dict) else {}
    return f"""
    <header class="hero">
      <div>
        <p class="eyebrow">GX10 Optimization Cockpit</p>
        <h1>vLLM Mission Control</h1>
        <p class="hero-copy">Select tuning areas, inspect safety gates, monitor artifact progress, and review optimization outcomes from one deterministic cockpit.</p>
      </div>
      <div class="hero-grid">
        {metric_tile("Tuning Areas", len(groups), "catalog entries")}
        {metric_tile("Status", overall, "execution")}
        {metric_tile("Decision", recommendation.get("status", "no report"), "report")}
      </div>
    </header>"""


def render_tabs() -> str:
    return """
    <div class="tabs" aria-label="Cockpit sections">
      <button type="button" class="active" data-tab-target="overview">Overview</button>
      <button type="button" data-tab-target="knobs">Tuning Areas</button>
      <button type="button" data-tab-target="pipeline">Pipeline</button>
      <button type="button" data-tab-target="runs">Runs</button>
      <button type="button" data-tab-target="reports">Reports</button>
      <button type="button" data-tab-target="promotion">Promotion</button>
      <button type="button" data-tab-target="how-to-use">How to Use</button>
      <button type="button" data-tab-target="sources">Sources</button>
    </div>"""


def render_workflow(
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    current = current_workflow_action(status, report)
    current_index = workflow_index(current)
    loaded_state = is_loaded_artifact_state(status, report)
    steps = []
    for index, step in enumerate(WORKFLOW_STEPS, start=1):
        action = step["action"]
        if action == current:
            state = "active"
            label = "Review" if loaded_state else "Ready"
        elif index < current_index:
            state = "complete"
            label = "Loaded" if loaded_state else "Done"
        else:
            state = "locked"
            label = workflow_locked_label(action, manifest)
        steps.append(
            f"""
            <article class="workflow-step {state}" data-workflow-step="{escape(action)}">
              <span class="step-index">{index}</span>
              <strong>{escape(step['label'])}</strong>
              <small>{escape(label)}</small>
            </article>"""
        )
    return f"""
    <section class="workflow-band" aria-label="Optimization workflow">
      <div class="workflow-heading">
        <h2>{'Loaded Artifact State' if loaded_state else 'Optimization Workflow'}</h2>
        <span>Step {current_index} of {len(WORKFLOW_STEPS)}</span>
      </div>
      <div class="workflow-steps">{''.join(steps)}</div>
    </section>"""


def render_overview(
    groups: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    return f"""
    <section class="panel tab-panel active" id="overview" data-tab-panel="overview">
      {render_performance_evidence(report)}
      {render_guided_step_workspace(groups, manifest, status, report)}
      {render_end_to_end_flow_map(status, report)}
      {render_operation_result_panel()}
      {render_disabled_actions(manifest)}
    </section>
    <section class="panel tab-panel" id="knobs" data-tab-panel="knobs">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Tuning Areas</p>
          <h2>Optimization areas</h2>
        </div>
        <p><span id="visible-group-count">{len(groups)}</span> of {len(groups)} tuning areas visible from the deterministic catalog.</p>
      </div>
      <div class="filter-bar">
        <label for="knob-search">Search tuning areas</label>
        <input id="knob-search" type="search" placeholder="Search by name, family, safety, or config">
      </div>
      <div class="group-grid">{''.join(render_group_card(group) for group in groups) or '<p class="empty">No tuning areas loaded.</p>'}</div>
      <p class="empty hidden" id="group-empty-state">No tuning areas match the current filter.</p>
    </section>"""


def render_decision_strip(
    groups: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    summary = report_outcome_summary(report)
    action = current_workflow_action(status, report)
    primary = primary_cockpit_action(action)
    selected = selected_group_label(groups, manifest)
    return f"""
      <section class="decision-strip" aria-label="Decision Strip">
        <article class="decision-cell selected">
          <span>Selected Workload</span>
          <strong>{escape(selected)}</strong>
          <small>{escape(selected_group_description(groups, manifest) or "Catalog-driven tuning area.")}</small>
        </article>
        <article class="decision-cell winner">
          <span>Current Winner</span>
          <strong><code>{escape(summary['winner_id'])}</code></strong>
          <small>{escape(summary['winner_detail'])}</small>
        </article>
        <article class="decision-cell improvement">
          <span>Improvement vs Baseline</span>
          <strong class="{escape(summary['delta_class'])}">{escape(summary['improvement'])}</strong>
          <small>{escape(summary['baseline_detail'])}</small>
        </article>
        <article class="decision-cell safety">
          <span>Safety Decision</span>
          <strong>{escape(summary['decision'])}</strong>
          <small>{escape(summary['decision_detail'])}</small>
        </article>
        <article class="decision-cell target">
          <span>Optimization Target</span>
          <strong id="selected-objective-label">Balanced</strong>
          <small id="selected-objective-description">Blend throughput, latency, failure rate, and safety.</small>
        </article>
        <article class="decision-cell next">
          <span>Next Safe Action</span>
          <strong>{escape(primary['label'])}</strong>
          <small>{escape(primary['next'])}</small>
        </article>
      </section>"""


def render_model_objective_panel(profiles: list[dict[str, Any]]) -> str:
    profile_cards = "".join(render_profile_card(profile, index == 0) for index, profile in enumerate(profiles))
    if not profile_cards:
        profile_cards = """
          <article class="profile-card empty-profile">
            <span>No profiles loaded</span>
            <strong>Add --profile PROFILE.json</strong>
            <small>The cockpit can still run, but model selection is not available for this page.</small>
          </article>"""
    target_cards = "".join(render_target_card(target, index == 0) for index, target in enumerate(OPTIMIZATION_TARGETS))
    return f"""
      <section class="model-objective-panel" aria-label="Model and optimization target selection">
        <div class="model-selector">
          <div class="section-heading compact-heading">
            <div>
              <p class="eyebrow">Model Selection</p>
              <h2>Model/Profile</h2>
            </div>
            <p>Profiles define model identity, parser settings, readiness state, and promoted serve knobs.</p>
          </div>
          <div class="profile-strip">{profile_cards}</div>
        </div>
        <div class="target-selector">
          <div class="section-heading compact-heading">
            <div>
              <p class="eyebrow">Optimization Target</p>
              <h2>Best tweak for...</h2>
            </div>
            <p>This selection is local UI state until target-aware scoring is wired into planning.</p>
          </div>
          <div class="target-grid">{target_cards}</div>
        </div>
      </section>"""


def render_profile_card(profile: dict[str, Any], active: bool) -> str:
    optional = profile.get("optional_flags", {}) if isinstance(profile.get("optional_flags"), dict) else {}
    knob_summary = ", ".join(f"{key}={value}" for key, value in sorted(optional.items())) or "base serve flags"
    role = str(profile.get("role") or profile.get("support_status") or "Profile")
    label = str(profile.get("display_name") or profile.get("profile_id") or "unknown-profile")
    readiness = str(profile.get("support_status") or profile.get("promotion_status") or "profile")
    return f"""
          <button type="button" class="profile-card {'active' if active else ''}" data-profile-card data-profile-id="{escape(str(profile.get('profile_id') or 'profile'))}">
            <span>{escape(role)}</span>
            <strong>{escape(label)}</strong>
            <small>{escape(str(profile.get('served_model_name') or profile.get('model') or 'unknown model'))}</small>
            <code>{escape(str(profile.get('path') or 'n/a'))}</code>
            <em>{escape(str(profile.get('tool_call_parser') or profile.get('tool_support') or 'no parser'))} / {escape(readiness)} / {escape(knob_summary)}</em>
          </button>"""


def render_target_card(target: dict[str, str], active: bool) -> str:
    return f"""
          <button type="button" class="target-card {'active' if active else ''}" data-objective-target="{escape(target['id'])}" data-target-label="{escape(target['label'])}" data-target-description="{escape(target['description'])}">
            <span>{escape(target['label'])}</span>
            <strong>{escape(target['headline'])}</strong>
            <small>{escape(target['description'])}</small>
          </button>"""


def render_performance_evidence(report: dict[str, Any] | None) -> str:
    rows = _candidate_metric_rows(report.get("candidates", {}) if isinstance(report, dict) else {})
    if not rows:
        return """
      <section class="evidence-panel" aria-label="Performance Evidence">
        <div class="section-heading compact-heading">
          <div>
            <p class="eyebrow">Performance Evidence</p>
            <h2>Waiting for report data</h2>
          </div>
          <p>No canonical report loaded yet.</p>
        </div>
        <div class="evidence-empty">
          <strong>No report yet</strong>
          <p>Run or load a report to populate baseline comparison, latency/throughput position, stability context, and failure heatmap.</p>
        </div>
      </section>"""
    summary = report_outcome_summary(report)
    baseline = summary["baseline_row"]
    winner = summary["winner_row"]
    max_tps = max((row["throughput"] or 0 for row in rows), default=0) or 1
    max_latency = max((row["latency"] or 0 for row in rows), default=0) or 1
    bar_rows = render_evidence_bar("Baseline", baseline, max_tps) + render_evidence_bar("Winner", winner, max_tps)
    scatter_dots = "".join(render_scatter_dot(row, max_tps, max_latency, summary["winner_id"]) for row in rows)
    stability_rows = "".join(render_stability_row(row) for row in rows)
    heatmap_cells = "".join(render_heatmap_cell(row) for row in rows)
    return f"""
      <section class="evidence-panel" aria-label="Performance Evidence">
        <div class="section-heading compact-heading">
          <div>
            <p class="eyebrow">Performance Evidence</p>
            <h2>Report-backed performance map</h2>
          </div>
          <p>Canonical report metrics rendered as decision evidence; winner selection still belongs to the report artifact.</p>
        </div>
        <div class="evidence-grid">
          <article class="chart-card bar-comparison">
            <div class="chart-head"><strong>Baseline vs Winner</strong><span>tokens/sec</span></div>
            <div class="comparison-bars">{bar_rows}</div>
          </article>
          <article class="chart-card">
            <div class="chart-head"><strong>Latency / Throughput</strong><span>higher and left is better</span></div>
            <div class="scatter-plot" data-chart="latency-throughput">{scatter_dots}</div>
            <div class="axis-row"><span>lower latency</span><span>higher throughput</span></div>
          </article>
          <article class="chart-card">
            <div class="chart-head"><strong>Stability Band</strong><span>failure context</span></div>
            <div class="stability-list">{stability_rows}</div>
          </article>
          <article class="chart-card">
            <div class="chart-head"><strong>Failure Heatmap</strong><span>candidate risk</span></div>
            <div class="failure-heatmap">{heatmap_cells}</div>
          </article>
        </div>
      </section>"""


def render_pipeline(manifest: dict[str, Any] | None) -> str:
    if manifest is None:
        body = '<p class="empty">No pipeline manifest loaded.</p>'
        safety = ""
    else:
        stages = _list_of_dicts(manifest.get("stages"))
        rows = []
        for stage in stages:
            rows.append(
                f"""
                <tr>
                  <td>{escape(str(stage.get('name') or 'stage'))}</td>
                  <td>{'remote' if stage.get('remote') else 'local'}</td>
                  <td>{render_gate_list(stage.get('required_gates'))}</td>
                  <td><code>{escape(str(stage.get('artifact') or 'n/a'))}</code></td>
                </tr>"""
            )
        body = f"""
        <table>
          <thead><tr><th>Stage</th><th>Scope</th><th>Required gates</th><th>Artifact</th></tr></thead>
          <tbody>{''.join(rows) or '<tr><td colspan="4">No stages defined.</td></tr>'}</tbody>
        </table>"""
        promotion = manifest.get("promotion", {}) if isinstance(manifest.get("promotion"), dict) else {}
        safety = f"<p class=\"safety-note\">Promotion automatic: <strong>{escape(str(promotion.get('automatic', False)))}</strong>. Gate: <code>{escape(str(promotion.get('required_gate') or '--allow-promotion'))}</code>.</p>"
    return f"""
    <section class="panel tab-panel" id="pipeline" data-tab-panel="pipeline">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Pipeline</p>
          <h2>Operation stages</h2>
        </div>
        <p>Stages and gates come from the pipeline control manifest.</p>
      </div>
      {body}
      {safety}
    </section>"""


def render_reporting(
    report: dict[str, Any] | None,
    manifest: dict[str, Any] | None = None,
    *,
    promotion_allowed: bool = False,
) -> str:
    if report is None:
        content = """
        <div class="report-card">
          <p class="empty">No canonical report loaded.</p>
          <p>After an optimization run finishes, use <strong>Generate &amp; Review Report</strong> to generate and open the decision artifact.</p>
        </div>"""
    else:
        candidates = report.get("candidates", {})
        content = f"""
        {render_recommendation_detail(report)}
        {render_report_next_steps(report, manifest)}
        {render_candidate_selector(report, promotion_allowed=promotion_allowed)}
        {render_metric_visualizer(candidates)}
        {render_failure_summary(candidates)}"""
    return f"""
    <section class="panel tab-panel" id="reports" data-tab-panel="reports">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Reports</p>
          <h2>Optimization outcome</h2>
        </div>
        <p>Report values are read from canonical report artifacts.</p>
      </div>
      {content}
    </section>"""


def render_candidate_selector(report: dict[str, Any], *, promotion_allowed: bool = False) -> str:
    rows = _candidate_metric_rows(report.get("candidates", {}))
    if not rows:
        return ""
    recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}
    selected_id = str(recommendation.get("candidate_id") or rows[0]["candidate_id"])
    objective = promotion_objective(str(recommendation.get("objective") or "balanced"))
    cards = []
    for row in rows:
        candidate_id = row["candidate_id"]
        active = candidate_id == selected_id
        cards.append(
            f"""
            <button type="button" class="candidate-choice {'active' if active else ''}"
              data-candidate-select="{escape(candidate_id)}"
              data-candidate-id="{escape(candidate_id)}"
              data-candidate-objective="{escape(objective)}"
              data-candidate-throughput="{escape(_fmt(row['throughput']))}"
              data-candidate-latency="{escape(_fmt(row['latency']))}">
              <span>{'Selected' if active else 'Candidate'}</span>
              <strong><code>{escape(candidate_id)}</code></strong>
              <small>{escape(_fmt(row['throughput']))} tok/s / {escape(_fmt(row['latency']))} ms</small>
            </button>"""
        )
    gate_text = (
        "Promotion gate is open for this server session."
        if promotion_allowed
        else "Launch with --allow-promotion to test the promote flow."
    )
    return f"""
    <div class="report-card candidate-selector" data-selected-candidate-id="{escape(selected_id)}" data-selected-objective="{escape(objective)}">
      <div class="section-heading compact-heading">
        <div>
          <p class="eyebrow">Select Candidate</p>
          <h3>Choose the profile candidate to promote</h3>
        </div>
        <p id="selected-candidate-summary">Selected <code id="selected-candidate-id">{escape(selected_id)}</code> for <code id="selected-candidate-objective">{escape(objective)}</code>.</p>
      </div>
      <div class="candidate-choice-grid">{''.join(cards)}</div>
      <p class="candidate-gate-note">{escape(gate_text)}</p>
    </div>"""


def render_report_next_steps(report: dict[str, Any], manifest: dict[str, Any] | None) -> str:
    recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}
    status = str(recommendation.get("status") or "unknown")
    candidate = str(recommendation.get("candidate_id") or "no candidate")
    commands = controller_commands(manifest)
    confirm_command = commands.get("confirm", "uv run vllm-optimizer optimize-workload --mode confirm --sweep SWEEP_JSON --out ARTIFACT_DIR")
    return f"""
    <div class="report-card report-next-steps">
      <div class="section-heading compact-heading">
        <div>
          <p class="eyebrow">Continue From Report</p>
          <h3>Decision path</h3>
        </div>
        <p>{escape(status)} / <code>{escape(candidate)}</code></p>
      </div>
      <div class="decision-grid">
        <article>
          <strong>1. Review evidence</strong>
          <small>Use the metrics, rationale, failures, and next actions below before touching the GX10 again.</small>
        </article>
        <article>
          <strong>2. Confirmation gate</strong>
          <small>Run repeated confirmation only when the report makes a candidate worth validating.</small>
          <code>{escape(confirm_command)}</code>
        </article>
        <article>
          <strong>3. Promotion gate</strong>
          <small>Promotion remains disabled until confirmation is accepted and the explicit gate is provided.</small>
          <button type="button" data-tab-jump="promotion" data-refresh-tab="false">Open Promotion Gate</button>
        </article>
      </div>
    </div>"""


def render_runs(run_index: dict[str, Any] | None) -> str:
    if run_index is None:
        content = '<p class="empty">No run index loaded.</p>'
    else:
        runs = _list_of_dicts(run_index.get("runs"))
        cards = []
        for run in runs:
            cards.append(
                f"""
                <article class="run-card">
                  <div class="metric-row-head">
                    <strong>{escape(str(run.get('run_id') or 'run'))}</strong>
                    <span>{escape(str(run.get('modified_at') or 'n/a'))}</span>
                  </div>
                  <p><code>{escape(str(run.get('relative_dir') or 'n/a'))}</code></p>
                  <p>{escape(', '.join(str(item) for item in run.get('artifact_types', [])) or 'no artifacts')}</p>
                  <div class="run-paths">{render_run_paths(run.get('artifact_paths'))}</div>
                </article>"""
            )
        content = f"""
        <p><strong>{escape(str(run_index.get('run_count', len(runs))))}</strong> local run directories indexed.</p>
        <div class="run-grid">{''.join(cards) or '<p class="empty">No runs found.</p>'}</div>"""
    return f"""
    <section class="panel tab-panel" id="runs" data-tab-panel="runs">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Runs</p>
          <h2>Run browser</h2>
        </div>
        <p>Local artifact directories indexed for quick cockpit navigation.</p>
      </div>
      {content}
    </section>"""


def render_automatic_pipeline_panel(
    groups: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    progress = pipeline_progress(status, report)
    rows = "".join(render_pipeline_progress_stage(stage, status, report) for stage in WORKFLOW_STEPS)
    gates = render_human_gate_summary(manifest)
    selected = selected_group_label(groups, manifest)
    command = controller_commands(manifest).get("run", controller_commands(manifest).get("plan", ""))
    return f"""
    <section class="auto-pipeline-panel">
      <div class="auto-flow-card">
        <p class="eyebrow">Primary Flow</p>
        <h2>Start Optimization</h2>
        <p>Select a tuning area, review the generated plan, then let the cockpit advance through automatic stages until a real human decision is needed.</p>
        <dl>
          <div><dt>Tuning area</dt><dd id="auto-flow-selected-area">{escape(selected)}</dd></div>
          <div><dt>Optimization target</dt><dd id="auto-flow-selected-target">Balanced</dd></div>
          <div><dt>User decisions</dt><dd>Live run confirmation and promotion remain explicit.</dd></div>
        </dl>
        <button type="button" class="primary-action" data-controller-action="run" data-controller-endpoint="/api/controller/run" data-controller-command="{escape(command)}">Start Optimization</button>
      </div>
      <div class="pipeline-progress-card">
        <div class="section-heading compact-heading">
          <div>
            <p class="eyebrow">Execution Pipeline</p>
            <h2>Automatic Pipeline Progress</h2>
          </div>
          <span id="pipeline-overall-progress-label" class="step-pill">{progress}%</span>
        </div>
        <div class="progress-track overall-progress" aria-label="Overall progress">
          <div id="pipeline-overall-progress-bar" class="progress-bar" style="width:{progress}%"></div>
        </div>
        <p id="pipeline-caption" class="progress-caption">{escape(pipeline_caption(status, report))}</p>
        <div class="pipeline-stage-list">{rows}</div>
      </div>
      <div class="human-gates-card">
        <p class="eyebrow">Next Decision</p>
        <h2>Human Gates</h2>
        {gates}
      </div>
    </section>"""


def render_pipeline_progress_stage(
    stage: dict[str, Any],
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    action = str(stage["action"])
    state = pipeline_stage_state(action, status, report)
    detail = pipeline_stage_detail(action, status, report)
    return f"""
      <article class="pipeline-stage {escape(state)}" data-pipeline-stage="{escape(action)}">
        <span>{escape(state.title())}</span>
        <strong>{escape(stage['label'])}</strong>
        <small>{escape(detail)}</small>
      </article>"""


def render_human_gate_summary(manifest: dict[str, Any] | None) -> str:
    gates = []
    for stage in _list_of_dicts((manifest or {}).get("stages")):
        if stage.get("remote"):
            gates.append(("Live GX10 execution", "--confirm-live-run"))
        for gate in stage.get("required_gates") or []:
            gates.append(("Safety opt-in", str(gate)))
    promotion = manifest.get("promotion", {}) if isinstance((manifest or {}).get("promotion"), dict) else {}
    gates.append(("Promotion remains manual", str(promotion.get("required_gate") or "--allow-promotion")))
    unique: list[tuple[str, str]] = []
    for gate in gates:
        if gate not in unique:
            unique.append(gate)
    items = "".join(
        f"<li><strong>{escape(label)}</strong><code>{escape(flag)}</code></li>"
        for label, flag in unique
    )
    return f'<ul class="gate-list"><li><strong>Manual gate</strong><code>Only when needed</code></li>{items}</ul>'


def render_guided_step_workspace(
    groups: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    action = current_workflow_action(status, report)
    step = workflow_step(action)
    primary = primary_cockpit_action(action)
    selected = selected_group_label(groups, manifest)
    command = primary_command(primary, manifest, fallback_action=action)
    facts = "".join(f"<li>{escape(item)}</li>" for item in primary["facts"])
    return f"""
    <div class="guided-grid">
      <article class="selected-group-card">
        <p class="eyebrow">Selected Tuning Area</p>
        <h2 id="selected-tuning-area-label">{escape(selected)}</h2>
        <p id="selected-tuning-area-description">{escape(selected_group_description(groups, manifest) or step['group_hint'])}</p>
        <div class="chips">{render_selected_group_chips(groups, manifest)}</div>
        <div class="knobs-tuned-panel">
          <strong>Knobs tuned</strong>
          <ul id="selected-knobs-tuned">{render_selected_knob_items(groups, manifest)}</ul>
        </div>
      </article>
      <article class="active-step-card">
        <p class="eyebrow">{escape(primary['eyebrow'])}</p>
        <h2>{escape(primary['headline'])}</h2>
        <ul class="fact-list">{facts}</ul>
        {render_primary_action_button(primary, manifest)}
        <p class="next-note">Next: {escape(primary['next'])}</p>
      </article>
      <article class="command-shell">
        <p class="eyebrow">Controller command shell</p>
        <h2>{escape(primary['label'])} command</h2>
        <pre><code>{escape(command or 'No command loaded for this step.')}</code></pre>
        {render_secondary_action_button(primary, manifest)}
        <p id="controller-feedback" class="controller-feedback" aria-live="polite">Ready to run the selected step from the cockpit server.</p>
        <div class="what-next">
          <strong>What happens next?</strong>
          <p>{escape(primary['what_next'])}</p>
        </div>
      </article>
    </div>"""


def render_promotion_workflow(
    report: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    *,
    promotion_allowed: bool = False,
) -> str:
    if report is None:
        content = '<p class="empty">No promotion workflow loaded.</p>'
    else:
        recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}
        promotion = manifest.get("promotion", {}) if isinstance((manifest or {}).get("promotion"), dict) else {}
        gate = str(promotion.get("required_gate") or "--allow-promotion")
        available = bool(promotion.get("available", False))
        automatic = bool(promotion.get("automatic", False))
        rows = _candidate_metric_rows(report.get("candidates", {}))
        candidate_id = str(recommendation.get("candidate_id") or (rows[0]["candidate_id"] if rows else "no candidate"))
        objective = promotion_objective(str(recommendation.get("objective") or "balanced"))
        status = str(recommendation.get("status") or "unknown")
        promote_command = controller_commands(manifest).get("promote", "")
        disabled = "" if promotion_allowed else " disabled"
        gate_copy = (
            "The cockpit server was launched with the promotion gate. The button writes a local selected-candidate profile artifact."
            if promotion_allowed
            else f"Promotion is locked. Restart the cockpit with {gate} when you want to test the write path."
        )
        content = f"""
        <div class="promotion-grid" data-selected-candidate-id="{escape(candidate_id)}" data-selected-objective="{escape(objective)}">
          <article class="promotion-card">
            <p class="eyebrow">Recommendation</p>
            <h3>{escape(status)}</h3>
            <dl>
              <div><dt>Candidate</dt><dd><code id="promotion-selected-candidate">{escape(candidate_id)}</code></dd></div>
              <div><dt>Objective</dt><dd>{escape(objective)}</dd></div>
              <div><dt>Available</dt><dd>{escape(str(available))}</dd></div>
              <div><dt>Automatic</dt><dd>{escape(str(automatic))}</dd></div>
            </dl>
          </article>
          <article class="promotion-card gate-card">
            <p class="eyebrow">Required gate</p>
            <h3><code>{escape(gate)}</code></h3>
            <p>{escape(gate_copy)}</p>
            <button type="button" class="primary-action"
              data-controller-action="promote"
              data-controller-endpoint="/api/controller/promote"
              data-controller-command="{escape(promote_command)}"{disabled}>Promote Selected Candidate</button>
          </article>
        </div>
        <div class="command-stack">
          <article>
            <strong>Preview profile promotion</strong>
            <code>uv run vllm-optimizer promote-preview --ranking ARTIFACT_DIR/live/ranking.json --candidate-id {escape(candidate_id)} --out ARTIFACT_DIR/promotion-preview.json</code>
          </article>
          <article>
            <strong>Promote after confirmation</strong>
            <code>uv run vllm-optimizer promote-confirmed-profile --confirmation-report ARTIFACT_DIR/confirmation/confirmation-report.json --ranking ARTIFACT_DIR/live/ranking.json --candidate-id {escape(candidate_id)} --profile-out PROFILE_OUT --summary-out SUMMARY_OUT --force</code>
          </article>
        </div>"""
    return f"""
    <section class="panel tab-panel" id="promotion" data-tab-panel="promotion">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Promotion</p>
          <h2>Promotion workflow</h2>
        </div>
        <p>Profile promotion is gated by explicit opt-in and writes only the selected candidate profile artifact.</p>
      </div>
      {content}
    </section>"""


def render_how_to_use() -> str:
    steps = [
        ("Choose", "Pick a tuning area that matches the workload or parameter family you want to explore."),
        ("Plan", "Plan creates the deterministic run blueprint: candidates, trial IDs, artifacts, objectives, and safety metadata."),
        ("Preview", "Preview validates the blueprint before execution and shows blocked trials or required gates."),
        ("Run", "Run starts remote-capable execution only from the local cockpit server and only after explicit confirmation."),
        ("Report", "Report ranks completed results and explains the recommendation from generated artifacts."),
        ("Confirm", "Confirm repeats A/B checks so a candidate proves stable before promotion."),
        ("Promote", "Promote writes a profile only after confirmation and an explicit promotion gate."),
    ]
    cards = "".join(
        f"""
        <article class="how-card">
          <strong>{escape(label)}</strong>
          <p>{escape(text)}</p>
        </article>"""
        for label, text in steps
    )
    return f"""
    <section class="panel tab-panel" id="how-to-use" data-tab-panel="how-to-use">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Guide</p>
          <h2>How to Use</h2>
        </div>
        <p>The cockpit follows the same deterministic pipeline as the CLI. The server can run safe local actions; remote actions stay gated.</p>
      </div>
      <div class="how-grid">{cards}</div>
    </section>"""


def render_operation_result_panel() -> str:
    return """
    <section class="operation-result" aria-live="polite">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Operation Result</p>
          <h3 id="operation-title">Nothing is running yet.</h3>
        </div>
        <button type="button" id="operation-cancel" disabled>Cancel</button>
      </div>
      <div class="explain-grid">
        <article>
          <strong>What happened?</strong>
          <p id="operation-what">Click Plan to make a blueprint. I made the plan will appear here after Plan finishes.</p>
        </article>
        <article>
          <strong>What does it mean?</strong>
          <p id="operation-meaning">The cockpit will explain each step in plain words.</p>
        </article>
        <article>
          <strong>Next step</strong>
          <p id="operation-next">Click Preview to check if it is safe after you make a plan.</p>
        </article>
      </div>
      <div id="operation-diagnostics" class="failure-diagnostics hidden">
        <strong>Failure detail</strong>
        <p id="operation-failure-cause"></p>
        <ul id="operation-failure-steps"></ul>
        <dl id="operation-failure-artifacts"></dl>
        <div id="operation-failed-trials"></div>
      </div>
    </section>"""


def render_end_to_end_flow_map(status: dict[str, Any] | None, report: dict[str, Any] | None) -> str:
    current = current_workflow_action(status, report)
    current_index = workflow_index(current)
    cards = []
    for step in WORKFLOW_STEPS:
        action = step["action"]
        index = workflow_index(action)
        if action == "confirm":
            title = "Confirmation gate"
            detail = "Manual stability decision after the report is reviewed."
        elif action == "promote":
            title = "Promotion gate"
            detail = "Writes a profile only after explicit opt-in."
        elif action == "report":
            title = "Generate & Review Report"
            detail = "Builds and opens the canonical ranking and recommendation artifact."
        elif action == "run":
            title = "Start Optimization"
            detail = "Runs plan, preview, and the live sweep through real gates."
        else:
            title = step["label"]
            detail = step["description"]
        state = "waiting"
        state_label = "Waiting"
        if index < current_index:
            state = "complete"
            state_label = "Done"
        if action == current:
            state = "current"
            state_label = "Current"
        if action in {"confirm", "promote"} and index >= current_index:
            state = "gate" if action != current else "current gate"
            state_label = "Gate" if action != current else "Review"
        cards.append(
            f"""
            <article class="flow-card {escape(state)}" data-flow-step="{escape(action)}">
              <span>{escape(state_label)}</span>
              <strong>{escape(title)}</strong>
              <small>{escape(detail)}</small>
            </article>"""
        )
    return f"""
      <section class="flow-map" aria-label="End-to-end optimization flow">
        <div class="section-heading compact-heading">
          <div>
            <p class="eyebrow">End-to-End Flow</p>
            <h2>What happens from click to decision</h2>
          </div>
          <p>{escape(pipeline_caption(status, report))}</p>
        </div>
        <div class="flow-grid">{''.join(cards)}</div>
        <div class="flow-context">
          {render_status_summary(status)}
          {render_report_summary(report)}
        </div>
      </section>"""


def render_run_paths(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    return "".join(f"<div><code>{escape(str(key))}</code>: <code>{escape(str(path))}</code></div>" for key, path in sorted(value.items()))


def render_recommendation_detail(report: dict[str, Any]) -> str:
    recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}
    rationale = _list_of_strings(recommendation.get("rationale"))
    next_actions = _list_of_strings(recommendation.get("next_actions"))
    rationale_items = "".join(f"<li>{escape(item)}</li>" for item in rationale) or "<li>No rationale recorded.</li>"
    action_items = "".join(f"<li>{escape(item)}</li>" for item in next_actions) or "<li>No next actions recorded.</li>"
    return f"""
    <div class="report-card recommendation-card">
      <div>
        <p class="eyebrow">Recommendation detail</p>
        <h3>{escape(str(recommendation.get('status') or 'unknown'))}</h3>
        <p>Objective <code>{escape(str(recommendation.get('objective') or 'n/a'))}</code>, candidate <code>{escape(str(recommendation.get('candidate_id') or 'n/a'))}</code>.</p>
      </div>
      <div class="report-lists">
        <div><h4>Rationale</h4><ul>{rationale_items}</ul></div>
        <div><h4>Next actions</h4><ul>{action_items}</ul></div>
      </div>
    </div>"""


def render_metric_visualizer(candidates: Any) -> str:
    rows = _candidate_metric_rows(candidates)
    if not rows:
        return '<div class="report-card"><p class="empty">No candidate metrics available.</p></div>'
    max_tps = max((row["throughput"] or 0 for row in rows), default=0) or 1
    max_latency = max((row["latency"] or 0 for row in rows), default=0) or 1
    visual_rows = []
    table_rows = []
    for row in rows:
        throughput_width = _bar_width(row["throughput"], max_tps)
        latency_width = _bar_width(row["latency"], max_latency)
        role = "baseline" if row["baseline"] else "candidate"
        if not row["recommendable"]:
            role = "excluded"
        visual_rows.append(
            f"""
            <article class="metric-row">
              <div class="metric-row-head">
                <strong><code>{escape(row['candidate_id'])}</code></strong>
                <span>{escape(role)}</span>
              </div>
              <div class="report-bar-line">
                <span>Throughput</span>
                <div class="report-bar-track"><div class="report-bar throughput" data-report-bar="throughput" style="width:{throughput_width:.3f}%"></div></div>
                <strong>{escape(_fmt(row['throughput']))}</strong>
              </div>
              <div class="report-bar-line">
                <span>Latency</span>
                <div class="report-bar-track"><div class="report-bar latency" data-report-bar="latency" style="width:{latency_width:.3f}%"></div></div>
                <strong>{escape(_fmt(row['latency']))}</strong>
              </div>
            </article>"""
        )
        table_rows.append(
            f"""
            <tr>
              <td><code>{escape(row['candidate_id'])}</code></td>
              <td>{escape(role)}</td>
              <td>{escape(_fmt(row['throughput']))}</td>
              <td>{escape(_fmt(row['latency']))}</td>
              <td>{escape(_fmt_pct(row['failure_rate']))}</td>
            </tr>"""
        )
    return f"""
    <div class="report-card">
      <div class="section-heading">
        <div><p class="eyebrow">Metric visualizer</p><h3>Candidate performance</h3></div>
        <p>Bars preserve the canonical report's metrics without recomputing winners.</p>
      </div>
      <div class="metric-visuals">{''.join(visual_rows)}</div>
      <table>
        <thead><tr><th>Candidate</th><th>Role</th><th>Tok/s</th><th>Latency</th><th>Failure</th></tr></thead>
        <tbody>{''.join(table_rows)}</tbody>
      </table>
    </div>"""


def render_failure_summary(candidates: Any) -> str:
    rows = _candidate_metric_rows(candidates)
    if not rows:
        return ""
    items = []
    for row in rows:
        status = "recommendable" if row["recommendable"] else "excluded"
        reason = row["exclusion_reason"] or "No exclusion reason recorded."
        items.append(
            f"""
            <article class="failure-item {'excluded' if not row['recommendable'] else ''}">
              <strong><code>{escape(row['candidate_id'])}</code></strong>
              <span>{escape(_fmt_pct(row['failure_rate']))}</span>
              <small>{escape(status)} - {escape(reason)}</small>
            </article>"""
        )
    return f"""
    <div class="report-card">
      <div class="section-heading">
        <div><p class="eyebrow">Failure summary</p><h3>Reliability and exclusions</h3></div>
        <p>Failed or excluded candidates stay visible instead of disappearing from the report.</p>
      </div>
      <div class="failure-grid">{''.join(items)}</div>
    </div>"""


def render_right_rail(
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    return f"""
    <aside class="right-rail">
      {render_next_action_panel(manifest, status, report)}
      <section class="rail-panel">
        <h2>Execution</h2>
        {render_live_execution_summary(status)}
      </section>
    </aside>"""


def render_live_execution_summary(status: dict[str, Any] | None) -> str:
    initial_status = str((status or {}).get("overall_status") or "idle")
    initial_summary = "No active operation yet." if status is None else "Loaded status artifact."
    initial_progress = 0
    if status is not None:
        trial_counts = status.get("trial_counts", {}) if isinstance(status.get("trial_counts"), dict) else {}
        completed = _number(trial_counts.get("completed")) or 0
        total = _number(trial_counts.get("total")) or 0
        initial_progress = int((completed / total) * 100) if total else 0
    return f"""
    <div class="live-execution" id="live-execution-panel">
      <div class="summary-block compact">
        <span id="live-execution-title">Status</span>
        <strong id="live-execution-status">{escape(initial_status)}</strong>
        <small id="live-execution-elapsed">{escape(initial_summary)}</small>
      </div>
      <div class="progress-track mini-progress" aria-label="Live execution progress">
        <div id="live-execution-progress-bar" class="progress-bar" style="width:{initial_progress}%"></div>
      </div>
      <p id="live-execution-summary" class="controller-feedback">{escape(initial_summary)}</p>
    </div>"""


def render_next_action_panel(
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    action = current_workflow_action(status, report)
    primary = primary_cockpit_action(action)
    facts = "".join(f"<li>{escape(item)}</li>" for item in primary["facts"])
    followups = "".join(f"<li>{escape(item['label'])}</li>" for item in WORKFLOW_STEPS[workflow_index(action) : workflow_index(action) + 3])
    return f"""
      <section class="rail-panel next-action-card">
        <p class="eyebrow">Next Action</p>
        <span class="step-pill">Step {workflow_index(action)} of {len(WORKFLOW_STEPS)}</span>
        <h2 id="next-action-headline">{escape(primary['headline'])}</h2>
        <p id="next-action-description">{escape(primary['description'])}</p>
        <ul id="next-action-facts" class="fact-list compact">{facts}</ul>
        {render_primary_action_button(primary, manifest, button_id="next-action-button")}
        <div class="after-this">
          <strong>After this:</strong>
          <ul>{followups or '<li>Review the resulting artifacts.</li>'}</ul>
        </div>
      </section>"""


def render_sources(sources: dict[str, str | None]) -> str:
    if not sources:
        return ""
    rows = []
    for key, value in sorted(sources.items()):
        rows.append(f"<tr><td>{escape(key)}</td><td><code>{escape(str(value or 'not loaded'))}</code></td></tr>")
    return f"""
    <section class="panel tab-panel" id="sources" data-tab-panel="sources">
      <div class="section-heading"><div><p class="eyebrow">Traceability</p><h2>Source artifacts</h2></div></div>
      <table><tbody>{''.join(rows)}</tbody></table>
    </section>"""


def render_group_card(group: dict[str, Any]) -> str:
    gate = "requires opt-in" if group.get("requires_opt_in") else "no extra opt-in"
    search_text = group_search_text(group)
    knobs = group_knobs(group)
    return f"""
    <article class="group-card {escape(str(group.get('safety_tier') or 'unknown'))}" data-family="{escape(str(group.get('family') or 'unknown'))}" data-search="{escape(search_text)}" data-tuning-area-id="{escape(str(group.get('id') or ''))}">
      <div class="card-topline"><span>{escape(group_display_family(group))}</span><strong>{escape(str(group.get('safety_tier') or 'unknown'))}</strong></div>
      <h3>{escape(group_label(group))}</h3>
      <p>{escape(str(group.get('description') or 'No description.'))}</p>
      <dl>
        <div><dt>Command</dt><dd>{escape(str(group.get('command_kind') or 'n/a'))}</dd></div>
        <div><dt>Knobs tuned</dt><dd>{escape(', '.join(knobs) or 'n/a')}</dd></div>
        <div><dt>Gate</dt><dd>{escape(gate)}</dd></div>
        <div><dt>Config</dt><dd><code>{escape(str(group.get('config_path') or 'n/a'))}</code></dd></div>
      </dl>
    </article>"""


def group_search_text(group: dict[str, Any]) -> str:
    return " ".join(
        dedupe_strings(
            [
                group_label(group),
                group_display_family(group),
                str(group.get("id") or ""),
                str(group.get("family") or ""),
                str(group.get("safety_tier") or ""),
                str(group.get("description") or ""),
                str(group.get("command_kind") or ""),
                str(group.get("config_path") or ""),
            ]
        )
    ).lower()


def render_status_summary(status: dict[str, Any] | None) -> str:
    if status is None:
        return '<p class="empty">No execution status loaded.</p>'
    trial_counts = status.get("trial_counts", {}) if isinstance(status.get("trial_counts"), dict) else {}
    return f"""
    <div class="summary-block">
      <span>Status</span>
      <strong>{escape(str(status.get('overall_status') or 'unknown'))}</strong>
      <small>{escape(str(trial_counts.get('completed', 0)))} completed / {escape(str(trial_counts.get('total', 0)))} total, {escape(str(trial_counts.get('failed', 0)))} failed</small>
    </div>"""


def render_report_summary(report: dict[str, Any] | None) -> str:
    if report is None:
        return '<p class="empty">No canonical report loaded.</p>'
    recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}
    return f"""
    <div class="summary-block">
      <span>Recommendation</span>
      <strong>{escape(str(recommendation.get('status') or 'unknown'))}</strong>
      <small>{escape(str(recommendation.get('objective') or 'no objective'))} / {escape(str(recommendation.get('candidate_id') or 'no candidate'))}</small>
    </div>"""


def render_disabled_actions(manifest: dict[str, Any] | None) -> str:
    return f"""
    <div class="disabled-actions">
      <div><strong>Controller actions</strong><p>Served by <code>cockpit-server</code>, these buttons call local API endpoints. Without the server, they copy commands.</p></div>
      <div>{render_controller_buttons(manifest)}</div>
    </div>"""


def render_controller_buttons(manifest: dict[str, Any] | None, *, compact: bool = False) -> str:
    commands = controller_commands(manifest)
    preferred = [step["action"] for step in WORKFLOW_STEPS]
    ordered = [(name, commands[name]) for name in preferred if name in commands]
    ordered.extend((name, command) for name, command in sorted(commands.items()) if name not in preferred)
    if compact:
        ordered = ordered[:6]
    buttons = []
    for name, command in ordered:
        if name in {"confirm", "promote"}:
            buttons.append(
                f'<button type="button" disabled data-gated-action="{escape(name)}" '
                f'data-controller-command="{escape(command)}">{escape(name.title())}{help_button(name)}</button>'
            )
            continue
        buttons.append(
            f'<button type="button" data-controller-action="{escape(name)}" data-controller-endpoint="/api/controller/{escape(name)}" '
            f'data-controller-command="{escape(command)}">{escape(name.title())}{help_button(name)}</button>'
        )
    return "".join(buttons)


def controller_commands(manifest: dict[str, Any] | None) -> dict[str, str]:
    stages = _list_of_dicts((manifest or {}).get("stages"))
    commands = {
        str(stage.get("name") or "stage"): str(stage.get("command_hint") or "")
        for stage in stages
        if stage.get("command_hint")
    }
    defaults = {
        "plan": "uv run vllm-optimizer optimize-workload --mode plan --sweep SWEEP_JSON --out ARTIFACT_DIR",
        "preview": "uv run vllm-optimizer cockpit-preview --sweep SWEEP_JSON --out-dir ARTIFACT_DIR",
        "run": "uv run vllm-optimizer cockpit-run --sweep SWEEP_JSON --config config/local.gx10.json --out-dir ARTIFACT_DIR --confirm-live-run",
        "report": "uv run vllm-optimizer optimize-workload --mode report --sweep SWEEP_JSON --out ARTIFACT_DIR",
        "confirm": "uv run vllm-optimizer optimize-workload --mode confirm --sweep SWEEP_JSON --out ARTIFACT_DIR",
        "promote": "uv run vllm-optimizer promote-confirmed-profile --confirmation-report ARTIFACT_DIR/confirmation/confirmation-report.json --ranking ARTIFACT_DIR/live/ranking.json --profile-out PROFILE_OUT --summary-out SUMMARY_OUT --force",
    }
    return {**defaults, **commands}


WORKFLOW_STEPS = [
    {
        "action": "plan",
        "label": "Generate Plan",
        "headline": "Generate Plan",
        "description": "Build the proposed vLLM tuning plan for the selected tuning area.",
        "group_hint": "Start by turning the selected tuning area into a deterministic blueprint.",
        "facts": ["No execution", "Deterministic output", "Safe to run"],
        "next": "Preview Commands will be enabled.",
        "what_next": "After planning, preview the exact commands before execution.",
    },
    {
        "action": "preview",
        "label": "Preview Commands",
        "headline": "Preview Commands",
        "description": "Inspect the exact local and remote commands before any live run starts.",
        "group_hint": "Check command shape, output paths, and required gates before running.",
        "facts": ["No remote execution", "Shows required gates", "Good checkpoint"],
        "next": "Run Optimization will be enabled.",
        "what_next": "If the preview looks right, run the optimization with the live-run gate.",
    },
    {
        "action": "run",
        "label": "Run Optimization",
        "headline": "Run Optimization",
        "description": "Execute the selected sweep and write progress artifacts for reporting.",
        "group_hint": "Run the selected tuning family and watch status artifacts update.",
        "facts": ["Can touch GX10", "Requires confirmation", "Cancelable from server jobs"],
        "next": "Generate & Review Report will be enabled after results exist.",
        "what_next": "When execution finishes, generate or load the canonical report.",
    },
    {
        "action": "report",
        "label": "Generate & Review Report",
        "headline": "Generate & Review Report",
        "description": "Rank completed results, write the canonical report, and open the report view.",
        "group_hint": "Turn run artifacts into a decision-ready report.",
        "facts": ["Artifact only", "Shows winner", "Report opens automatically after generation"],
        "next": "Confirm Candidate will be enabled if a candidate is recommendable.",
        "what_next": "Use confirmation before trusting a winner enough to promote it.",
    },
    {
        "action": "confirm",
        "label": "Confirm Candidate",
        "headline": "Confirm Candidate",
        "description": "Repeat checks so the current winner proves stable against baseline.",
        "group_hint": "Verify the recommendation before writing any profile.",
        "facts": ["Repeated checks", "Compares baseline", "No promotion yet"],
        "next": "Promote Profile remains gated by explicit opt-in.",
        "what_next": "If confirmation passes, decide whether to promote the profile.",
    },
    {
        "action": "promote",
        "label": "Promote Profile",
        "headline": "Promote Profile",
        "description": "Write the confirmed configuration only after the promotion gate.",
        "group_hint": "Promotion is visible but intentionally gated.",
        "facts": ["Writes profile", "Requires explicit gate", "Never automatic"],
        "next": "Review promoted profile and rerun if workloads change.",
        "what_next": "After promotion, keep the report and profile summary as provenance.",
    },
]


def workflow_step(action: str) -> dict[str, Any]:
    for step in WORKFLOW_STEPS:
        if step["action"] == action:
            return step
    return WORKFLOW_STEPS[0]


def workflow_index(action: str) -> int:
    for index, step in enumerate(WORKFLOW_STEPS, start=1):
        if step["action"] == action:
            return index
    return 1


def current_workflow_action(status: dict[str, Any] | None, report: dict[str, Any] | None) -> str:
    if report is not None:
        recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}
        if str(recommendation.get("status") or "").lower() in {"confirmed", "promotable", "promoted"}:
            return "promote"
        return "confirm"
    if status is not None:
        overall = str(status.get("overall_status") or "").lower()
        if overall in {"completed", "complete", "succeeded", "success"}:
            return "report"
        if overall in {"running", "cancel-requested", "failed"}:
            return "run"
    return "plan"


def is_loaded_artifact_state(status: dict[str, Any] | None, report: dict[str, Any] | None) -> bool:
    if report is None:
        return False
    overall = str((status or {}).get("overall_status") or (status or {}).get("overall_state") or "").lower()
    return overall not in {"running", "cancel-requested"}


def primary_cockpit_action(action: str) -> dict[str, Any]:
    if action in {"plan", "preview"}:
        return {
            "action": "run",
            "label": "Start Optimization",
            "headline": "Start Optimization",
            "eyebrow": "Automatic flow",
            "description": "Runs plan and preview first, then stops for live GX10 confirmation before remote execution.",
            "facts": ["Plans automatically", "No execution until gate", "Previews safety", "Stops at real gates"],
            "next": "The cockpit will plan, preview, then ask before live GX10 execution.",
            "what_next": "The cockpit creates the plan and preview artifacts first, then uses the live-run confirmation gate before touching the GX10.",
        }
    if action == "confirm":
        return {
            "action": "review-report",
            "label": "Review Report",
            "headline": "Review Report",
            "eyebrow": "Decision gate",
            "description": "Read the recommendation and evidence before deciding whether a confirmation run is warranted.",
            "facts": ["Report is ready", "No unsupported endpoint", "Confirmation stays gated"],
            "next": "Use the report evidence to decide whether to run confirmation.",
            "what_next": "The Reports tab shows the current winner, failure reasons, rationale, and recommended follow-up before any confirmation work.",
            "tab_jump": "reports",
        }
    if action == "promote":
        return {
            "action": "review-promotion",
            "label": "Review Promotion Gate",
            "headline": "Review Promotion Gate",
            "eyebrow": "Promotion gate",
            "description": "Review the confirmed candidate and promotion command before writing a profile.",
            "facts": ["Explicit opt-in", "Writes a profile", "Never automatic"],
            "next": "Promote only with the explicit CLI gate after confirmation.",
            "what_next": "The Promotion tab keeps the write action visible, disabled by default, and tied to its required gate.",
            "tab_jump": "promotion",
        }
    step = workflow_step(action)
    return {
        "action": action,
        "label": step["label"],
        "headline": step["headline"],
        "eyebrow": f"Step {workflow_index(action)}: {step['label']}",
        "description": step["description"],
        "facts": step["facts"],
        "next": step["next"],
        "what_next": step["what_next"],
    }


def pipeline_progress(status: dict[str, Any] | None, report: dict[str, Any] | None) -> int:
    if report is not None:
        recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}
        if str(recommendation.get("status") or "").lower() in {"confirmed", "promotable", "promoted"}:
            return 84
        return 72
    if status is not None:
        overall = str(status.get("overall_status") or "").lower()
        if overall in {"completed", "complete", "succeeded", "success"}:
            return 64
        if overall in {"running", "cancel-requested", "failed"}:
            trial_counts = status.get("trial_counts", {}) if isinstance(status.get("trial_counts"), dict) else {}
            completed = _number(trial_counts.get("completed")) or 0
            total = _number(trial_counts.get("total")) or 0
            trial_progress = (completed / total) if total else 0
            return int(32 + (trial_progress * 28))
    return 8


def pipeline_caption(status: dict[str, Any] | None, report: dict[str, Any] | None) -> str:
    if report is not None:
        return "Report is available. Confirmation or promotion may be the next real decision."
    if status is not None:
        overall = str(status.get("overall_status") or "").lower()
        trial_counts = status.get("trial_counts", {}) if isinstance(status.get("trial_counts"), dict) else {}
        completed = trial_counts.get("completed", 0)
        total = trial_counts.get("total", 0)
        if overall in {"running", "cancel-requested", "failed"}:
            return f"Running trial {completed} of {total}"
        if overall in {"completed", "complete", "succeeded", "success"}:
            return "Run complete. Reporting can be generated automatically."
    return "Ready to generate a plan and preview safety before execution."


def pipeline_stage_state(action: str, status: dict[str, Any] | None, report: dict[str, Any] | None) -> str:
    current = current_workflow_action(status, report)
    if action == "promote":
        return "manual gate"
    if workflow_index(action) < workflow_index(current):
        return "complete"
    if action == current:
        if is_loaded_artifact_state(status, report):
            return "review"
        if action in {"run", "report", "confirm"}:
            return "running" if status is not None or report is not None else "waiting"
        return "automatic"
    return "waiting"


def pipeline_stage_detail(action: str, status: dict[str, Any] | None, report: dict[str, Any] | None) -> str:
    if action == "plan":
        return "Creates the deterministic blueprint."
    if action == "preview":
        return "Validates commands and safety gates automatically."
    if action == "run":
        return pipeline_caption(status, report) if status is not None else "Starts only after live-run confirmation."
    if action == "report":
        return "Ranks artifacts and explains the recommendation."
    if action == "confirm":
        if report is not None:
            return "Report review: choose whether confirmation is still needed."
        return "Repeats checks when stability is required."
    if action == "promote":
        return "Promotion remains manual and explicitly gated."
    return "Waiting for prior stages."


def workflow_locked_label(action: str, manifest: dict[str, Any] | None) -> str:
    if action == "promote":
        promotion = manifest.get("promotion", {}) if isinstance((manifest or {}).get("promotion"), dict) else {}
        return f"Locked ({promotion.get('required_gate') or '--allow-promotion'})"
    if action == "run":
        return "Locked (--confirm-live-run)"
    return "Locked"


def selected_group_label(groups: list[dict[str, Any]], manifest: dict[str, Any] | None) -> str:
    group = manifest.get("group", {}) if isinstance((manifest or {}).get("group"), dict) else {}
    label = group.get("display_label") or group.get("label") or group.get("id")
    if label:
        return str(label)
    if groups:
        return group_label(groups[0])
    return "No tuning area selected"


def selected_group_description(groups: list[dict[str, Any]], manifest: dict[str, Any] | None) -> str:
    group = selected_group(groups, manifest)
    return str(group.get("description") or "")


def render_selected_group_chips(groups: list[dict[str, Any]], manifest: dict[str, Any] | None) -> str:
    selected = selected_group(groups, manifest)
    values = [
        group_display_family(selected),
        str(selected.get("safety_tier") or "unknown safety"),
        str(selected.get("command_kind") or "workflow"),
    ]
    return "".join(f"<span>{escape(value)}</span>" for value in values)


def render_selected_knob_items(groups: list[dict[str, Any]], manifest: dict[str, Any] | None) -> str:
    knobs = group_knobs(selected_group(groups, manifest))
    return "".join(f"<li>{escape(knob)}</li>" for knob in knobs) or "<li>No knob metadata loaded.</li>"


def selected_group(groups: list[dict[str, Any]], manifest: dict[str, Any] | None) -> dict[str, Any]:
    manifest_group = manifest.get("group", {}) if isinstance((manifest or {}).get("group"), dict) else {}
    group_id = str(manifest_group.get("id") or "")
    if group_id:
        for group in groups:
            if str(group.get("id") or "") == group_id:
                return group
        return manifest_group
    return groups[0] if groups else {}


def read_profile_summaries(profile_paths: list[Path] | tuple[Path, ...]) -> list[dict[str, Any]]:
    summaries = []
    for path in profile_paths:
        if not path.exists():
            continue
        data = read_json(path)
        if isinstance(data, dict):
            summaries.append(profile_summary(data, path))
    return summaries


def read_model_catalog_profile_summaries(model_catalog_path: Path | None) -> list[dict[str, Any]]:
    if model_catalog_path is None or not model_catalog_path.exists():
        return []
    catalog = read_json(model_catalog_path)
    models = catalog.get("models")
    if not isinstance(models, list):
        return []
    summaries = []
    for item in models:
        if not isinstance(item, dict):
            continue
        profile_path = item.get("profile_path")
        profile_data: dict[str, Any] = {}
        path = Path(profile_path) if isinstance(profile_path, str) and profile_path else Path()
        if profile_path and path.exists():
            loaded = read_json(path)
            if isinstance(loaded, dict):
                profile_data = loaded
        summary = profile_summary(profile_data, path) if profile_data else {"path": profile_path}
        summary.update(
            {
                "model_id": item.get("model_id"),
                "display_name": item.get("display_name"),
                "served_model_name": item.get("served_model_name") or summary.get("served_model_name"),
                "support_status": item.get("support_status"),
                "tool_support": item.get("tool_support"),
                "role": item.get("support_status") or "candidate",
            }
        )
        summaries.append(summary)
    return summaries


def profile_summary(data: dict[str, Any], path: Path) -> dict[str, Any]:
    promotion = data.get("promotion", {}) if isinstance(data.get("promotion"), dict) else {}
    confirmation = promotion.get("confirmation", {}) if isinstance(promotion.get("confirmation"), dict) else {}
    decision = confirmation.get("decision", {}) if isinstance(confirmation.get("decision"), dict) else {}
    role = "Promoted" if promotion else "Base"
    if str(data.get("profile_id") or "").endswith("recommended"):
        role = "Recommended"
    if "concurrent" in str(data.get("profile_id") or ""):
        role = "Confirmed Concurrent"
    return {
        "path": path.as_posix(),
        "profile_id": data.get("profile_id"),
        "model": data.get("model"),
        "served_model_name": data.get("served_model_name"),
        "tool_call_parser": data.get("tool_call_parser"),
        "enable_auto_tool_choice": data.get("enable_auto_tool_choice"),
        "gpu_memory_utilization": data.get("gpu_memory_utilization"),
        "max_model_len": data.get("max_model_len"),
        "performance_mode": data.get("performance_mode"),
        "optional_flags": data.get("optional_flags", {}),
        "role": role,
        "promotion_status": decision.get("status"),
    }


def group_label(group: dict[str, Any]) -> str:
    return str(group.get("display_label") or group.get("label") or group.get("id") or "Unnamed tuning area")


def group_display_family(group: dict[str, Any]) -> str:
    return str(group.get("display_family") or group.get("family") or "Unknown family")


def group_knobs(group: dict[str, Any]) -> list[str]:
    value = group.get("knobs_tuned")
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped = []
    for value in values:
        if not value or value in seen:
            continue
        deduped.append(value)
        seen.add(value)
    return deduped


def primary_command(primary: dict[str, Any], manifest: dict[str, Any] | None, *, fallback_action: str | None = None) -> str:
    command_action = str(primary.get("command_action") or primary.get("action") or fallback_action or "")
    return controller_commands(manifest).get(command_action, "")


def render_primary_action_button(
    primary: dict[str, Any], manifest: dict[str, Any] | None, *, button_id: str | None = None
) -> str:
    action = str(primary.get("action") or "")
    text = str(primary.get("label") or workflow_step(action)["label"])
    button_id_attr = f' id="{escape(button_id)}"' if button_id else ""
    if primary.get("tab_jump"):
        tab = str(primary["tab_jump"])
        refresh = "true" if primary.get("refresh_tab") else "false"
        return (
            f'<button{button_id_attr} type="button" class="primary-action" '
            f'data-tab-jump="{escape(tab)}" data-refresh-tab="{refresh}">'
            f'{escape(text)} -></button>'
        )
    command = primary_command(primary, manifest)
    return (
        f'<button{button_id_attr} type="button" class="primary-action" data-controller-action="{escape(action)}" '
        f'data-controller-endpoint="/api/controller/{escape(action)}" data-controller-command="{escape(command)}">'
        f'{escape(text)} -></button>'
    )


def render_secondary_action_button(primary: dict[str, Any], manifest: dict[str, Any] | None) -> str:
    action = str(primary.get("action") or "")
    text = str(primary.get("label") or action)
    if primary.get("tab_jump"):
        tab = str(primary["tab_jump"])
        refresh = "true" if primary.get("refresh_tab") else "false"
        return (
            f'<button type="button" data-tab-jump="{escape(tab)}" data-refresh-tab="{refresh}">'
            f'{escape(text)}</button>'
        )
    command = primary_command(primary, manifest)
    return (
        f'<button type="button" data-controller-action="{escape(action)}" '
        f'data-controller-endpoint="/api/controller/{escape(action)}" data-controller-command="{escape(command)}">'
        f'{escape(text)}</button>'
    )


def help_button(key: str) -> str:
    label = key.replace("-", " ").title()
    text = HELP_TEXT.get(key, f"Runs the {label} cockpit action.")
    return (
        f' <span class="help-dot" data-help-key="{escape(key)}" aria-label="What is {escape(label)}?" '
        f'title="{escape(text)}">?</span>'
    )


def render_gate_list(value: Any) -> str:
    gates = value if isinstance(value, list) else []
    return " ".join(f"<code>{escape(str(gate))}</code>" for gate in gates) or "none"


def metric_tile(label: str, value: Any, suffix: str) -> str:
    return f"""
    <article class="metric-tile">
      <span>{escape(label)}</span>
      <strong>{escape(str(value))}</strong>
      <small>{escape(suffix)}</small>
    </article>"""


OPTIMIZATION_TARGETS = [
    {
        "id": "balanced",
        "label": "Balanced",
        "headline": "Default recommendation",
        "description": "Blend throughput, latency, failure rate, and safety.",
    },
    {
        "id": "performance",
        "label": "Performance",
        "headline": "Max useful speed",
        "description": "Prefer higher tokens/sec and lower latency.",
    },
    {
        "id": "single_user",
        "label": "Single User",
        "headline": "Fastest personal session",
        "description": "Prefer one active request: lower latency and smoother interactive response over aggregate concurrency.",
    },
    {
        "id": "stability",
        "label": "Stability",
        "headline": "Lowest operational risk",
        "description": "Penalize failures, variance, and fragile candidates.",
    },
    {
        "id": "tool_use",
        "label": "Tool Use",
        "headline": "Structured-output reliability",
        "description": "Foundation for future parser and JSON correctness scoring.",
    },
]


def _read_optional(path: Path | None, label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.exists():
        raise WebCockpitError(f"{label} path does not exist: {path}")
    return read_json(path)


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _candidate_metric_rows(candidates: Any) -> list[dict[str, Any]]:
    rows = []
    if isinstance(candidates, dict):
        candidate_items = candidates.items()
    elif isinstance(candidates, list):
        candidate_items = (
            (
                str(candidate.get("candidate_id") or candidate.get("id") or candidate.get("name") or f"candidate-{index + 1}"),
                candidate,
            )
            for index, candidate in enumerate(candidates)
            if isinstance(candidate, dict)
        )
    else:
        candidate_items = []
    for candidate_id, candidate in candidate_items:
        if not isinstance(candidate, dict):
            continue
        metrics = candidate.get("metrics", {}) if isinstance(candidate.get("metrics"), dict) else {}
        rows.append(
            {
                "candidate_id": str(candidate_id),
                "throughput": _number(metrics.get("aggregate_tokens_per_second")),
                "latency": _number(metrics.get("mean_latency_ms")),
                "failure_rate": _number(metrics.get("failure_rate")),
                "recommendable": bool(candidate.get("recommendable", True)),
                "baseline": bool(candidate.get("is_baseline", False)),
                "exclusion_reason": str(candidate.get("exclusion_reason") or ""),
            }
        )
    return sorted(rows, key=lambda row: (not row["recommendable"], row["candidate_id"]))


def promotion_objective(value: str) -> str:
    if value == "performance":
        return "throughput"
    if value == "single_user":
        return "single_user"
    if value in {"stability", "tool_use", "no objective"}:
        return "balanced"
    return value or "balanced"


def report_outcome_summary(report: dict[str, Any] | None) -> dict[str, Any]:
    recommendation = report.get("recommendation", {}) if isinstance((report or {}).get("recommendation"), dict) else {}
    candidates = report.get("candidates", {}) if isinstance(report, dict) else {}
    rows = _candidate_metric_rows(candidates)
    baseline = next((row for row in rows if row["baseline"]), None)
    if baseline is None and rows:
        baseline = rows[0]
    recommended_id = str(recommendation.get("candidate_id") or "")
    winner = next((row for row in rows if row["candidate_id"] == recommended_id), None)
    if winner is None:
        winner = max(
            (row for row in rows if row["recommendable"]),
            key=lambda row: row["throughput"] or 0,
            default=max(rows, key=lambda row: row["throughput"] or 0, default=None),
        )
    decision = str(recommendation.get("status") or ("no report" if not rows else "not ranked"))
    objective = str(recommendation.get("objective") or "n/a")
    if winner is None:
        return {
            "winner_id": "No report",
            "winner_detail": "Load a canonical report to see the recommended candidate.",
            "baseline_detail": "Baseline unavailable until report data is loaded.",
            "improvement": "Awaiting data",
            "delta_class": "delta-neutral",
            "decision": decision,
            "decision_detail": "No report decision has been loaded.",
            "baseline_row": None,
            "winner_row": None,
        }
    improvement = "Baseline n/a"
    delta_class = "delta-neutral"
    if baseline and isinstance(baseline["throughput"], float | int) and isinstance(winner["throughput"], float | int):
        delta = winner["throughput"] - baseline["throughput"]
        if baseline["throughput"] > 0:
            pct = delta / baseline["throughput"]
            sign = "+" if pct >= 0 else ""
            improvement = f"{sign}{pct:.1%}"
        else:
            sign = "+" if delta >= 0 else ""
            improvement = f"{sign}{delta:.3f} tok/s"
        delta_class = "delta-positive" if delta >= 0 else "delta-negative"
    winner_detail = f"{_fmt(winner['throughput'])} tok/s, {_fmt(winner['latency'])} ms latency"
    baseline_detail = (
        f"Baseline {baseline['candidate_id']}: {_fmt(baseline['throughput'])} tok/s"
        if baseline
        else "Baseline candidate not present in report."
    )
    return {
        "winner_id": winner["candidate_id"],
        "winner_detail": winner_detail,
        "baseline_detail": baseline_detail,
        "improvement": improvement,
        "delta_class": delta_class,
        "decision": decision,
        "decision_detail": f"Objective {objective}; confirmation and promotion stay gated.",
        "baseline_row": baseline,
        "winner_row": winner,
    }


def render_evidence_bar(label: str, row: dict[str, Any] | None, max_tps: float) -> str:
    if row is None:
        return f"""
          <div class="comparison-row empty-row">
            <span>{escape(label)}</span>
            <div class="evidence-bar-track"><div class="evidence-bar" style="width:0%"></div></div>
            <strong>n/a</strong>
          </div>"""
    width = _bar_width(row["throughput"], max_tps)
    return f"""
          <div class="comparison-row">
            <span>{escape(label)}</span>
            <div class="evidence-bar-track"><div class="evidence-bar" style="width:{width:.3f}%"></div></div>
            <strong>{escape(_fmt(row['throughput']))}</strong>
            <small><code>{escape(row['candidate_id'])}</code></small>
          </div>"""


def render_scatter_dot(row: dict[str, Any], max_tps: float, max_latency: float, winner_id: str) -> str:
    throughput = row["throughput"] or 0
    latency = row["latency"] or max_latency
    left = max(6.0, min(94.0, (throughput / max_tps) * 88.0 + 6.0))
    bottom = max(6.0, min(94.0, 100.0 - ((latency / max_latency) * 88.0 + 6.0)))
    classes = "scatter-dot"
    if row["candidate_id"] == winner_id:
        classes += " winner"
    if row["baseline"]:
        classes += " baseline"
    if not row["recommendable"]:
        classes += " excluded"
    return (
        f'<span class="{escape(classes)}" style="left:{left:.3f}%; bottom:{bottom:.3f}%" '
        f'title="{escape(row["candidate_id"])}: {escape(_fmt(throughput))} tok/s, {escape(_fmt(latency))} ms"></span>'
    )


def render_stability_row(row: dict[str, Any]) -> str:
    failure = row["failure_rate"] or 0.0
    stability = max(0.0, min(1.0, 1.0 - failure))
    return f"""
          <div class="stability-row">
            <span><code>{escape(row['candidate_id'])}</code></span>
            <div class="stability-track"><div style="width:{stability * 100:.3f}%"></div></div>
            <strong>{escape(_fmt_pct(failure))}</strong>
          </div>"""


def render_heatmap_cell(row: dict[str, Any]) -> str:
    failure = row["failure_rate"] or 0.0
    level = "low"
    if failure >= 0.2:
        level = "high"
    elif failure > 0:
        level = "medium"
    if not row["recommendable"]:
        level += " excluded"
    return f"""
          <div class="heat-cell {escape(level)}" title="{escape(row['candidate_id'])}: {escape(_fmt_pct(failure))}">
            <strong>{escape(_fmt_pct(failure))}</strong>
            <span>{escape(row['candidate_id'])}</span>
          </div>"""


def _number(value: Any) -> float | None:
    return float(value) if isinstance(value, int | float) else None


def _bar_width(value: float | None, maximum: float) -> float:
    if value is None or maximum <= 0:
        return 0.0
    return max(4.0, min(100.0, (value / maximum) * 100.0))


def _fmt(value: Any) -> str:
    return f"{value:.3f}" if isinstance(value, int | float) else "n/a" if value is None else str(value)


def _fmt_pct(value: Any) -> str:
    return f"{value:.3%}" if isinstance(value, int | float) else "n/a" if value is None else str(value)


HELP_TEXT = {
    "plan": "Plan creates the deterministic run blueprint without touching the GX10.",
    "preview": "Preview validates the blueprint and shows blocked trials or required gates.",
    "run": "Run starts remote-capable execution only through the local server and explicit confirmation.",
    "report": "Report ranks completed artifacts and explains the recommendation.",
    "confirm": "Confirm repeats A/B checks before any promotion decision.",
    "promote": "Promote writes a profile only after confirmation and an explicit promotion gate.",
}


CSS = """
:root {
  color-scheme: dark;
  --bg: #04080d;
  --panel: #09131f;
  --panel-2: #0e1a29;
  --metal: #172332;
  --ink: #edf8ff;
  --muted: #91a7bb;
  --line: #21384f;
  --cyan: #22d7ff;
  --green: #45f29b;
  --amber: #f1c45a;
  --red: #ff6b6b;
  --violet: #9e9cff;
  --shadow: rgba(0, 0, 0, .44);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px),
    linear-gradient(0deg, rgba(255,255,255,.014) 1px, transparent 1px),
    repeating-linear-gradient(135deg, rgba(255,255,255,.035) 0 1px, transparent 1px 9px),
    radial-gradient(circle at 50% 0%, rgba(34, 215, 255, .14), transparent 36%),
    linear-gradient(135deg, #04080d 0%, #06111d 56%, #0a0d16 100%);
  background-size: 42px 42px, 42px 42px, auto, auto, auto;
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.cockpit { display: grid; grid-template-columns: 280px minmax(0, 1fr) 300px; gap: 16px; min-height: 100vh; padding: 16px; }
.left-rail, .right-rail { position: sticky; top: 16px; align-self: start; display: grid; gap: 14px; max-height: calc(100vh - 32px); overflow: auto; }
.brand, .rail-panel, .panel, .mini-card, .metric-tile, .group-card {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, .035), transparent 32%),
    linear-gradient(180deg, rgba(12, 24, 38, .96), rgba(5, 11, 20, .96));
  border: 1px solid rgba(34, 215, 255, .17);
  border-radius: 6px;
  box-shadow: 0 18px 52px var(--shadow), inset 0 1px 0 rgba(255, 255, 255, .055);
}
.brand { display: flex; align-items: center; gap: 12px; padding: 16px; }
.brand strong { display: block; font-size: 20px; }
.brand small { color: var(--muted); }
.pulse { width: 12px; height: 12px; border-radius: 50%; background: var(--green); box-shadow: 0 0 18px var(--green); }
.family-nav, .rail-section, .rail-panel { padding: 14px; }
.family-nav { display: grid; gap: 8px; }
.family-nav button { color: var(--ink); text-align: left; border: 1px solid rgba(55, 216, 255, .12); padding: 9px 10px; border-radius: 6px; background: rgba(55, 216, 255, .06); cursor: pointer; }
.family-nav button.active { border-color: rgba(73, 242, 161, .55); background: rgba(73, 242, 161, .12); }
h1, h2, h3, p { margin-top: 0; letter-spacing: 0; }
h1 { font-size: 44px; line-height: 1.02; margin-bottom: 14px; }
h2 { font-size: 20px; margin-bottom: 8px; }
h3 { font-size: 18px; margin-bottom: 8px; }
p, small, .empty { color: var(--muted); line-height: 1.5; }
.workspace { display: grid; gap: 16px; min-width: 0; }
.hero { min-height: 240px; display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(280px, .8fr); gap: 16px; align-items: stretch; padding: 24px; border: 1px solid rgba(55, 216, 255, .22); border-radius: 6px; background: linear-gradient(135deg, rgba(8, 18, 33, .92), rgba(13, 27, 47, .84)); box-shadow: inset 0 1px 0 rgba(255,255,255,.06), 0 22px 60px rgba(0,0,0,.32); }
.hero-copy { max-width: 680px; }
.eyebrow, .card-topline, dt { color: var(--cyan); font-size: 12px; text-transform: uppercase; font-weight: 760; }
.hero-grid, .status-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.hero-grid { grid-template-columns: 1fr; }
.metric-tile { padding: 14px; min-height: 88px; }
.metric-tile span, .summary-block span { display: block; color: var(--muted); font-size: 12px; text-transform: uppercase; font-weight: 760; }
.metric-tile strong, .summary-block strong { display: block; font-size: 24px; margin: 8px 0 4px; overflow-wrap: anywhere; }
.tabs { display: flex; gap: 8px; flex-wrap: wrap; padding: 8px; border: 1px solid rgba(55,216,255,.16); background: rgba(3, 8, 16, .5); border-radius: 8px; }
.tabs button { color: var(--ink); padding: 9px 13px; border-radius: 6px; background: rgba(55, 216, 255, .08); border: 1px solid rgba(55, 216, 255, .12); cursor: pointer; }
.tabs button.active { border-color: rgba(73, 242, 161, .55); background: rgba(73, 242, 161, .12); }
.panel { padding: 18px; }
.tab-panel { display: none; }
.tab-panel.active { display: block; }
.workflow-band { padding: 18px 22px; border: 1px solid rgba(55, 216, 255, .22); border-radius: 8px; background: linear-gradient(135deg, rgba(7, 17, 31, .94), rgba(10, 22, 39, .88)); }
.workflow-heading { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.workflow-heading h2 { margin: 0; }
.workflow-heading span, .step-pill { color: var(--ink); border: 1px solid rgba(55,216,255,.28); background: rgba(55,216,255,.12); border-radius: 999px; padding: 5px 11px; font-size: 13px; font-weight: 760; }
.workflow-steps { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; }
.workflow-step { position: relative; display: grid; gap: 8px; justify-items: center; min-height: 118px; padding: 14px 10px; border-radius: 8px; border: 1px solid rgba(55,216,255,.14); background: rgba(13,27,47,.64); text-align: center; }
.workflow-step:not(:last-child)::after { content: "->"; position: absolute; right: -12px; top: 45px; color: var(--cyan); font-weight: 900; z-index: 2; }
.workflow-step.active { border-color: rgba(73,242,161,.62); background: rgba(73,242,161,.09); box-shadow: inset 0 0 0 1px rgba(73,242,161,.18); }
.workflow-step.complete { border-color: rgba(55,216,255,.36); }
.workflow-step.locked { opacity: .78; }
.step-index { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, var(--cyan), var(--green)); color: #04101b; font-weight: 900; }
.workflow-step.locked .step-index { background: rgba(141,164,187,.24); color: var(--muted); }
.workflow-step strong { font-size: 15px; }
.workflow-step small { color: var(--muted); min-height: 20px; overflow-wrap: anywhere; }
.guided-grid { display: grid; grid-template-columns: minmax(220px, .95fr) minmax(260px, 1fr) minmax(260px, .9fr); gap: 14px; margin-bottom: 16px; }
.selected-group-card, .active-step-card, .command-shell { border: 1px solid rgba(55,216,255,.18); border-radius: 8px; background: rgba(3,8,16,.34); padding: 16px; }
.selected-group-card h2, .active-step-card h2, .command-shell h2 { font-size: 22px; line-height: 1.2; }
.auto-pipeline-panel { display: grid; grid-template-columns: minmax(230px, .85fr) minmax(320px, 1.25fr) minmax(220px, .8fr); gap: 14px; margin-bottom: 16px; }
.auto-flow-card, .pipeline-progress-card, .human-gates-card { border: 1px solid rgba(55,216,255,.2); border-radius: 8px; background: rgba(3,8,16,.36); padding: 16px; }
.auto-flow-card h2, .pipeline-progress-card h2, .human-gates-card h2 { font-size: 22px; line-height: 1.2; }
.auto-flow-card dl { margin-bottom: 14px; }
.compact-heading { align-items: center; margin-bottom: 10px; }
.overall-progress { margin-bottom: 10px; }
.progress-caption { margin-bottom: 13px; }
.pipeline-stage-list { display: grid; gap: 8px; }
.pipeline-stage { display: grid; grid-template-columns: 88px minmax(0, .8fr) minmax(0, 1.2fr); gap: 10px; align-items: center; border: 1px solid rgba(55,216,255,.13); border-radius: 8px; background: rgba(15,29,47,.44); padding: 10px; }
.pipeline-stage span { color: var(--muted); text-transform: uppercase; font-size: 11px; font-weight: 850; }
.pipeline-stage.complete span { color: var(--green); }
.pipeline-stage.review span,
.pipeline-stage.running span, .pipeline-stage.automatic span { color: var(--cyan); }
.pipeline-stage.manual.gate span, .pipeline-stage.manual span { color: var(--amber); }
.pipeline-stage small { color: var(--muted); overflow-wrap: anywhere; }
.flow-map { margin-bottom: 16px; padding: 16px; border: 1px solid rgba(55,216,255,.18); border-radius: 8px; background: rgba(3,8,16,.28); }
.flow-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; }
.flow-card { min-height: 128px; display: grid; align-content: start; gap: 8px; padding: 12px; border: 1px solid rgba(55,216,255,.14); border-radius: 8px; background: rgba(15,29,47,.44); }
.flow-card span { color: var(--muted); text-transform: uppercase; font-size: 11px; font-weight: 850; }
.flow-card strong { overflow-wrap: anywhere; }
.flow-card small { color: var(--muted); overflow-wrap: anywhere; }
.flow-card.complete { border-color: rgba(73,242,161,.28); background: rgba(73,242,161,.06); }
.flow-card.complete span { color: var(--green); }
.flow-card.current { border-color: rgba(55,216,255,.48); background: rgba(55,216,255,.08); box-shadow: inset 0 0 0 1px rgba(55,216,255,.16); }
.flow-card.current span { color: var(--cyan); }
.flow-card.gate, .flow-card.current.gate { border-color: rgba(240,198,91,.36); background: rgba(240,198,91,.06); }
.flow-card.gate span, .flow-card.current.gate span { color: var(--amber); }
.flow-context { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 12px; }
.flow-context .summary-block, .flow-context .empty { border: 1px solid rgba(55,216,255,.12); border-radius: 8px; background: rgba(15,29,47,.32); padding: 12px; margin: 0; }
.decision-strip {
  display: grid;
  grid-template-columns: 1.2fr 1fr .9fr .9fr .9fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}
.decision-cell {
  position: relative;
  min-height: 132px;
  padding: 15px;
  border: 1px solid rgba(34,215,255,.18);
  border-radius: 6px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.045), transparent 38%),
    linear-gradient(145deg, rgba(12,25,40,.88), rgba(4,10,18,.92));
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06), 0 14px 38px rgba(0,0,0,.24);
  overflow: hidden;
}
.decision-cell::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(34,215,255,.08), transparent);
  transform: translateX(-60%);
  opacity: .45;
  pointer-events: none;
}
.decision-cell span, .chart-head span {
  display: block;
  color: var(--muted);
  font-size: 11px;
  font-weight: 850;
  text-transform: uppercase;
}
.decision-cell strong {
  display: block;
  margin: 12px 0 8px;
  font-size: 20px;
  line-height: 1.14;
  overflow-wrap: anywhere;
}
.decision-cell small { display: block; color: var(--muted); }
.decision-cell.selected { border-left: 2px solid var(--cyan); }
.decision-cell.winner { border-left: 2px solid var(--green); }
.decision-cell.improvement { border-left: 2px solid var(--amber); }
.decision-cell.target { border-left: 2px solid var(--violet); }
.delta-positive { color: var(--green); }
.delta-negative { color: var(--red); }
.delta-neutral { color: var(--amber); }
.model-objective-panel {
  display: grid;
  grid-template-columns: minmax(360px, 1.05fr) minmax(360px, .95fr);
  gap: 14px;
  margin-bottom: 16px;
}
.model-selector,
.target-selector {
  padding: 16px;
  border: 1px solid rgba(34,215,255,.18);
  border-radius: 6px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.032), transparent 32%),
    rgba(4,10,18,.74);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 14px 38px rgba(0,0,0,.22);
}
.profile-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 10px;
}
.profile-card,
.target-card {
  display: grid;
  gap: 7px;
  min-height: 140px;
  width: 100%;
  padding: 13px;
  text-align: left;
  border: 1px solid rgba(55,216,255,.14);
  border-radius: 6px;
  background: rgba(7,17,31,.66);
}
.profile-card.active,
.target-card.active {
  border-color: rgba(73,242,161,.6);
  background: rgba(73,242,161,.09);
  box-shadow: inset 0 0 0 1px rgba(73,242,161,.16);
}
.profile-card span,
.target-card span {
  color: var(--cyan);
  font-size: 11px;
  font-weight: 850;
  text-transform: uppercase;
}
.profile-card strong,
.target-card strong {
  color: var(--ink);
  font-size: 16px;
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.profile-card small,
.target-card small,
.profile-card em {
  color: var(--muted);
  font-style: normal;
}
.profile-card code { display: inline-block; overflow-wrap: anywhere; }
.target-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.evidence-panel {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid rgba(34,215,255,.2);
  border-radius: 6px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.035), transparent 28%),
    linear-gradient(145deg, rgba(7,18,31,.9), rgba(3,8,15,.92));
  box-shadow: inset 0 1px 0 rgba(255,255,255,.055), 0 18px 48px rgba(0,0,0,.28);
}
.evidence-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
.chart-card {
  min-height: 220px;
  padding: 13px;
  border: 1px solid rgba(55,216,255,.14);
  border-radius: 6px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.03), transparent),
    rgba(5,12,22,.72);
}
.chart-head { display: flex; justify-content: space-between; gap: 10px; align-items: start; margin-bottom: 12px; }
.comparison-bars, .stability-list { display: grid; gap: 12px; }
.comparison-row { display: grid; grid-template-columns: 70px minmax(0, 1fr) 70px; gap: 8px; align-items: center; }
.comparison-row small { grid-column: 2 / -1; color: var(--muted); }
.evidence-bar-track, .stability-track {
  height: 12px;
  border-radius: 999px;
  background: rgba(141,164,187,.16);
  overflow: hidden;
}
.evidence-bar, .stability-track div {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--cyan), var(--green));
  box-shadow: 0 0 18px rgba(69,242,155,.22);
}
.scatter-plot {
  position: relative;
  height: 152px;
  border: 1px solid rgba(55,216,255,.12);
  border-radius: 6px;
  background:
    linear-gradient(90deg, rgba(55,216,255,.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(55,216,255,.08) 1px, transparent 1px),
    rgba(0,0,0,.18);
  background-size: 25% 25%;
}
.scatter-dot {
  position: absolute;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--cyan);
  border: 2px solid rgba(237,248,255,.9);
  transform: translate(-50%, 50%);
  box-shadow: 0 0 16px rgba(34,215,255,.46);
}
.scatter-dot.winner { width: 15px; height: 15px; background: var(--green); box-shadow: 0 0 20px rgba(69,242,155,.58); }
.scatter-dot.baseline { background: var(--amber); }
.scatter-dot.excluded { background: var(--red); }
.axis-row { display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: var(--muted); }
.stability-row { display: grid; grid-template-columns: minmax(0, 1fr) minmax(80px, 1fr) 72px; gap: 8px; align-items: center; }
.failure-heatmap { display: grid; grid-template-columns: repeat(auto-fit, minmax(78px, 1fr)); gap: 8px; }
.heat-cell {
  min-height: 64px;
  display: grid;
  align-content: center;
  gap: 4px;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid rgba(73,242,161,.22);
  background: rgba(73,242,161,.09);
}
.heat-cell.medium { border-color: rgba(240,198,91,.35); background: rgba(240,198,91,.1); }
.heat-cell.high, .heat-cell.excluded { border-color: rgba(255,107,107,.35); background: rgba(255,107,107,.1); }
.heat-cell strong { color: var(--ink); }
.heat-cell span { color: var(--muted); font-size: 11px; overflow-wrap: anywhere; }
.evidence-empty { border: 1px dashed rgba(55,216,255,.25); border-radius: 6px; padding: 18px; background: rgba(3,8,16,.34); }
.gate-list { display: grid; gap: 10px; padding: 0; margin: 14px 0 0; list-style: none; }
.gate-list li { display: grid; gap: 6px; border: 1px solid rgba(240,198,91,.22); border-radius: 8px; padding: 10px; background: rgba(240,198,91,.05); }
.fact-list { display: grid; gap: 8px; padding: 0; margin: 14px 0; list-style: none; }
.fact-list li { position: relative; min-height: 28px; padding: 7px 9px 7px 32px; border: 1px solid rgba(73,242,161,.16); border-radius: 8px; background: rgba(73,242,161,.06); }
.fact-list li::before { content: "✓"; position: absolute; left: 10px; color: var(--green); font-weight: 900; }
.fact-list.compact li { background: transparent; border: 0; padding-top: 3px; padding-bottom: 3px; }
.primary-action { width: 100%; min-height: 52px; color: white; border: 0; background: linear-gradient(135deg, #22b8ff, #4653ff); font-size: 16px; font-weight: 850; }
.next-note { margin: 14px 0 0; color: var(--amber); }
.command-shell pre { margin: 12px 0; padding: 14px; min-height: 108px; white-space: pre-wrap; overflow-wrap: anywhere; border: 1px solid rgba(55,216,255,.18); border-radius: 8px; background: rgba(0,0,0,.26); }
.command-shell pre code { display: block; border: 0; background: transparent; padding: 0; }
.what-next { margin-top: 14px; padding: 12px; border: 1px solid rgba(55,216,255,.14); border-radius: 8px; background: rgba(55,216,255,.06); }
.what-next strong { display: block; margin-bottom: 6px; }
.knobs-tuned-panel { margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(55,216,255,.14); }
.knobs-tuned-panel strong { display: block; margin-bottom: 8px; }
.knobs-tuned-panel ul { display: flex; flex-wrap: wrap; gap: 7px; margin: 0; padding: 0; list-style: none; }
.knobs-tuned-panel li { border: 1px solid rgba(55,216,255,.18); background: rgba(55,216,255,.08); border-radius: 999px; padding: 4px 8px; color: #dff9ff; font-family: "Cascadia Mono", Consolas, monospace; font-size: .86em; }
.next-action-card { border-color: rgba(55,216,255,.34); background: linear-gradient(180deg, rgba(10, 25, 45, .96), rgba(7, 14, 26, .96)); }
.next-action-card h2 { font-size: 22px; margin: 14px 0 10px; }
.after-this { border-top: 1px solid rgba(55,216,255,.15); margin-top: 16px; padding-top: 14px; }
.after-this ul { display: grid; gap: 7px; margin: 10px 0 0; padding-left: 18px; }
.section-heading { display: flex; justify-content: space-between; gap: 18px; align-items: end; margin-bottom: 16px; }
.section-heading p { max-width: 480px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.chips span, code { color: #dff9ff; border: 1px solid rgba(55,216,255,.18); background: rgba(55,216,255,.08); border-radius: 5px; padding: 3px 6px; font-family: "Cascadia Mono", Consolas, monospace; font-size: .88em; }
.group-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; }
.filter-bar { display: grid; gap: 8px; margin-bottom: 14px; }
.filter-bar label { color: var(--muted); font-size: 12px; text-transform: uppercase; font-weight: 760; }
.filter-bar input { width: 100%; min-height: 40px; color: var(--ink); background: rgba(3,8,16,.62); border: 1px solid rgba(55,216,255,.18); border-radius: 6px; padding: 9px 11px; }
.hidden { display: none !important; }
.group-card, .mini-card { padding: 14px; }
.mini-card { display: grid; gap: 5px; width: 100%; min-height: auto; text-align: left; }
.tuning-area-option.active { border-color: rgba(73,242,161,.72); background: rgba(73,242,161,.12); box-shadow: inset 0 0 0 1px rgba(73,242,161,.18); }
.mini-card span { color: var(--muted); }
.card-topline { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
.card-topline strong { color: var(--green); }
.risky-session .card-topline strong { color: var(--red); }
.session-tuning .card-topline strong { color: var(--violet); }
dl { display: grid; gap: 9px; margin: 14px 0 0; }
dd { margin: 2px 0 0; overflow-wrap: anywhere; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th, td { padding: 11px 9px; border-bottom: 1px solid rgba(55,216,255,.13); text-align: left; vertical-align: top; overflow-wrap: anywhere; }
th { color: var(--muted); font-size: 12px; text-transform: uppercase; }
.disabled-actions { display: flex; justify-content: space-between; gap: 14px; align-items: center; margin-top: 18px; padding: 14px; border: 1px dashed rgba(240,198,91,.45); border-radius: 8px; background: rgba(240,198,91,.06); }
button { min-width: 74px; min-height: 34px; border-radius: 6px; border: 1px solid rgba(55,216,255,.22); background: rgba(55,216,255,.09); color: var(--ink); margin: 3px; cursor: pointer; }
button:disabled { border-color: rgba(141,164,187,.3); background: rgba(141,164,187,.12); color: var(--muted); cursor: not-allowed; }
.safety-note { margin-top: 12px; }
.actions button { width: 100%; margin: 4px 0; }
.controller-feedback { min-height: 42px; margin: 10px 0 0; font-size: 13px; }
.help-dot { display: inline-grid; place-items: center; width: 18px; height: 18px; margin-left: 6px; border-radius: 50%; border: 1px solid rgba(55,216,255,.32); color: var(--cyan); font-size: 12px; font-weight: 800; vertical-align: middle; }
.operation-result { border: 1px solid rgba(73,242,161,.2); border-radius: 8px; background: rgba(73,242,161,.05); padding: 16px; margin: 16px 0; }
.operation-result.failed { border-color: rgba(255,107,107,.38); background: rgba(255,107,107,.07); }
.progress-track { height: 14px; border-radius: 999px; background: rgba(141,164,187,.16); overflow: hidden; margin-bottom: 14px; }
.progress-bar { height: 100%; width: 0; border-radius: 999px; background: linear-gradient(90deg, var(--cyan), var(--green)); transition: width .24s ease; }
.explain-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.explain-grid article { border: 1px solid rgba(55,216,255,.14); border-radius: 8px; background: rgba(3,8,16,.32); padding: 12px; }
.explain-grid strong { display: block; margin-bottom: 6px; }
.failure-diagnostics { margin-top: 12px; border: 1px solid rgba(255,107,107,.28); border-radius: 8px; background: rgba(3,8,16,.48); padding: 12px; }
.failure-diagnostics strong { display: block; margin-bottom: 6px; color: var(--red); }
.failure-diagnostics ul { display: grid; gap: 6px; margin: 8px 0 12px 18px; padding: 0; }
.failure-diagnostics dl { display: grid; grid-template-columns: minmax(120px, .45fr) minmax(0, 1fr); gap: 7px 10px; margin: 10px 0; }
.failure-diagnostics dt { color: var(--amber); }
.failure-diagnostics dd { margin: 0; overflow-wrap: anywhere; }
.failure-diagnostics code { display: inline-block; max-width: 100%; overflow-wrap: anywhere; }
.failed-trial-list { display: grid; gap: 8px; margin-top: 10px; }
.failed-trial-list article { border: 1px solid rgba(255,107,107,.18); border-radius: 8px; background: rgba(255,107,107,.06); padding: 9px; }
.how-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.how-card { border: 1px solid rgba(55,216,255,.16); border-radius: 8px; background: rgba(3,8,16,.38); padding: 14px; }
.how-card strong { display: block; margin-bottom: 8px; color: var(--ink); }
.report-card { border: 1px solid rgba(55,216,255,.16); border-radius: 8px; background: rgba(3,8,16,.38); padding: 16px; margin-bottom: 14px; }
.recommendation-card { display: grid; grid-template-columns: minmax(0, .9fr) minmax(0, 1.4fr); gap: 16px; }
.report-lists { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.report-lists h4 { margin: 0 0 8px; }
.decision-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.decision-grid article { display: grid; gap: 8px; align-content: start; border: 1px solid rgba(55,216,255,.14); border-radius: 8px; background: rgba(15,29,47,.44); padding: 12px; }
.decision-grid code { display: block; overflow-wrap: anywhere; }
.candidate-selector {
  border-color: rgba(69,242,155,.28);
  background:
    radial-gradient(circle at 8% 0, rgba(69,242,155,.12), transparent 32%),
    rgba(3,8,16,.42);
}
.candidate-choice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.candidate-choice {
  width: 100%;
  min-height: 118px;
  display: grid;
  gap: 8px;
  align-content: start;
  text-align: left;
  padding: 13px;
  border-radius: 12px;
  border: 1px solid rgba(141,221,255,.16);
  background: rgba(15,29,47,.54);
}
.candidate-choice.active {
  border-color: rgba(69,242,155,.72);
  background: rgba(69,242,155,.10);
  box-shadow: inset 0 0 0 1px rgba(69,242,155,.16), 0 0 28px rgba(69,242,155,.08);
}
.candidate-choice span {
  color: var(--cyan);
  font-size: 11px;
  font-weight: 850;
  text-transform: uppercase;
}
.candidate-choice small,
.candidate-gate-note {
  color: var(--muted);
}
.metric-visuals { display: grid; gap: 12px; margin-bottom: 16px; }
.metric-row { border: 1px solid rgba(55,216,255,.12); border-radius: 8px; padding: 12px; background: rgba(15,29,47,.58); }
.metric-row-head { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.metric-row-head span { color: var(--muted); }
.report-bar-line { display: grid; grid-template-columns: 92px minmax(0, 1fr) 78px; gap: 10px; align-items: center; margin-top: 8px; }
.report-bar-line span { color: var(--muted); }
.report-bar-track { height: 12px; border-radius: 999px; background: rgba(141,164,187,.16); overflow: hidden; }
.report-bar { height: 100%; border-radius: 999px; }
.report-bar.throughput { background: var(--green); }
.report-bar.latency { background: var(--cyan); }
.failure-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; }
.failure-item { border: 1px solid rgba(73,242,161,.18); border-radius: 8px; padding: 12px; background: rgba(73,242,161,.05); display: grid; gap: 6px; }
.failure-item.excluded { border-color: rgba(255,107,107,.28); background: rgba(255,107,107,.06); }
.failure-item span { color: var(--amber); font-weight: 780; }
.failure-item small { color: var(--muted); }
.promotion-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-bottom: 14px; }
.promotion-card { border: 1px solid rgba(55,216,255,.16); border-radius: 8px; background: rgba(3,8,16,.38); padding: 16px; }
.gate-card { border-color: rgba(240,198,91,.36); background: rgba(240,198,91,.06); }
.command-stack { display: grid; gap: 10px; }
.command-stack article { border: 1px solid rgba(55,216,255,.14); border-radius: 8px; background: rgba(15,29,47,.48); padding: 13px; display: grid; gap: 8px; }
.command-stack code { display: block; overflow-wrap: anywhere; }
.run-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.run-card { border: 1px solid rgba(55,216,255,.16); border-radius: 8px; background: rgba(3,8,16,.38); padding: 14px; }
.run-paths { display: grid; gap: 5px; margin-top: 10px; overflow-wrap: anywhere; }
@media (max-width: 1450px) {
  .cockpit { grid-template-columns: 240px minmax(0, 1fr) 280px; }
  .hero { grid-template-columns: 1fr; min-height: auto; }
  .hero-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .workflow-steps { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .flow-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .decision-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .evidence-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .model-objective-panel { grid-template-columns: 1fr; }
  .workflow-step:nth-child(3)::after { display: none; }
  .guided-grid, .auto-pipeline-panel { grid-template-columns: 1fr; }
  .command-shell { grid-column: auto; }
}
@media (max-width: 1180px) {
  .cockpit { grid-template-columns: 220px minmax(0, 1fr); }
  .right-rail { grid-column: 1 / -1; position: static; grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 820px) {
  .cockpit, .hero, .hero-grid, .status-grid, .right-rail { grid-template-columns: 1fr; }
  .left-rail, .right-rail { position: static; max-height: none; }
  .workspace { order: 1; }
  .left-rail { order: 2; }
  .right-rail { order: 3; }
  h1 { font-size: 34px; }
  .section-heading, .disabled-actions { display: block; }
  .recommendation-card, .report-lists, .report-bar-line, .promotion-grid, .explain-grid, .guided-grid, .auto-pipeline-panel, .workflow-steps, .pipeline-stage, .flow-grid, .flow-context, .decision-grid, .decision-strip, .evidence-grid, .model-objective-panel, .target-grid { grid-template-columns: 1fr; }
  .command-shell { grid-column: auto; }
  .workflow-heading { align-items: flex-start; flex-direction: column; }
  .workflow-step { justify-items: start; text-align: left; grid-template-columns: auto minmax(0, 1fr); align-items: center; min-height: 76px; }
  .workflow-step small { grid-column: 2; }
  .workflow-step::after { display: none; }
}

/* Objective command center redesign */
.objective-cockpit,
.objective-cockpit * {
  letter-spacing: 0;
}
.objective-cockpit {
  position: relative;
  width: min(1680px, calc(100vw - 40px));
  min-height: 100vh;
  margin: 0 auto;
  padding: 26px 0 46px;
}
.objective-cockpit::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 18% 10%, rgba(69, 242, 155, .12), transparent 26%),
    radial-gradient(circle at 76% 2%, rgba(158, 156, 255, .12), transparent 30%),
    linear-gradient(180deg, rgba(255,255,255,.04), transparent 26%);
  z-index: -1;
}
.command-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 28px;
}
.command-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.command-brand strong {
  display: block;
  font-size: 20px;
  line-height: 1.1;
}
.command-brand small {
  display: block;
  color: var(--muted);
  font-size: 13px;
  margin-top: 2px;
}
.command-orb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: conic-gradient(from 180deg, var(--green), var(--cyan), var(--violet), var(--green));
  box-shadow: 0 0 24px rgba(69, 242, 155, .4);
}
.command-status-strip {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}
.command-status-strip span {
  padding: 8px 11px;
  border: 1px solid rgba(141, 221, 255, .2);
  border-radius: 999px;
  color: rgba(237, 248, 255, .82);
  background: rgba(255,255,255,.045);
  font-size: 12px;
  font-weight: 750;
}
.command-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 390px);
  gap: 20px;
  align-items: stretch;
  margin-bottom: 18px;
}
.command-hero-copy {
  position: relative;
  overflow: hidden;
  min-height: 252px;
  padding: 30px;
  border: 1px solid rgba(99, 226, 255, .2);
  border-radius: 18px;
  background:
    linear-gradient(120deg, rgba(9, 24, 43, .92), rgba(4, 9, 18, .92)),
    linear-gradient(90deg, rgba(69, 242, 155, .08), rgba(34, 215, 255, .04));
  box-shadow: 0 28px 90px rgba(0, 0, 0, .34), inset 0 1px 0 rgba(255,255,255,.07);
}
.command-hero-copy::after {
  content: "";
  position: absolute;
  right: 28px;
  bottom: 22px;
  width: min(42%, 440px);
  height: 132px;
  border: 1px solid rgba(69, 242, 155, .2);
  border-radius: 16px;
  background:
    linear-gradient(90deg, rgba(69, 242, 155, .75) 0 68%, rgba(255,255,255,.12) 68%),
    linear-gradient(rgba(255,255,255,.08), rgba(255,255,255,.08));
  background-size: 100% 12px, 100% 100%;
  background-repeat: no-repeat;
  background-position: 0 24px, 0 0;
  opacity: .46;
}
.command-hero h1 {
  position: relative;
  max-width: 870px;
  margin: 0;
  font-size: clamp(40px, 4.7vw, 68px);
  line-height: .96;
  z-index: 1;
}
.command-hero p {
  position: relative;
  max-width: 760px;
  margin: 20px 0 0;
  color: rgba(237, 248, 255, .74);
  font-size: 18px;
  line-height: 1.58;
  z-index: 1;
}
.decision-story-card,
.command-panel,
.decision-story,
.advanced-shell {
  border: 1px solid rgba(99, 226, 255, .19);
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.055), transparent 32%),
    rgba(5, 14, 27, .82);
  box-shadow: 0 22px 70px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.06);
}
.decision-story-card {
  display: grid;
  align-content: space-between;
  min-height: 252px;
  padding: 24px;
  background:
    radial-gradient(circle at 80% 12%, rgba(69, 242, 155, .16), transparent 38%),
    linear-gradient(180deg, rgba(12, 30, 49, .95), rgba(5, 12, 24, .95));
}
.decision-story-card span,
.command-section-head span,
.story-grid span {
  color: var(--cyan);
  font-size: 12px;
  font-weight: 850;
  text-transform: uppercase;
}
.decision-story-card > strong {
  display: block;
  margin: 18px 0;
  font-size: 28px;
  line-height: 1.08;
}
.decision-story-card code,
.story-grid code {
  white-space: normal;
  overflow-wrap: anywhere;
}
.decision-story-card dl,
.recipe-facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
}
.decision-story-card dt,
.recipe-facts dt {
  color: var(--muted);
  font-size: 12px;
}
.decision-story-card dd,
.recipe-facts dd {
  margin: 2px 0 0;
  color: var(--ink);
  font-weight: 850;
}
.command-setup-grid,
.command-runway {
  display: grid;
  gap: 16px;
  margin-bottom: 16px;
}
.command-setup-grid {
  grid-template-columns: minmax(260px, .8fr) minmax(380px, 1.15fr) minmax(300px, .8fr);
}
.command-runway {
  grid-template-columns: minmax(300px, .76fr) minmax(420px, 1.1fr) minmax(320px, .86fr);
}
.command-panel {
  min-width: 0;
  padding: 18px;
}
.command-section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 14px;
}
.command-section-head strong {
  color: var(--ink);
  font-size: 20px;
  line-height: 1.16;
  text-align: right;
}
.model-panel .profile-strip {
  display: grid;
  grid-auto-flow: row;
  grid-template-columns: 1fr;
}
.objective-panel .target-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.objective-cockpit .profile-card,
.objective-cockpit .target-card {
  min-height: 116px;
  border-radius: 12px;
  background: rgba(13, 29, 48, .72);
}
.objective-cockpit .profile-card.active,
.objective-cockpit .target-card.active {
  border-color: rgba(69, 242, 155, .74);
  box-shadow: inset 0 0 0 1px rgba(69, 242, 155, .18), 0 12px 34px rgba(69, 242, 155, .08);
}
.selected-objective-summary {
  display: grid;
  gap: 4px;
  margin-top: 14px;
  padding: 12px;
  border: 1px solid rgba(69, 242, 155, .18);
  border-radius: 12px;
  background: rgba(69, 242, 155, .06);
}
.selected-objective-summary span {
  color: var(--green);
  font-size: 12px;
  font-weight: 850;
  text-transform: uppercase;
}
.selected-objective-summary strong {
  font-size: 18px;
}
.selected-objective-summary small {
  color: var(--muted);
}
.recipe-panel p {
  color: var(--muted);
  line-height: 1.48;
}
.compact-knobs {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(141, 221, 255, .14);
}
.compact-knobs ul {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  padding: 0;
  margin: 10px 0 0;
  list-style: none;
}
.compact-knobs li {
  padding: 6px 9px;
  border-radius: 999px;
  color: rgba(237,248,255,.86);
  background: rgba(255,255,255,.07);
  font-size: 12px;
}
.loaded-run-controls {
  display: grid;
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(141, 221, 255, .14);
}
.loaded-run-controls span {
  color: var(--amber);
  font-size: 12px;
  font-weight: 850;
  text-transform: uppercase;
}
.loaded-run-controls div {
  display: grid;
  grid-template-columns: .82fr 1fr;
  gap: 10px;
}
.loaded-run-controls.compact div {
  grid-template-columns: 1fr;
}
.secondary-action {
  width: 100%;
  min-height: 48px;
  border: 1px solid rgba(141, 221, 255, .25);
  border-radius: 12px;
  color: var(--ink);
  background: rgba(255, 255, 255, .055);
  font-size: 14px;
  font-weight: 850;
  cursor: pointer;
}
.secondary-action:hover {
  border-color: rgba(34, 215, 255, .55);
  background: rgba(34, 215, 255, .09);
}
.fresh-run-card {
  border-color: rgba(69, 242, 155, .35);
}
.primary-command-card {
  background:
    radial-gradient(circle at 12% 8%, rgba(69, 242, 155, .13), transparent 34%),
    linear-gradient(180deg, rgba(12, 30, 49, .95), rgba(5, 12, 24, .95));
}
.objective-cockpit .primary-action {
  border-radius: 12px;
  background: linear-gradient(100deg, #1bc7ff, #5264ff 54%, #45f29b);
  box-shadow: 0 18px 42px rgba(34, 215, 255, .18);
}
.progress-head strong {
  min-width: 66px;
  text-align: right;
}
.progress-head em {
  color: var(--muted);
  font-style: normal;
  font-size: 13px;
  margin-left: auto;
}
.command-stage-list {
  display: grid;
  gap: 8px;
  margin-top: 14px;
}
.command-gates {
  margin-top: 14px;
}
.command-gates .gate-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}
.command-gates .gate-list li {
  margin: 0;
}
.command-stage-list .pipeline-stage {
  grid-template-columns: 82px minmax(0, .92fr) minmax(0, 1.35fr);
  border-radius: 12px;
}
.live-command-card .live-execution {
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}
.live-command-card .operation-result {
  margin-top: 16px;
  padding: 16px 0 0;
  border: 0;
  border-top: 1px solid rgba(141, 221, 255, .14);
  background: transparent;
  box-shadow: none;
}
.live-command-card .operation-result .section-heading {
  align-items: center;
}
.live-command-card .explain-grid {
  grid-template-columns: 1fr;
}
.decision-story {
  margin-bottom: 16px;
  padding: 20px;
}
.story-heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}
.story-heading h2 {
  font-size: 30px;
}
.story-heading p {
  max-width: 620px;
  color: var(--muted);
  line-height: 1.45;
}
.story-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
.story-grid article {
  min-height: 132px;
  padding: 16px;
  border: 1px solid rgba(141, 221, 255, .15);
  border-radius: 14px;
  background: rgba(255,255,255,.045);
}
.story-grid strong {
  display: block;
  margin: 12px 0 8px;
  font-size: 26px;
  line-height: 1.05;
}
.story-grid small {
  color: var(--muted);
}
.winner-story {
  border-color: rgba(69, 242, 155, .45) !important;
  background: rgba(69, 242, 155, .08) !important;
}
.advanced-command-center {
  margin-top: 18px;
}
.advanced-shell {
  overflow: hidden;
}
.advanced-shell > summary {
  display: grid;
  grid-template-columns: minmax(0, .4fr) minmax(0, 1fr);
  gap: 16px;
  align-items: center;
  padding: 20px;
  cursor: pointer;
  list-style: none;
}
.advanced-shell > summary::-webkit-details-marker {
  display: none;
}
.advanced-shell > summary span {
  color: var(--cyan);
  font-size: 12px;
  font-weight: 850;
  text-transform: uppercase;
}
.advanced-shell > summary strong {
  font-size: 20px;
}
.advanced-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 16px;
  padding: 0 20px 20px;
}
.advanced-rail {
  display: grid;
  align-content: start;
  gap: 14px;
  min-width: 0;
}
.advanced-workspace {
  display: grid;
  gap: 16px;
  min-width: 0;
}
.advanced-family-nav,
.advanced-recipe-list {
  border: 1px solid rgba(141, 221, 255, .14);
  border-radius: 14px;
  background: rgba(255,255,255,.035);
}
.advanced-recipe-list {
  max-height: 520px;
  overflow: auto;
}
.advanced-recipe-list .mini-card {
  width: 100%;
}
.advanced-workspace .tabs {
  position: sticky;
  top: 0;
  z-index: 3;
  backdrop-filter: blur(12px);
}
.advanced-workspace .decision-strip,
.advanced-workspace .workflow-band {
  display: none;
}
@media (max-width: 1280px) {
  .command-setup-grid,
  .command-runway,
  .command-hero {
    grid-template-columns: 1fr;
  }
  .decision-story-card,
  .command-hero-copy {
    min-height: auto;
  }
  .story-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 900px) {
  .objective-cockpit {
    width: min(100% - 24px, 1680px);
    padding-top: 18px;
  }
  .command-topbar,
  .story-heading,
  .command-section-head {
    align-items: flex-start;
    flex-direction: column;
  }
  .command-section-head strong {
    text-align: left;
  }
  .command-status-strip {
    justify-content: flex-start;
  }
  .command-hero-copy {
    padding: 24px;
  }
  .command-hero h1 {
    font-size: 42px;
  }
  .command-hero-copy::after {
    display: none;
  }
  .objective-panel .target-grid,
  .story-grid,
  .decision-story-card dl,
  .recipe-facts,
  .advanced-layout {
    grid-template-columns: 1fr;
  }
  .command-stage-list .pipeline-stage {
    grid-template-columns: 1fr;
  }
  .command-gates .gate-list {
    grid-template-columns: 1fr;
  }
  .loaded-run-controls div {
    grid-template-columns: 1fr;
  }
  .advanced-shell > summary {
    grid-template-columns: 1fr;
  }
}
"""

JS = """
const state = {
  tab: 'overview',
  family: 'all',
  query: '',
  currentJobId: null,
  pollTimer: null,
  selectedObjective: 'balanced',
  selectedCandidateId: '',
  selectedCandidateObjective: '',
  reportAutoOpened: false
};

function setActiveTab(tab) {
  state.tab = tab;
  document.querySelectorAll('[data-tab-target]').forEach((button) => {
    button.classList.toggle('active', button.dataset.tabTarget === tab);
  });
  document.querySelectorAll('[data-tab-panel]').forEach((panel) => {
    panel.classList.toggle('active', panel.dataset.tabPanel === tab);
  });
}

function openDetailPanel(tab) {
  const details = document.getElementById('advanced-cockpit-details') || document.querySelector('.advanced-shell');
  if (details) details.open = true;
  setActiveTab(tab);
  const panel = document.querySelector('[data-tab-panel="' + tab + '"]');
  if (panel) {
    window.setTimeout(() => panel.scrollIntoView({ behavior: 'smooth', block: 'start' }), 30);
  }
}

function safeSessionSet(key, value) {
  try {
    window.sessionStorage.setItem(key, value);
  } catch (_error) {
    state[key] = value;
  }
}

function safeSessionGet(key) {
  try {
    return window.sessionStorage.getItem(key);
  } catch (_error) {
    return state[key] || null;
  }
}

function safeSessionRemove(key) {
  try {
    window.sessionStorage.removeItem(key);
  } catch (_error) {
    delete state[key];
  }
}

function applyGroupFilters() {
  const query = state.query.trim().toLowerCase();
  let gridVisible = 0;
  let railVisible = 0;
  document.querySelectorAll('.group-card, .tuning-area-option').forEach((card) => {
    const familyMatch = state.family === 'all' || card.dataset.family === state.family;
    const queryMatch = !query || (card.dataset.search || '').includes(query);
    const railItem = card.classList.contains('tuning-area-option');
    const show = familyMatch && (railItem || queryMatch);
    card.classList.toggle('hidden', !show);
    if (show && railItem) railVisible += 1;
    if (show && !railItem) gridVisible += 1;
  });
  const count = document.getElementById('visible-group-count');
  if (count) count.textContent = String(gridVisible);
  const empty = document.getElementById('group-empty-state');
  if (empty) empty.classList.toggle('hidden', gridVisible !== 0);
  const railEmpty = document.getElementById('rail-empty-state');
  if (railEmpty) railEmpty.classList.toggle('hidden', railVisible !== 0);
  syncSelectedTuningArea();
}

function syncSelectedTuningArea() {
  const active = document.querySelector('.tuning-area-option.active');
  if (active && !active.classList.contains('hidden')) return;
  const firstVisible = Array.from(document.querySelectorAll('.tuning-area-option')).find((item) => !item.classList.contains('hidden'));
  if (firstVisible) selectTuningArea(firstVisible);
}

document.querySelectorAll('[data-tab-target]').forEach((button) => {
  button.addEventListener('click', () => setActiveTab(button.dataset.tabTarget));
});

document.querySelectorAll('[data-family-filter]').forEach((button) => {
  button.addEventListener('click', () => {
    state.family = button.dataset.familyFilter || 'all';
    document.querySelectorAll('[data-family-filter]').forEach((item) => {
      item.classList.toggle('active', item === button);
    });
    openDetailPanel('knobs');
    applyGroupFilters();
  });
});

const search = document.getElementById('knob-search');
if (search) {
  search.addEventListener('input', () => {
    state.query = search.value;
    applyGroupFilters();
  });
}

function selectTuningArea(button) {
  const label = button.dataset.tuningAreaLabel || 'Unnamed tuning area';
  const description = button.dataset.tuningAreaDescription || 'No description.';
  const knobs = (button.dataset.knobsTuned || '').split('|').filter(Boolean);
  document.querySelectorAll('[data-tuning-area-id]').forEach((item) => {
    item.classList.toggle('active', item.dataset.tuningAreaId === button.dataset.tuningAreaId);
  });
  const labelTarget = document.getElementById('selected-tuning-area-label');
  const descriptionTarget = document.getElementById('selected-tuning-area-description');
  const knobsTarget = document.getElementById('selected-knobs-tuned');
  const autoFlowTarget = document.getElementById('auto-flow-selected-area');
  if (labelTarget) labelTarget.textContent = label;
  if (autoFlowTarget) autoFlowTarget.textContent = label;
  if (descriptionTarget) descriptionTarget.textContent = description;
  if (knobsTarget) {
    knobsTarget.innerHTML = '';
    if (knobs.length === 0) {
      const item = document.createElement('li');
      item.textContent = 'No knob metadata loaded.';
      knobsTarget.appendChild(item);
    } else {
      knobs.forEach((knob) => {
        const item = document.createElement('li');
        item.textContent = knob;
        knobsTarget.appendChild(item);
      });
    }
  }
}

function selectObjectiveTarget(button) {
  const label = button.dataset.targetLabel || 'Balanced';
  const description = button.dataset.targetDescription || 'Blend throughput, latency, failure rate, and safety.';
  const target = button.dataset.objectiveTarget || 'balanced';
  state.selectedObjective = objectiveForTarget(target);
  document.querySelectorAll('[data-objective-target]').forEach((item) => {
    item.classList.toggle('active', item === button);
  });
  const labelTarget = document.getElementById('selected-objective-label');
  const descriptionTarget = document.getElementById('selected-objective-description');
  const flowTarget = document.getElementById('auto-flow-selected-target');
  if (labelTarget) labelTarget.textContent = label;
  if (descriptionTarget) descriptionTarget.textContent = description;
  if (flowTarget) flowTarget.textContent = label;
}

function objectiveForTarget(target) {
  if (target === 'performance') return 'throughput';
  if (target === 'single_user') return 'single_user';
  if (target === 'stability' || target === 'tool_use') return 'balanced';
  return target || 'balanced';
}

function selectedCandidateId() {
  const active = document.querySelector('[data-candidate-select].active');
  const holder = document.querySelector('[data-selected-candidate-id]');
  return state.selectedCandidateId || (active ? active.dataset.candidateId : '') || (holder ? holder.dataset.selectedCandidateId : '');
}

function selectedPromotionObjective() {
  const active = document.querySelector('[data-candidate-select].active');
  const holder = document.querySelector('[data-selected-objective]');
  return state.selectedCandidateObjective || (active ? active.dataset.candidateObjective : '') || (holder ? holder.dataset.selectedObjective : '') || state.selectedObjective || 'balanced';
}

function selectPromotionCandidate(button) {
  const candidateId = button.dataset.candidateId || button.dataset.candidateSelect || '';
  const objective = button.dataset.candidateObjective || selectedPromotionObjective();
  if (!candidateId) return;
  state.selectedCandidateId = candidateId;
  state.selectedCandidateObjective = objective;
  document.querySelectorAll('[data-candidate-select]').forEach((item) => {
    const active = item.dataset.candidateId === candidateId;
    item.classList.toggle('active', active);
    const label = item.querySelector('span');
    if (label) label.textContent = active ? 'Selected' : 'Candidate';
  });
  document.querySelectorAll('[data-selected-candidate-id]').forEach((item) => {
    item.dataset.selectedCandidateId = candidateId;
    item.dataset.selectedObjective = objective;
  });
  document.querySelectorAll('#selected-candidate-id').forEach((item) => {
    item.textContent = candidateId;
  });
  document.querySelectorAll('#selected-candidate-objective').forEach((item) => {
    item.textContent = objective;
  });
  document.querySelectorAll('#promotion-selected-candidate').forEach((item) => {
    item.textContent = candidateId;
  });
}

function selectProfileCard(button) {
  document.querySelectorAll('[data-profile-card]').forEach((item) => {
    item.classList.toggle('active', item === button);
  });
}

async function copyControllerCommand(button) {
  const command = button.dataset.controllerCommand || '';
  const action = button.dataset.controllerAction || 'action';
  const feedback = document.getElementById('controller-feedback');
  if (!command) {
    if (feedback) feedback.textContent = 'No command is available for ' + action + '.';
    return;
  }
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(command);
      if (feedback) feedback.textContent = 'Copied ' + action + ' command to clipboard.';
    } else {
      throw new Error('Clipboard API unavailable');
    }
  } catch (_error) {
    if (feedback) feedback.textContent = action + ' command: ' + command;
  }
}

async function runControllerAction(button) {
  if (button.dataset.tabJump) {
    if (button.dataset.refreshTab === 'true') {
      openDetailPanel(button.dataset.tabJump);
      safeSessionSet('cockpit-tab-after-reload', button.dataset.tabJump);
      window.setTimeout(() => window.location.reload(), 50);
      return;
    }
    openDetailPanel(button.dataset.tabJump);
    return;
  }
  const endpoint = button.dataset.controllerEndpoint || '';
  const action = button.dataset.controllerAction || 'action';
  const feedback = document.getElementById('controller-feedback');
  const activeServer = window.location.protocol === 'http:' || window.location.protocol === 'https:';
  if (!activeServer || !endpoint) {
    await copyControllerCommand(button);
    return;
  }
  const payload = {};
  if (action === 'run') {
    const confirmed = window.confirm('Run can execute on the GX10. Continue with the confirmed live run gate?');
    if (!confirmed) {
      if (feedback) feedback.textContent = 'Run cancelled before remote execution.';
      return;
    }
    payload.confirm_live_run = true;
  }
  if (action === 'promote') {
    payload.candidate_id = selectedCandidateId();
    payload.objective = selectedPromotionObjective();
    if (!payload.candidate_id) {
      if (feedback) feedback.textContent = 'Select a candidate before promotion.';
      return;
    }
    const confirmed = window.confirm('Promotion writes a selected-candidate profile artifact under the cockpit output directory. Continue?');
    if (!confirmed) {
      if (feedback) feedback.textContent = 'Promotion cancelled before writing a profile artifact.';
      return;
    }
  }
  renderOperationResult({
    action,
    status: 'running',
    progress_percent: 5,
    plain_summary: {
      what_happened: 'I am starting ' + action + '.',
      what_it_means: 'The local controller got your request.',
      next_step: 'Watch the progress bar.'
    }
  });
  resetWorkflowForNewOperation(action);
  if (feedback) feedback.textContent = 'Running ' + action + '...';
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok || result.status === 'error') {
      throw new Error(result.error || 'Controller request failed');
    }
    if (result.job_id) {
      state.currentJobId = result.job_id;
      renderOperationResult(result);
      pollControllerJob(result.job_id);
      if (feedback) feedback.textContent = action + ' started.';
      return;
    }
    renderOperationResult(result);
    if (feedback) feedback.textContent = action + ' completed.';
  } catch (error) {
    renderOperationResult({
      action,
      status: 'failed',
      progress_percent: 100,
      plain_summary: {
        what_happened: action + ' did not finish.',
        what_it_means: error.message,
        next_step: 'Check the message and try again.'
      }
    });
    if (feedback) feedback.textContent = action + ' failed: ' + error.message;
  }
}

function renderOperationResult(job) {
  const panel = document.querySelector('.operation-result');
  const title = document.getElementById('operation-title');
  const bar = document.getElementById('operation-progress-bar');
  const what = document.getElementById('operation-what');
  const meaning = document.getElementById('operation-meaning');
  const next = document.getElementById('operation-next');
  const cancel = document.getElementById('operation-cancel');
  const liveTitle = document.getElementById('live-execution-title');
  const liveStatus = document.getElementById('live-execution-status');
  const liveElapsed = document.getElementById('live-execution-elapsed');
  const liveBar = document.getElementById('live-execution-progress-bar');
  const liveSummary = document.getElementById('live-execution-summary');
  const summary = job.plain_summary || {};
  const progress = Math.max(0, Math.min(100, Number(job.progress_percent || 0)));
  const actionLabel = formatActionLabel(job.action || 'action');
  const statusLabel = job.status || 'unknown';
  const elapsed = Number(job.elapsed_seconds || 0);
  if (panel) panel.classList.toggle('failed', statusLabel === 'failed');
  if (title) title.textContent = actionLabel + ': ' + statusLabel;
  if (bar) bar.style.width = progress + '%';
  if (what) what.textContent = summary.what_happened || 'The controller updated this operation.';
  if (meaning) meaning.textContent = summary.what_it_means || 'The cockpit is waiting for more details.';
  if (next) next.textContent = summary.next_step || 'Choose the next safe step.';
  if (liveTitle) liveTitle.textContent = actionLabel;
  if (liveStatus) liveStatus.textContent = statusLabel;
  if (liveElapsed) liveElapsed.textContent = elapsed ? elapsed + 's elapsed' : 'Just started';
  if (liveBar) liveBar.style.width = progress + '%';
  if (liveSummary) liveSummary.textContent = summary.what_happened || 'Operation state updated.';
  renderFailureDiagnostics(job);
  updatePipelineFromJob(job);
  updateNextActionFromJob(job);
  autoOpenReportAfterCompletion(job);
  if (cancel) {
    cancel.disabled = !job.job_id || !['running', 'cancel-requested'].includes(job.status);
    cancel.dataset.jobId = job.job_id || '';
  }
}

function renderFailureDiagnostics(job) {
  const panel = document.getElementById('operation-diagnostics');
  if (!panel) return;
  const diagnostics = job.diagnostics || null;
  if (job.status !== 'failed' || !diagnostics) {
    panel.classList.add('hidden');
    return;
  }
  panel.classList.remove('hidden');
  const cause = document.getElementById('operation-failure-cause');
  const steps = document.getElementById('operation-failure-steps');
  const artifacts = document.getElementById('operation-failure-artifacts');
  const trials = document.getElementById('operation-failed-trials');
  if (cause) cause.textContent = diagnostics.likely_cause || diagnostics.error || 'The controller reported a failure.';
  if (steps) {
    steps.innerHTML = '';
    (Array.isArray(diagnostics.next_steps) ? diagnostics.next_steps : []).forEach((step) => {
      const li = document.createElement('li');
      li.textContent = step;
      steps.appendChild(li);
    });
  }
  if (artifacts) {
    artifacts.innerHTML = '';
    Object.entries(diagnostics.artifacts || {}).forEach(([label, path]) => {
      const dt = document.createElement('dt');
      const dd = document.createElement('dd');
      const code = document.createElement('code');
      dt.textContent = label.replace(/_/g, ' ');
      code.textContent = String(path || '');
      dd.appendChild(code);
      artifacts.appendChild(dt);
      artifacts.appendChild(dd);
    });
  }
  if (trials) {
    trials.innerHTML = '';
    const failedTrials = Array.isArray(diagnostics.failed_trials) ? diagnostics.failed_trials : [];
    if (failedTrials.length) {
      const wrap = document.createElement('div');
      wrap.className = 'failed-trial-list';
      failedTrials.forEach((trial) => {
        const item = document.createElement('article');
        const strong = document.createElement('strong');
        const p = document.createElement('p');
        strong.textContent = trial.trial_id || trial.candidate_id || 'failed trial';
        p.textContent = trial.failure_reason || 'No failure reason was recorded.';
        item.appendChild(strong);
        item.appendChild(p);
        wrap.appendChild(item);
      });
      trials.appendChild(wrap);
    }
  }
}

function autoOpenReportAfterCompletion(job) {
  if (state.reportAutoOpened) return;
  if (job.action !== 'report' || job.status !== 'completed') return;
  state.reportAutoOpened = true;
  safeSessionSet('cockpit-tab-after-reload', 'reports');
  const feedback = document.getElementById('controller-feedback');
  if (feedback) feedback.textContent = 'Report generated. Opening report...';
  window.setTimeout(() => window.location.reload(), 120);
}

function updatePipelineFromJob(job) {
  const summary = job.pipeline_summary || (job.result && job.result.pipeline_summary) || {};
  let completed = Array.isArray(summary.completed_stages) ? summary.completed_stages : [];
  if (completed.length === 0 && job.action === 'run' && ['running', 'cancel-requested'].includes(job.status)) {
    resetWorkflowForNewOperation('run');
    return;
  }
  if (completed.length === 0 && job.action === 'run' && job.status === 'completed') {
    completed = ['plan', 'preview', 'run'];
  }
  if (completed.length === 0) return;
  const stageOrder = ['plan', 'preview', 'run', 'report', 'confirm', 'promote'];
  const normalized = completed.map((stage) => stage === 'confirmation-benchmarks' ? 'confirm' : stage);
  let highest = 0;
  normalized.forEach((stage) => {
    const index = stageOrder.indexOf(stage);
    if (index >= 0) highest = Math.max(highest, index + 1);
  });
  const nextStage = stageOrder[highest] || 'promote';
  document.querySelectorAll('[data-pipeline-stage]').forEach((item) => {
    const stage = item.dataset.pipelineStage;
    const state = item.querySelector('span');
    item.classList.remove('complete', 'running', 'automatic', 'manual', 'gate', 'waiting');
    if (normalized.includes(stage)) {
      item.classList.add('complete');
      if (state) state.textContent = 'Complete';
    } else if (stage === nextStage && stage !== 'promote') {
      item.classList.add('automatic');
      if (state) state.textContent = 'Next';
    } else if (stage === 'promote') {
      item.classList.add('manual', 'gate');
      if (state) state.textContent = 'Manual Gate';
    } else {
      item.classList.add('waiting');
      if (state) state.textContent = 'Waiting';
    }
  });
  const progressByStage = { plan: 20, preview: 32, run: 64, report: 72, confirm: 84, promote: 92 };
  const lastStage = stageOrder[Math.max(0, highest - 1)] || 'plan';
  const progress = progressByStage[lastStage] || 8;
  const progressBar = document.getElementById('pipeline-overall-progress-bar');
  const progressLabel = document.getElementById('pipeline-overall-progress-label');
  const caption = document.getElementById('pipeline-caption');
  if (progressBar) progressBar.style.width = progress + '%';
  if (progressLabel) progressLabel.textContent = progress + '%';
  if (caption) caption.textContent = pipelineCaptionForCompleted(normalized);
  updateWorkflowBand(normalized, nextStage);
  updateFlowMap(normalized, nextStage);
}

function updateNextActionFromJob(job) {
  const summary = job.pipeline_summary || (job.result && job.result.pipeline_summary) || {};
  let completed = Array.isArray(summary.completed_stages) ? summary.completed_stages : [];
  if (job.action === 'run' && ['running', 'cancel-requested'].includes(job.status)) {
    setRunningOptimizationAction();
    return;
  }
  if (completed.length === 0 && job.action === 'run' && job.status === 'completed') {
    completed = ['plan', 'preview', 'run'];
  }
  if (completed.includes('report')) {
    setReviewReportAction();
    return;
  }
  if (!completed.includes('run')) return;
  const headline = document.getElementById('next-action-headline');
  const description = document.getElementById('next-action-description');
  const facts = document.getElementById('next-action-facts');
  const button = document.getElementById('next-action-button');
  const reportCommand = commandForAction('report');
  if (headline) headline.textContent = 'Generate & Review Report';
  if (description) description.textContent = 'Run artifacts are ready. Generate the report so the cockpit can rank candidates and explain the recommendation.';
  if (facts) {
    facts.innerHTML = '<li>Uses completed artifacts</li><li>No remote execution</li><li>Opens the report automatically</li>';
  }
  if (button) {
    configureControllerButton(button, 'report', '/api/controller/report', reportCommand, 'Generate & Review Report');
  }
}

function resetWorkflowForNewOperation(action) {
  if (action !== 'run') return;
  document.querySelectorAll('[data-pipeline-stage]').forEach((item) => {
    const stage = item.dataset.pipelineStage;
    const state = item.querySelector('span');
    item.classList.remove('complete', 'running', 'automatic', 'manual', 'gate', 'waiting');
    if (stage === 'plan') {
      item.classList.add('automatic');
      if (state) state.textContent = 'Next';
    } else if (stage === 'promote') {
      item.classList.add('manual', 'gate');
      if (state) state.textContent = 'Manual Gate';
    } else {
      item.classList.add('waiting');
      if (state) state.textContent = 'Waiting';
    }
  });
  updateWorkflowBand([], 'plan');
  updateFlowMap([], 'plan');
  const progressBar = document.getElementById('pipeline-overall-progress-bar');
  const progressLabel = document.getElementById('pipeline-overall-progress-label');
  const caption = document.getElementById('pipeline-caption');
  if (progressBar) progressBar.style.width = '8%';
  if (progressLabel) progressLabel.textContent = '8%';
  if (caption) caption.textContent = 'Starting optimization. Prior run state has been cleared for this run.';
}

function updateWorkflowBand(completed, nextStage) {
  document.querySelectorAll('[data-workflow-step]').forEach((item) => {
    const stage = item.dataset.workflowStep;
    const label = item.querySelector('small');
    item.classList.remove('complete', 'active', 'locked');
    if (completed.includes(stage)) {
      item.classList.add('complete');
      if (label) label.textContent = 'Done';
    } else if (stage === nextStage) {
      item.classList.add('active');
      if (label) label.textContent = 'Ready';
    } else {
      item.classList.add('locked');
      if (label) label.textContent = stage === 'promote' ? 'Manual Gate' : 'Locked';
    }
  });
}

function updateFlowMap(completed, nextStage) {
  document.querySelectorAll('[data-flow-step]').forEach((item) => {
    const stage = item.dataset.flowStep;
    const label = item.querySelector('span');
    item.classList.remove('complete', 'current', 'gate', 'waiting');
    if (completed.includes(stage)) {
      item.classList.add('complete');
      if (label) label.textContent = 'Done';
    } else if (stage === nextStage) {
      item.classList.add('current');
      if (label) label.textContent = stage === 'confirm' ? 'Review' : 'Current';
    } else if (['confirm', 'promote'].includes(stage)) {
      item.classList.add('gate');
      if (label) label.textContent = 'Gate';
    } else {
      item.classList.add('waiting');
      if (label) label.textContent = 'Waiting';
    }
  });
}

function setRunningOptimizationAction() {
  const headline = document.getElementById('next-action-headline');
  const description = document.getElementById('next-action-description');
  const facts = document.getElementById('next-action-facts');
  const button = document.getElementById('next-action-button');
  if (headline) headline.textContent = 'Optimization Running';
  if (description) description.textContent = 'The new run is active. Progress and stages now reflect this run, not the previous report.';
  if (facts) {
    facts.innerHTML = '<li>Fresh run state</li><li>Progress reset</li><li>Cancel available below</li>';
  }
  if (button) {
    button.textContent = 'Optimization Running';
    button.disabled = true;
    button.classList.remove('hidden');
    delete button.dataset.controllerAction;
    delete button.dataset.controllerEndpoint;
    delete button.dataset.controllerCommand;
    delete button.dataset.tabJump;
    delete button.dataset.refreshTab;
  }
}

function setReviewReportAction() {
  const headline = document.getElementById('next-action-headline');
  const description = document.getElementById('next-action-description');
  const facts = document.getElementById('next-action-facts');
  const button = document.getElementById('next-action-button');
  if (headline) headline.textContent = 'Review Report';
  if (description) description.textContent = 'The report is ready. Open the Reports view to review the recommendation, metrics, and failures.';
  if (facts) {
    facts.innerHTML = '<li>Report generated</li><li>Review recommendation</li><li>Confirm only after review</li>';
  }
  if (button) {
    configureTabJumpButton(button, 'reports', 'Review Report', true);
  }
}

function closeLoadedRunHistory() {
  document.querySelectorAll('[data-loaded-history]').forEach((item) => {
    item.classList.add('hidden');
  });
  document.querySelectorAll('[data-fresh-run-state]').forEach((item) => {
    item.classList.remove('hidden');
  });
  document.querySelectorAll('[data-tab-jump="reports"]').forEach((item) => {
    item.classList.add('hidden');
  });
  document.querySelectorAll('[data-loaded-run-action="close"]').forEach((button) => {
    button.disabled = true;
    button.textContent = 'Loaded Run Closed';
  });
  const progressBar = document.getElementById('pipeline-overall-progress-bar');
  const progressLabel = document.getElementById('pipeline-overall-progress-label');
  const caption = document.getElementById('pipeline-caption');
  const reportState = document.getElementById('command-report-state');
  const nextHeadline = document.getElementById('next-action-headline');
  const nextDescription = document.getElementById('next-action-description');
  const nextFacts = document.getElementById('next-action-facts');
  const nextButton = document.getElementById('next-action-button');
  const controllerFeedback = document.getElementById('controller-feedback');
  const runCommand = commandForAction('run');
  if (progressBar) progressBar.style.width = '8%';
  if (progressLabel) progressLabel.textContent = '8%';
  if (caption) caption.textContent = 'Loaded run closed. Ready to start a new optimization.';
  if (reportState) reportState.textContent = 'history closed';
  if (nextHeadline) nextHeadline.textContent = 'Start Optimization';
  if (nextDescription) nextDescription.textContent = 'Start a fresh optimization from the selected model, target, and tuning area.';
  if (nextFacts) {
    nextFacts.innerHTML = [
      'Old history hidden locally',
      'No files deleted',
      'Live run still requires confirmation'
    ].map((text) => '<li>' + text + '</li>').join('');
  }
  if (controllerFeedback) controllerFeedback.textContent = 'Loaded run closed. Start New Optimization is ready.';
  configureControllerButton(nextButton, 'run', '/api/controller/run', runCommand, 'Start Optimization');
  renderOperationResult({
    action: 'history',
    status: 'closed',
    progress_percent: 0,
    plain_summary: {
      what_happened: 'Loaded run history was closed.',
      what_it_means: 'The old report is hidden in this browser session. No files were deleted.',
      next_step: 'Start New Optimization when you want a fresh run.'
    }
  });
}

function commandForAction(action) {
  const source = document.querySelector('[data-controller-action="' + action + '"][data-controller-command]');
  return source ? source.dataset.controllerCommand || '' : '';
}

function configureControllerButton(button, action, endpoint, command, label) {
  if (!button) return;
  button.textContent = label;
  button.disabled = false;
  button.classList.remove('hidden');
  button.dataset.controllerAction = action;
  button.dataset.controllerEndpoint = endpoint;
  button.dataset.controllerCommand = command || '';
  delete button.dataset.tabJump;
  delete button.dataset.refreshTab;
}

function configureTabJumpButton(button, tab, label, refresh) {
  if (!button) return;
  button.textContent = label;
  button.disabled = false;
  button.classList.remove('hidden');
  button.dataset.tabJump = tab;
  button.dataset.refreshTab = refresh ? 'true' : 'false';
  delete button.dataset.controllerAction;
  delete button.dataset.controllerEndpoint;
  delete button.dataset.controllerCommand;
}

function runTabJumpButton(button) {
  if (button.dataset.refreshTab === 'true') {
    openDetailPanel(button.dataset.tabJump);
    safeSessionSet('cockpit-tab-after-reload', button.dataset.tabJump);
    window.setTimeout(() => window.location.reload(), 50);
    return;
  }
  openDetailPanel(button.dataset.tabJump);
}

function pipelineCaptionForCompleted(completed) {
  if (completed.includes('confirm')) return 'Confirmation is complete. Promotion remains the next manual gate.';
  if (completed.includes('report')) return 'Report is available. Review the recommendation before confirmation or promotion.';
  if (completed.includes('run')) return 'Run complete. Generate & Review Report is the next local step.';
  if (completed.includes('preview')) return 'Preview complete. The run is ready for the live execution gate.';
  return 'Plan complete. Preview safety before execution.';
}

function formatActionLabel(action) {
  if (action === 'run') return 'Start Optimization';
  return String(action || 'action').replace(/[-_]/g, ' ').replace(/\\b\\w/g, (letter) => letter.toUpperCase());
}

async function pollControllerJob(jobId) {
  if (state.pollTimer) window.clearTimeout(state.pollTimer);
  try {
    const response = await fetch('/api/jobs/' + encodeURIComponent(jobId));
    const job = await response.json();
    renderOperationResult(job);
    if (['running', 'cancel-requested'].includes(job.status)) {
      state.pollTimer = window.setTimeout(() => pollControllerJob(jobId), 1000);
    }
  } catch (error) {
    renderOperationResult({
      action: 'status',
      status: 'failed',
      progress_percent: 100,
      plain_summary: {
        what_happened: 'I could not check progress.',
        what_it_means: error.message,
        next_step: 'Refresh the page or check the server.'
      }
    });
  }
}

async function loadRecentControllerJob() {
  try {
    const response = await fetch('/api/jobs/recent');
    if (!response.ok) return;
    const job = await response.json();
    if (['failed', 'running', 'cancel-requested'].includes(job.status)) {
      renderOperationResult(job);
    }
  } catch (error) {
    // Static HTML mode and older cockpit servers may not expose recent jobs.
  }
}

async function cancelControllerJob() {
  const cancel = document.getElementById('operation-cancel');
  const jobId = cancel ? cancel.dataset.jobId : '';
  if (!jobId) return;
  try {
    const response = await fetch('/api/jobs/' + encodeURIComponent(jobId) + '/cancel', { method: 'POST' });
    const job = await response.json();
    renderOperationResult(job);
  } catch (error) {
    renderOperationResult({
      action: 'cancel',
      status: 'failed',
      progress_percent: 100,
      plain_summary: {
        what_happened: 'Cancel did not work.',
        what_it_means: error.message,
        next_step: 'Check the server.'
      }
    });
  }
}

document.addEventListener('click', (event) => {
  if (!event.target || !event.target.closest) return;
  const controllerButton = event.target.closest('[data-controller-command]');
  if (controllerButton) {
    runControllerAction(controllerButton);
    return;
  }
  const candidateButton = event.target.closest('[data-candidate-select]');
  if (candidateButton) {
    selectPromotionCandidate(candidateButton);
    return;
  }
  const tabButton = event.target.closest('[data-tab-jump]');
  if (tabButton) runTabJumpButton(tabButton);
});

document.querySelectorAll('.tuning-area-option').forEach((button, index) => {
  button.addEventListener('click', () => selectTuningArea(button));
  if (index === 0) button.classList.add('active');
});

document.querySelectorAll('[data-objective-target]').forEach((button, index) => {
  button.addEventListener('click', () => selectObjectiveTarget(button));
  if (index === 0) selectObjectiveTarget(button);
});

document.querySelectorAll('[data-profile-card]').forEach((button, index) => {
  button.addEventListener('click', () => selectProfileCard(button));
  if (index === 0) button.classList.add('active');
});

const cancelButton = document.getElementById('operation-cancel');
if (cancelButton) {
  cancelButton.addEventListener('click', cancelControllerJob);
}

document.querySelectorAll('[data-loaded-run-action="close"]').forEach((button) => {
  button.addEventListener('click', closeLoadedRunHistory);
});

const tabAfterReload = safeSessionGet('cockpit-tab-after-reload');
if (tabAfterReload) {
  safeSessionRemove('cockpit-tab-after-reload');
  openDetailPanel(tabAfterReload);
}

applyGroupFilters();
loadRecentControllerJob();
"""
