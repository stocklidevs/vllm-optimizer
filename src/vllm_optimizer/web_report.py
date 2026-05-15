from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from .artifacts import read_json


class WebReportError(ValueError):
    """Raised when a static web report cannot be generated."""


REQUIRED_SECTIONS = ("source", "recommendation", "objectives", "candidates", "chart_datasets", "provenance")


def write_web_report(report_path: Path, out_path: Path) -> dict[str, str]:
    if not report_path.exists():
        raise WebReportError(f"report path does not exist: {report_path}")
    report = read_json(report_path)
    html = render_web_report(report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return {"html_path": out_path.as_posix(), "report_path": report_path.as_posix()}


def render_web_report(report: dict[str, Any]) -> str:
    validate_report(report)
    source = report["source"]
    recommendation = report["recommendation"]
    candidates = report["candidates"]
    objectives = report["objectives"]
    provenance = report["provenance"]
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Canonical vLLM Report</title>",
            f"  <style>{CSS}</style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            render_header(source, recommendation),
            render_summary_metrics(candidates),
            render_metric_map(candidates),
            render_objectives(objectives),
            render_candidates(candidates),
            render_next_actions(recommendation),
            render_provenance(provenance),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def validate_report(report: dict[str, Any]) -> None:
    for section in REQUIRED_SECTIONS:
        if not isinstance(report.get(section), dict):
            raise WebReportError(f"missing canonical report section: {section}")


def render_header(source: dict[str, Any], recommendation: dict[str, Any]) -> str:
    status = str(recommendation.get("status", "unknown"))
    return f"""
    <section class="hero">
      <div>
        <div class="product">Canonical vLLM Report</div>
        <h1>{escape(str(source.get("label") or "Optimization report"))}</h1>
        <p>{inline_code_to_html(str(recommendation.get("summary") or "No summary available."))}</p>
      </div>
      <div class="decision">
        <span class="status">{escape(status)}</span>
        <dl>
          <div><dt>Objective</dt><dd>{escape(str(recommendation.get("objective") or "n/a"))}</dd></div>
          <div><dt>Candidate</dt><dd>{escape(str(recommendation.get("candidate_id") or "n/a"))}</dd></div>
          <div><dt>Family</dt><dd>{escape(str(source.get("family") or "n/a"))}</dd></div>
        </dl>
      </div>
    </section>"""


def render_summary_metrics(candidates: dict[str, Any]) -> str:
    rows = []
    best_tps = best_metric(candidates, "aggregate_tokens_per_second", higher=True)
    best_latency = best_metric(candidates, "mean_latency_ms", higher=False)
    worst_failure = best_metric(candidates, "failure_rate", higher=True)
    rows.append(metric_tile("Best throughput", best_tps, "tokens/sec"))
    rows.append(metric_tile("Best latency", best_latency, "ms"))
    rows.append(metric_tile("Highest failure rate", worst_failure, ""))
    rows.append(metric_tile("Candidates", str(len(candidates)), "total"))
    return '<section class="metrics">' + "".join(rows) + "</section>"


def metric_tile(label: str, value: Any, suffix: str) -> str:
    return f"""
    <article class="metric">
      <span>{escape(label)}</span>
      <strong>{escape(format_value(value))}</strong>
      <small>{escape(suffix)}</small>
    </article>"""


def render_metric_map(candidates: dict[str, Any]) -> str:
    points = []
    numeric = [
        candidate
        for candidate in candidates.values()
        if number(candidate.get("metrics", {}).get("aggregate_tokens_per_second")) is not None
    ]
    max_tps = max((number(item["metrics"].get("aggregate_tokens_per_second")) or 0 for item in numeric), default=1)
    for candidate in candidates.values():
        metrics = candidate.get("metrics", {})
        tps = number(metrics.get("aggregate_tokens_per_second")) or 0.0
        width = 0 if max_tps == 0 else max(4, min(100, (tps / max_tps) * 100))
        classes = "bar baseline" if candidate.get("is_baseline") else "bar"
        if not candidate.get("recommendable", True):
            classes += " blocked"
        points.append(
            f"""
            <div class="bar-row">
              <span title="{escape(str(candidate.get("candidate_id")))}">{escape(str(candidate.get("candidate_id")))}</span>
              <div class="{classes}" style="width:{width:.3f}%"></div>
              <strong>{escape(format_value(tps))}</strong>
            </div>"""
        )
    return f"""
    <section class="panel">
      <div class="section-heading">
        <h2>Metric map</h2>
        <p>Throughput comparison from canonical candidate metrics.</p>
      </div>
      <div class="bars">{''.join(points)}</div>
    </section>"""


def render_objectives(objectives: dict[str, Any]) -> str:
    rows = []
    for name in sorted(objectives):
        objective = objectives.get(name, {})
        rows.append(
            f"""
            <tr>
              <td>{escape(str(name))}</td>
              <td>{escape(str(objective.get("winner_candidate_id") or "n/a"))}</td>
              <td>{escape(str(objective.get("ranked_candidate_count") or 0))}</td>
            </tr>"""
        )
    return f"""
    <section class="panel">
      <div class="section-heading">
        <h2>Objective summary</h2>
        <p>Winners and rankable candidate counts by objective.</p>
      </div>
      <table>
        <thead><tr><th>Objective</th><th>Winner</th><th>Ranked</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>"""


def render_candidates(candidates: dict[str, Any]) -> str:
    rows = []
    for candidate in candidates.values():
        metrics = candidate.get("metrics", {})
        flags = []
        if candidate.get("is_baseline"):
            flags.append("baseline")
        if not candidate.get("recommendable", True):
            flags.append("excluded")
        rows.append(
            f"""
            <tr>
              <td><code>{escape(str(candidate.get("candidate_id")))}</code></td>
              <td>{escape(", ".join(flags) or "candidate")}</td>
              <td>{escape(format_value(metrics.get("aggregate_tokens_per_second")))}</td>
              <td>{escape(format_value(metrics.get("mean_latency_ms")))}</td>
              <td>{escape(format_percent(metrics.get("failure_rate")))}</td>
            </tr>"""
        )
    return f"""
    <section class="panel">
      <div class="section-heading">
        <h2>Candidate comparison</h2>
        <p>Canonical candidate metrics ready for dashboard tables and charts.</p>
      </div>
      <table>
        <thead><tr><th>Candidate</th><th>Role</th><th>Tok/s</th><th>Latency ms</th><th>Failure</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>"""


def render_next_actions(recommendation: dict[str, Any]) -> str:
    actions = recommendation.get("next_actions", [])
    if not isinstance(actions, list):
        actions = []
    items = "".join(f"<li>{inline_code_to_html(str(action))}</li>" for action in actions)
    rationale = recommendation.get("rationale", [])
    if not isinstance(rationale, list):
        rationale = []
    reasons = "".join(f"<li>{escape(str(reason))}</li>" for reason in rationale)
    return f"""
    <section class="split">
      <div class="panel">
        <h2>Next actions</h2>
        <ul>{items}</ul>
      </div>
      <div class="panel">
        <h2>Rationale</h2>
        <ul>{reasons}</ul>
      </div>
    </section>"""


def render_provenance(provenance: dict[str, Any]) -> str:
    rows = []
    for key in sorted(provenance):
        value = provenance[key]
        if value is None:
            continue
        rows.append(f"<tr><td>{escape(str(key))}</td><td><code>{escape(str(value))}</code></td></tr>")
    return f"""
    <section class="panel">
      <div class="section-heading">
        <h2>Provenance</h2>
        <p>Source artifacts used by the canonical report.</p>
      </div>
      <table><tbody>{''.join(rows)}</tbody></table>
    </section>"""


def best_metric(candidates: dict[str, Any], key: str, higher: bool) -> Any:
    values = [number(candidate.get("metrics", {}).get(key)) for candidate in candidates.values()]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return max(values) if higher else min(values)


def inline_code_to_html(value: str) -> str:
    parts = value.split("`")
    rendered = []
    for index, part in enumerate(parts):
        escaped = escape(part)
        if index % 2 == 1:
            rendered.append(f"<code>{escaped}</code>")
        else:
            rendered.append(escaped)
    return "".join(rendered)


def number(value: Any) -> float | None:
    return float(value) if isinstance(value, int | float) else None


def format_value(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.3f}"
    return "n/a" if value is None else str(value)


def format_percent(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.3%}"
    return "n/a" if value is None else str(value)


CSS = """
:root {
  color-scheme: light;
  --bg: #f6f8fb;
  --ink: #14181f;
  --muted: #657284;
  --panel: #ffffff;
  --line: #d9e1ea;
  --accent: #0f8a69;
  --accent-soft: #dff7ee;
  --blue: #2563a9;
  --shadow: 0 18px 55px rgba(20, 24, 31, .08);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.shell { max-width: 1180px; margin: 0 auto; padding: 32px 22px 48px; }
.hero {
  min-height: 270px;
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(280px, .75fr);
  gap: 22px;
  align-items: stretch;
  margin-bottom: 18px;
}
.product { font-size: 14px; font-weight: 760; color: var(--accent); margin-bottom: 18px; }
h1 { font-size: 44px; line-height: 1.05; margin: 0 0 18px; letter-spacing: 0; }
h2 { font-size: 20px; margin: 0 0 8px; letter-spacing: 0; }
p { color: var(--muted); line-height: 1.55; margin: 0; }
code { font-family: "Cascadia Mono", "SFMono-Regular", Consolas, monospace; font-size: .92em; }
.decision, .panel, .metric {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
}
.decision { padding: 22px; display: flex; flex-direction: column; justify-content: space-between; }
.status {
  width: fit-content;
  color: var(--accent);
  background: var(--accent-soft);
  border-radius: 6px;
  padding: 7px 9px;
  font-weight: 780;
}
dl { margin: 24px 0 0; display: grid; gap: 12px; }
dt { color: var(--muted); font-size: 12px; text-transform: uppercase; font-weight: 760; }
dd { margin: 2px 0 0; font-weight: 720; overflow-wrap: anywhere; }
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 18px; }
.metric { padding: 16px; }
.metric span, .metric small { color: var(--muted); font-size: 12px; font-weight: 680; }
.metric strong { display: block; font-size: 26px; margin: 8px 0 2px; }
.panel { padding: 20px; margin-bottom: 18px; }
.section-heading { display: flex; justify-content: space-between; gap: 18px; align-items: end; margin-bottom: 16px; }
.section-heading p { max-width: 420px; font-size: 14px; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th, td { text-align: left; border-bottom: 1px solid var(--line); padding: 12px 10px; vertical-align: top; overflow-wrap: anywhere; }
th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0; }
.bars { display: grid; gap: 12px; }
.bar-row { display: grid; grid-template-columns: minmax(160px, 280px) 1fr 88px; gap: 12px; align-items: center; }
.bar-row span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); }
.bar { height: 16px; background: var(--blue); border-radius: 4px; min-width: 4px; }
.bar.baseline { background: var(--accent); }
.bar.blocked { background: #9ca3af; }
.split { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
ul { margin: 10px 0 0; padding-left: 20px; color: var(--muted); line-height: 1.6; }
@media (max-width: 820px) {
  .hero, .metrics, .split { grid-template-columns: 1fr; }
  h1 { font-size: 34px; }
  .bar-row { grid-template-columns: 1fr; }
}
"""
