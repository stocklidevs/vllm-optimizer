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
) -> dict[str, str]:
    if not catalog_path.exists():
        raise WebCockpitError(f"catalog path does not exist: {catalog_path}")
    catalog = read_json(catalog_path)
    manifest = _read_optional(manifest_path, "manifest")
    status = _read_optional(status_path, "status")
    report = _read_optional(report_path, "report")
    html = render_web_cockpit(
        catalog,
        manifest=manifest,
        status=status,
        report=report,
        sources={
            "catalog": catalog_path.as_posix(),
            "manifest": manifest_path.as_posix() if manifest_path else None,
            "status": status_path.as_posix() if status_path else None,
            "report": report_path.as_posix() if report_path else None,
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
            render_reporting(report),
            render_sources(sources or {}),
            "</section>",
            render_right_rail(manifest, status),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def render_left_rail(families: list[str], groups: list[dict[str, Any]]) -> str:
    family_items = "".join(f'<a href="#knobs">{escape(family)}</a>' for family in families) or '<span class="empty">No families</span>'
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
      <nav class="family-nav">{family_items}</nav>
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
      <a href="#overview">Overview</a>
      <a href="#knobs">Knobs</a>
      <a href="#pipeline">Pipeline</a>
      <a href="#reports">Reports</a>
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
    <section class="panel" id="overview">
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
    <section class="panel" id="knobs">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Knobs</p>
          <h2>Optimization families</h2>
        </div>
        <p>Groups are loaded from the deterministic knob catalog.</p>
      </div>
      <div class="group-grid">{''.join(render_group_card(group) for group in groups) or '<p class="empty">No knob groups loaded.</p>'}</div>
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
    <section class="panel" id="pipeline">
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
        rows = []
        if isinstance(candidates, dict):
            for candidate_id, candidate in candidates.items():
                metrics = candidate.get("metrics", {}) if isinstance(candidate, dict) else {}
                rows.append(
                    f"""
                    <tr>
                      <td><code>{escape(str(candidate_id))}</code></td>
                      <td>{escape(_fmt(metrics.get('aggregate_tokens_per_second')))}</td>
                      <td>{escape(_fmt(metrics.get('mean_latency_ms')))}</td>
                    </tr>"""
                )
        content = f"""
        {render_report_summary(report)}
        <table>
          <thead><tr><th>Candidate</th><th>Tok/s</th><th>Latency</th></tr></thead>
          <tbody>{''.join(rows) or '<tr><td colspan="3">No candidates available.</td></tr>'}</tbody>
        </table>"""
    return f"""
    <section class="panel" id="reports">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Reports</p>
          <h2>Optimization outcome</h2>
        </div>
        <p>Report values are read from canonical report artifacts.</p>
      </div>
      {content}
    </section>"""


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
    <section class="panel">
      <div class="section-heading"><div><p class="eyebrow">Traceability</p><h2>Source artifacts</h2></div></div>
      <table><tbody>{''.join(rows)}</tbody></table>
    </section>"""


def render_group_card(group: dict[str, Any]) -> str:
    gate = "requires opt-in" if group.get("requires_opt_in") else "no extra opt-in"
    return f"""
    <article class="group-card {escape(str(group.get('safety_tier') or 'unknown'))}">
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


def _fmt(value: Any) -> str:
    return f"{value:.3f}" if isinstance(value, int | float) else "n/a" if value is None else str(value)


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
.family-nav a { color: var(--ink); text-decoration: none; border: 1px solid rgba(55, 216, 255, .12); padding: 9px 10px; border-radius: 6px; background: rgba(55, 216, 255, .06); }
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
.tabs a { color: var(--ink); text-decoration: none; padding: 9px 13px; border-radius: 6px; background: rgba(55, 216, 255, .08); border: 1px solid rgba(55, 216, 255, .12); }
.panel { padding: 20px; }
.section-heading { display: flex; justify-content: space-between; gap: 18px; align-items: end; margin-bottom: 16px; }
.section-heading p { max-width: 480px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.chips span, code { color: #dff9ff; border: 1px solid rgba(55,216,255,.18); background: rgba(55,216,255,.08); border-radius: 5px; padding: 3px 6px; font-family: "Cascadia Mono", Consolas, monospace; font-size: .88em; }
.group-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; }
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
@media (max-width: 1180px) {
  .cockpit { grid-template-columns: 220px minmax(0, 1fr); }
  .right-rail { grid-column: 1 / -1; position: static; grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 820px) {
  .cockpit, .hero, .status-grid, .right-rail { grid-template-columns: 1fr; }
  .left-rail, .right-rail { position: static; max-height: none; }
  h1 { font-size: 34px; }
  .section-heading, .disabled-actions { display: block; }
}
"""
