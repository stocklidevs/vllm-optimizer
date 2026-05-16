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
            render_tabs(),
            render_overview(groups, manifest, status, report),
            render_pipeline(manifest),
            render_runs(run_index),
            render_reporting(report),
            render_sources(sources or {}),
            "</section>",
            render_right_rail(manifest, status),
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
            <article class="mini-card {escape(str(group.get('safety_tier') or 'unknown'))}">
              <strong>{escape(str(group.get('label') or group.get('id') or 'Unnamed group'))}</strong>
              <span>{escape(str(group.get('safety_tier') or 'unknown'))}</span>
            </article>"""
        )
    return f"""
    <aside class="left-rail">
      <div class="brand">
        <span class="pulse"></span>
        <div><strong>vLLM</strong><small>Optimizer</small></div>
      </div>
      <nav class="family-nav" aria-label="Knob family filters">
        <button type="button" class="active" data-family-filter="all">All families</button>
        {family_items}
      </nav>
      <div class="rail-section">
        <h2>Knob Groups</h2>
        {''.join(group_items) or '<p class="empty">No knob groups loaded.</p>'}
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
        <p class="hero-copy">Select knob families, inspect safety gates, monitor artifact progress, and review optimization outcomes from one deterministic static interface.</p>
      </div>
      <div class="hero-grid">
        {metric_tile("Groups", len(groups), "catalog entries")}
        {metric_tile("Status", overall, "execution")}
        {metric_tile("Decision", recommendation.get("status", "no report"), "report")}
      </div>
    </header>"""


def render_tabs() -> str:
    return """
    <div class="tabs" aria-label="Cockpit sections">
      <button type="button" class="active" data-tab-target="overview">Overview</button>
      <button type="button" data-tab-target="knobs">Knobs</button>
      <button type="button" data-tab-target="pipeline">Pipeline</button>
      <button type="button" data-tab-target="runs">Runs</button>
      <button type="button" data-tab-target="reports">Reports</button>
      <button type="button" data-tab-target="sources">Sources</button>
    </div>"""


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
      <div class="section-heading">
        <div>
          <p class="eyebrow">Overview</p>
          <h2>Read-only controller shell</h2>
        </div>
        <p>The cockpit is ready for controller mode, but this spec keeps all operations disabled and artifact-driven.</p>
      </div>
      <div class="status-grid">
        <div>{metric_tile("Safety tiers", len(risk_counts), "families")}{'<div class="chips">' + chips + '</div>' if chips else ''}</div>
        <div>{render_status_summary(status)}</div>
        <div>{render_report_summary(report)}</div>
      </div>
      {render_disabled_actions(manifest)}
    </section>
    <section class="panel tab-panel" id="knobs" data-tab-panel="knobs">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Knobs</p>
          <h2>Optimization families</h2>
        </div>
        <p><span id="visible-group-count">{len(groups)}</span> of {len(groups)} groups visible from the deterministic knob catalog.</p>
      </div>
      <div class="filter-bar">
        <label for="knob-search">Search knob groups</label>
        <input id="knob-search" type="search" placeholder="Search by name, family, safety, or config">
      </div>
      <div class="group-grid">{''.join(render_group_card(group) for group in groups) or '<p class="empty">No knob groups loaded.</p>'}</div>
      <p class="empty hidden" id="group-empty-state">No knob groups match the current filter.</p>
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


def render_right_rail(manifest: dict[str, Any] | None, status: dict[str, Any] | None) -> str:
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
        <button disabled>Plan</button>
        <button disabled>Preview</button>
        <button disabled>Run</button>
        <button disabled>Confirm</button>
        <button disabled>Promote</button>
        <p>Actions are disabled in this read-only cockpit spec.</p>
      </section>
    </aside>"""


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
        str(group.get(key) or "")
        for key in ("label", "id", "family", "safety_tier", "description", "command_kind", "config_path")
    ).lower()
    return f"""
    <article class="group-card {escape(str(group.get('safety_tier') or 'unknown'))}" data-family="{escape(str(group.get('family') or 'unknown'))}" data-search="{escape(search_text)}">
      <div class="card-topline"><span>{escape(str(group.get('family') or 'unknown'))}</span><strong>{escape(str(group.get('safety_tier') or 'unknown'))}</strong></div>
      <h3>{escape(str(group.get('label') or group.get('id') or 'Unnamed group'))}</h3>
      <p>{escape(str(group.get('description') or 'No description.'))}</p>
      <dl>
        <div><dt>Command</dt><dd>{escape(str(group.get('command_kind') or 'n/a'))}</dd></div>
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
    stage_names = [str(stage.get("name") or "stage") for stage in _list_of_dicts((manifest or {}).get("stages"))]
    labels = stage_names or ["plan", "preview", "run", "report", "confirm", "promote"]
    buttons = "".join(f"<button disabled>{escape(label)}</button>" for label in labels)
    return f"""
    <div class="disabled-actions">
      <div><strong>Future controller actions</strong><p>Visible for layout alignment; disabled until a controller spec enables execution.</p></div>
      <div>{buttons}</div>
    </div>"""


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
.mini-card { display: grid; gap: 5px; }
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
button { min-width: 74px; min-height: 34px; border-radius: 6px; border: 1px solid rgba(141,164,187,.3); background: rgba(141,164,187,.12); color: var(--muted); margin: 3px; }
.safety-note { margin-top: 12px; }
.actions button { width: 100%; margin: 4px 0; }
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
.run-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.run-card { border: 1px solid rgba(55,216,255,.16); border-radius: 8px; background: rgba(3,8,16,.38); padding: 14px; }
.run-paths { display: grid; gap: 5px; margin-top: 10px; overflow-wrap: anywhere; }
@media (max-width: 1180px) {
  .cockpit { grid-template-columns: 220px minmax(0, 1fr); }
  .right-rail { grid-column: 1 / -1; position: static; grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 820px) {
  .cockpit, .hero, .status-grid, .right-rail { grid-template-columns: 1fr; }
  .left-rail, .right-rail { position: static; max-height: none; }
  .workspace { order: 1; }
  .left-rail { order: 2; }
  .right-rail { order: 3; }
  h1 { font-size: 34px; }
  .section-heading, .disabled-actions { display: block; }
  .recommendation-card, .report-lists, .report-bar-line { grid-template-columns: 1fr; }
}
"""

JS = """
const state = {
  tab: 'overview',
  family: 'all',
  query: ''
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

applyGroupFilters();
"""
