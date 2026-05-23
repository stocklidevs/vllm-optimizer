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
) -> dict[str, str]:
    if not catalog_path.exists():
        raise WebCockpitError(f"catalog path does not exist: {catalog_path}")
    catalog = read_json(catalog_path)
    manifest = _read_optional(manifest_path, "manifest")
    status = _read_optional(status_path, "status")
    report = _read_optional(report_path, "report")
    run_index = _read_optional(run_index_path, "run index")
    html = render_web_cockpit(
        catalog,
        manifest=manifest,
        status=status,
        report=report,
        run_index=run_index,
        sources={
            "catalog": catalog_path.as_posix(),
            "manifest": manifest_path.as_posix() if manifest_path else None,
            "status": status_path.as_posix() if status_path else None,
            "report": report_path.as_posix() if report_path else None,
            "run_index": run_index_path.as_posix() if run_index_path else None,
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
            "  <title>vLLM Mission Control</title>",
            f"  <style>{CSS}</style>",
            "</head>",
            "<body>",
            '<main class="cockpit">',
            render_left_rail(families, groups),
            '<section class="workspace">',
            render_hero(groups, status, report),
            render_automatic_pipeline_panel(groups, manifest, status, report),
            render_workflow(manifest, status, report),
            render_tabs(),
            render_overview(groups, manifest, status, report),
            render_pipeline(manifest),
            render_runs(run_index),
            render_reporting(report),
            render_promotion_workflow(report, manifest),
            render_how_to_use(),
            render_sources(sources or {}),
            "</section>",
            render_right_rail(manifest, status, report),
            f"<script>{JS}</script>",
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def render_left_rail(families: list[str], groups: list[dict[str, Any]]) -> str:
    family_items = "".join(
        f'<button type="button" data-family-filter="{escape(family)}">{escape(family)}</button>' for family in families
    ) or '<span class="empty">No families</span>'
    group_items = []
    for group in groups[:10]:
        group_items.append(
            f"""
            <button type="button" class="mini-card tuning-area-option {escape(str(group.get('safety_tier') or 'unknown'))}" data-tuning-area-id="{escape(str(group.get('id') or ''))}" data-tuning-area-label="{escape(group_label(group))}" data-tuning-area-family="{escape(group_display_family(group))}" data-tuning-area-safety="{escape(str(group.get('safety_tier') or 'unknown'))}" data-tuning-area-description="{escape(str(group.get('description') or 'No description.'))}" data-tuning-area-config="{escape(str(group.get('config_path') or 'n/a'))}" data-knobs-tuned="{escape('|'.join(group_knobs(group)))}">
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
    steps = []
    for index, step in enumerate(WORKFLOW_STEPS, start=1):
        action = step["action"]
        if action == current:
            state = "active"
            label = "Ready"
        elif index < current_index:
            state = "complete"
            label = "Done"
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
        <h2>Optimization Workflow</h2>
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
    risk_counts: dict[str, int] = {}
    for group in groups:
        tier = str(group.get("safety_tier") or "unknown")
        risk_counts[tier] = risk_counts.get(tier, 0) + 1
    chips = "".join(f"<span>{escape(tier)}: {count}</span>" for tier, count in sorted(risk_counts.items()))
    return f"""
    <section class="panel tab-panel active" id="overview" data-tab-panel="overview">
      {render_guided_step_workspace(groups, manifest, status, report)}
      <div class="status-grid">
        <div>{metric_tile("Safety tiers", len(risk_counts), "families")}{'<div class="chips">' + chips + '</div>' if chips else ''}</div>
        <div>{render_status_summary(status)}</div>
        <div>{render_report_summary(report)}</div>
      </div>
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


def render_reporting(report: dict[str, Any] | None) -> str:
    if report is None:
        content = '<p class="empty">No canonical report loaded.</p>'
    else:
        candidates = report.get("candidates", {})
        content = f"""
        {render_recommendation_detail(report)}
        {render_metric_visualizer(candidates if isinstance(candidates, dict) else {})}
        {render_failure_summary(candidates if isinstance(candidates, dict) else {})}"""
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
          <span class="step-pill">{progress}%</span>
        </div>
        <div class="progress-track overall-progress" aria-label="Overall progress">
          <div class="progress-bar" style="width:{progress}%"></div>
        </div>
        <p class="progress-caption">{escape(pipeline_caption(status, report))}</p>
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
    selected = selected_group_label(groups, manifest)
    command = controller_commands(manifest).get(action, "")
    facts = "".join(f"<li>{escape(item)}</li>" for item in step["facts"])
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
        <p class="eyebrow">Step {workflow_index(action)}: {escape(step['label'])}</p>
        <h2>{escape(step['headline'])}</h2>
        <ul class="fact-list">{facts}</ul>
        {render_primary_action_button(action, manifest)}
        <p class="next-note">Next: {escape(step['next'])}</p>
      </article>
      <article class="command-shell">
        <p class="eyebrow">Controller command shell</p>
        <h2>{escape(step['label'])} command</h2>
        <pre><code>{escape(command or 'No command loaded for this step.')}</code></pre>
        <button type="button" data-controller-action="{escape(action)}" data-controller-endpoint="/api/controller/{escape(action)}" data-controller-command="{escape(command)}">Run {escape(step['label'])}</button>
        <div class="what-next">
          <strong>What happens next?</strong>
          <p>{escape(step['what_next'])}</p>
        </div>
      </article>
    </div>"""


def render_promotion_workflow(report: dict[str, Any] | None, manifest: dict[str, Any] | None) -> str:
    if report is None:
        content = '<p class="empty">No promotion workflow loaded.</p>'
    else:
        recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}
        promotion = manifest.get("promotion", {}) if isinstance((manifest or {}).get("promotion"), dict) else {}
        gate = str(promotion.get("required_gate") or "--allow-promotion")
        available = bool(promotion.get("available", False))
        automatic = bool(promotion.get("automatic", False))
        candidate_id = str(recommendation.get("candidate_id") or "no candidate")
        objective = str(recommendation.get("objective") or "no objective")
        status = str(recommendation.get("status") or "unknown")
        content = f"""
        <div class="promotion-grid">
          <article class="promotion-card">
            <p class="eyebrow">Recommendation</p>
            <h3>{escape(status)}</h3>
            <dl>
              <div><dt>Candidate</dt><dd><code>{escape(candidate_id)}</code></dd></div>
              <div><dt>Objective</dt><dd>{escape(objective)}</dd></div>
              <div><dt>Available</dt><dd>{escape(str(available))}</dd></div>
              <div><dt>Automatic</dt><dd>{escape(str(automatic))}</dd></div>
            </dl>
          </article>
          <article class="promotion-card gate-card">
            <p class="eyebrow">Required gate</p>
            <h3><code>{escape(gate)}</code></h3>
            <p>Promotion remains disabled in the static cockpit. Use the CLI gate after repeated confirmation approves the candidate.</p>
            <button disabled>Promote disabled</button>
          </article>
        </div>
        <div class="command-stack">
          <article>
            <strong>Preview profile promotion</strong>
            <code>uv run vllm-optimizer promote-preview --ranking ARTIFACT_DIR/live/ranking.json --out ARTIFACT_DIR/promotion-preview.json</code>
          </article>
          <article>
            <strong>Promote after confirmation</strong>
            <code>uv run vllm-optimizer promote-confirmed-profile --confirmation-report ARTIFACT_DIR/confirmation/confirmation-report.json --ranking ARTIFACT_DIR/live/ranking.json --profile-out PROFILE_OUT --summary-out SUMMARY_OUT {escape(gate)}</code>
          </article>
        </div>"""
    return f"""
    <section class="panel tab-panel" id="promotion" data-tab-panel="promotion">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Promotion</p>
          <h2>Promotion workflow</h2>
        </div>
        <p>Profile promotion is visible for traceability, gated by explicit CLI flags, and never automatic from this static cockpit.</p>
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
      <div class="progress-track" aria-label="Operation progress">
        <div id="operation-progress-bar" class="progress-bar" style="width:0%"></div>
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


def render_metric_visualizer(candidates: dict[str, Any]) -> str:
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


def render_failure_summary(candidates: dict[str, Any]) -> str:
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
    gates: list[str] = []
    if manifest is not None:
        for stage in _list_of_dicts(manifest.get("stages")):
            for gate in stage.get("required_gates") or []:
                gates.append(str(gate))
        promotion = manifest.get("promotion", {}) if isinstance(manifest.get("promotion"), dict) else {}
        gate = promotion.get("required_gate")
        if gate:
            gates.append(str(gate))
    unique_gates = sorted(set(gates))
    return f"""
    <aside class="right-rail">
      {render_next_action_panel(manifest, status, report)}
      <section class="rail-panel">
        <h2>Execution</h2>
        {render_status_summary(status)}
      </section>
      <section class="rail-panel">
        <h2>Safety Gates</h2>
        {''.join(f'<code>{escape(gate)}</code>' for gate in unique_gates) or '<p class="empty">No gates loaded.</p>'}
      </section>
      <section class="rail-panel actions">
        <h2>Controller</h2>
        {render_controller_buttons(manifest, compact=True)}
        <p id="controller-feedback" class="controller-feedback" aria-live="polite">Choose an action to copy its CLI command.</p>
      </section>
    </aside>"""


def render_next_action_panel(
    manifest: dict[str, Any] | None,
    status: dict[str, Any] | None,
    report: dict[str, Any] | None,
) -> str:
    action = current_workflow_action(status, report)
    step = workflow_step(action)
    command = controller_commands(manifest).get(action, "")
    facts = "".join(f"<li>{escape(item)}</li>" for item in step["facts"])
    followups = "".join(f"<li>{escape(item['label'])}</li>" for item in WORKFLOW_STEPS[workflow_index(action) : workflow_index(action) + 3])
    return f"""
      <section class="rail-panel next-action-card">
        <p class="eyebrow">Next Action</p>
        <span class="step-pill">Step {workflow_index(action)} of {len(WORKFLOW_STEPS)}</span>
        <h2>{escape(step['headline'])}</h2>
        <p>{escape(step['description'])}</p>
        <ul class="fact-list compact">{facts}</ul>
        <button type="button" class="primary-action" data-controller-action="{escape(action)}" data-controller-endpoint="/api/controller/{escape(action)}" data-controller-command="{escape(command)}">{escape(step['label'])}</button>
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
    search_text = " ".join(
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
    return "".join(
        f'<button type="button" data-controller-action="{escape(name)}" data-controller-endpoint="/api/controller/{escape(name)}" data-controller-command="{escape(command)}">{escape(name.title())}{help_button(name)}</button>'
        for name, command in ordered
    )


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
        "promote": "uv run vllm-optimizer promote-confirmed-profile --confirmation-report ARTIFACT_DIR/confirmation/confirmation-report.json --ranking ARTIFACT_DIR/live/ranking.json --profile-out PROFILE_OUT --summary-out SUMMARY_OUT --allow-promotion",
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
        "next": "Load Report will be enabled after results exist.",
        "what_next": "When execution finishes, generate or load the canonical report.",
    },
    {
        "action": "report",
        "label": "Load Report",
        "headline": "Load Report",
        "description": "Rank completed results and explain the current recommendation.",
        "group_hint": "Turn run artifacts into a decision-ready report.",
        "facts": ["Artifact only", "Shows winner", "Explains failures"],
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


def render_primary_action_button(action: str, manifest: dict[str, Any] | None) -> str:
    step = workflow_step(action)
    command = controller_commands(manifest).get(action, "")
    return (
        f'<button type="button" class="primary-action" data-controller-action="{escape(action)}" '
        f'data-controller-endpoint="/api/controller/{escape(action)}" data-controller-command="{escape(command)}">'
        f'{escape(step["label"])} -></button>'
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


def _candidate_metric_rows(candidates: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for candidate_id, candidate in candidates.items():
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
  --bg: #050912;
  --panel: #0b1422;
  --panel-2: #0f1d2f;
  --ink: #e7f4ff;
  --muted: #8da4bb;
  --line: #24435f;
  --cyan: #37d8ff;
  --green: #49f2a1;
  --amber: #f0c65b;
  --red: #ff6b6b;
  --violet: #a891ff;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(55, 216, 255, .16), transparent 34%),
    linear-gradient(135deg, #050912 0%, #071321 58%, #0d1020 100%);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.cockpit { display: grid; grid-template-columns: 280px minmax(0, 1fr) 300px; gap: 16px; min-height: 100vh; padding: 16px; }
.left-rail, .right-rail { position: sticky; top: 16px; align-self: start; display: grid; gap: 14px; max-height: calc(100vh - 32px); overflow: auto; }
.brand, .rail-panel, .panel, .mini-card, .metric-tile, .group-card {
  background: linear-gradient(180deg, rgba(15, 29, 47, .94), rgba(8, 16, 28, .94));
  border: 1px solid rgba(55, 216, 255, .18);
  border-radius: 8px;
  box-shadow: 0 18px 52px rgba(0, 0, 0, .28), inset 0 1px 0 rgba(255, 255, 255, .04);
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
.hero { min-height: 280px; display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(280px, .8fr); gap: 16px; align-items: stretch; padding: 24px; border: 1px solid rgba(55, 216, 255, .22); border-radius: 8px; background: linear-gradient(135deg, rgba(8, 18, 33, .92), rgba(13, 27, 47, .84)); }
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
.panel { padding: 20px; }
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
.pipeline-stage.running span, .pipeline-stage.automatic span { color: var(--cyan); }
.pipeline-stage.manual.gate span, .pipeline-stage.manual span { color: var(--amber); }
.pipeline-stage small { color: var(--muted); overflow-wrap: anywhere; }
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
.hidden { display: none; }
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
.progress-track { height: 14px; border-radius: 999px; background: rgba(141,164,187,.16); overflow: hidden; margin-bottom: 14px; }
.progress-bar { height: 100%; width: 0; border-radius: 999px; background: linear-gradient(90deg, var(--cyan), var(--green)); transition: width .24s ease; }
.explain-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.explain-grid article { border: 1px solid rgba(55,216,255,.14); border-radius: 8px; background: rgba(3,8,16,.32); padding: 12px; }
.explain-grid strong { display: block; margin-bottom: 6px; }
.how-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.how-card { border: 1px solid rgba(55,216,255,.16); border-radius: 8px; background: rgba(3,8,16,.38); padding: 14px; }
.how-card strong { display: block; margin-bottom: 8px; color: var(--ink); }
.report-card { border: 1px solid rgba(55,216,255,.16); border-radius: 8px; background: rgba(3,8,16,.38); padding: 16px; margin-bottom: 14px; }
.recommendation-card { display: grid; grid-template-columns: minmax(0, .9fr) minmax(0, 1.4fr); gap: 16px; }
.report-lists { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.report-lists h4 { margin: 0 0 8px; }
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
  .recommendation-card, .report-lists, .report-bar-line, .promotion-grid, .explain-grid, .guided-grid, .auto-pipeline-panel, .workflow-steps, .pipeline-stage { grid-template-columns: 1fr; }
  .command-shell { grid-column: auto; }
  .workflow-heading { align-items: flex-start; flex-direction: column; }
  .workflow-step { justify-items: start; text-align: left; grid-template-columns: auto minmax(0, 1fr); align-items: center; min-height: 76px; }
  .workflow-step small { grid-column: 2; }
  .workflow-step::after { display: none; }
}
"""

JS = """
const state = {
  tab: 'overview',
  family: 'all',
  query: '',
  currentJobId: null,
  pollTimer: null
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

function applyGroupFilters() {
  const query = state.query.trim().toLowerCase();
  let visible = 0;
  document.querySelectorAll('.group-card').forEach((card) => {
    const familyMatch = state.family === 'all' || card.dataset.family === state.family;
    const queryMatch = !query || (card.dataset.search || '').includes(query);
    const show = familyMatch && queryMatch;
    card.classList.toggle('hidden', !show);
    if (show) visible += 1;
  });
  const count = document.getElementById('visible-group-count');
  if (count) count.textContent = String(visible);
  const empty = document.getElementById('group-empty-state');
  if (empty) empty.classList.toggle('hidden', visible !== 0);
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
    setActiveTab('knobs');
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
  if (labelTarget) labelTarget.textContent = label;
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
  const title = document.getElementById('operation-title');
  const bar = document.getElementById('operation-progress-bar');
  const what = document.getElementById('operation-what');
  const meaning = document.getElementById('operation-meaning');
  const next = document.getElementById('operation-next');
  const cancel = document.getElementById('operation-cancel');
  const summary = job.plain_summary || {};
  const progress = Math.max(0, Math.min(100, Number(job.progress_percent || 0)));
  if (title) title.textContent = (job.action || 'Action') + ': ' + (job.status || 'unknown');
  if (bar) bar.style.width = progress + '%';
  if (what) what.textContent = summary.what_happened || 'The controller updated this operation.';
  if (meaning) meaning.textContent = summary.what_it_means || 'The cockpit is waiting for more details.';
  if (next) next.textContent = summary.next_step || 'Choose the next safe step.';
  if (cancel) {
    cancel.disabled = !job.job_id || !['running', 'cancel-requested'].includes(job.status);
    cancel.dataset.jobId = job.job_id || '';
  }
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

document.querySelectorAll('[data-controller-command]').forEach((button) => {
  button.addEventListener('click', () => runControllerAction(button));
});

document.querySelectorAll('.tuning-area-option').forEach((button, index) => {
  button.addEventListener('click', () => selectTuningArea(button));
  if (index === 0) button.classList.add('active');
});

const cancelButton = document.getElementById('operation-cancel');
if (cancelButton) {
  cancelButton.addEventListener('click', cancelControllerJob);
}

applyGroupFilters();
"""
