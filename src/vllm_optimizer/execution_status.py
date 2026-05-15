from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from .artifacts import read_json, read_jsonl, write_json


class ExecutionStatusError(ValueError):
    """Raised when execution status cannot be generated."""


def write_execution_status(run_dir: Path, out_path: Path, html_out: Path | None = None) -> dict[str, str]:
    status = build_execution_status(run_dir)
    write_json(out_path, status)
    artifacts = {"status_path": out_path.as_posix()}
    if html_out is not None:
        html_out.parent.mkdir(parents=True, exist_ok=True)
        html_out.write_text(render_execution_status_html(status), encoding="utf-8")
        artifacts["html_path"] = html_out.as_posix()
    return artifacts


def build_execution_status(run_dir: Path) -> dict[str, Any]:
    if not run_dir.exists():
        raise ExecutionStatusError(f"run directory does not exist: {run_dir}")
    plan_path = run_dir / "pipeline-plan.json"
    if not plan_path.exists():
        raise ExecutionStatusError(f"pipeline plan does not exist: {plan_path}")
    plan = read_json(plan_path)
    summary = read_json(run_dir / "pipeline-summary.json") if (run_dir / "pipeline-summary.json").exists() else {}
    artifacts = artifact_statuses(plan.get("artifacts", {}))
    rows = read_results_rows(artifacts)
    trial_summary = summarize_trials(rows)
    failures = failure_rows(rows)
    completed_stages = summary.get("completed_stages", [])
    if not isinstance(completed_stages, list):
        completed_stages = []
    stages = stage_statuses(plan.get("stages", []), completed_stages)
    overall = overall_state(stages, trial_summary, bool(summary))
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "run_dir": run_dir.as_posix(),
        "mode": plan.get("mode"),
        "overall_state": overall,
        "completed_stages": completed_stages,
        "stages": stages,
        "trial_summary": trial_summary,
        "failures": failures,
        "artifacts": artifacts,
    }


def artifact_statuses(raw_artifacts: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(raw_artifacts, dict):
        return {}
    statuses = {}
    for name in sorted(raw_artifacts):
        value = raw_artifacts[name]
        if not isinstance(value, str):
            continue
        path = Path(value)
        statuses[name] = {
            "path": value,
            "exists": path.exists(),
            "kind": "directory" if path.exists() and path.is_dir() else "file",
        }
    return statuses


def read_results_rows(artifacts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    result_info = artifacts.get("results")
    if not result_info or not result_info.get("exists"):
        return []
    path = Path(str(result_info["path"]))
    return read_jsonl(path)


def summarize_trials(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(row.get("status") or "unknown") for row in rows)
    return {
        "total": len(rows),
        "by_status": dict(sorted(counts.items())),
        "completed": counts.get("completed", 0),
        "failed": counts.get("failed", 0),
    }


def failure_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for row in rows:
        if row.get("status") != "failed":
            continue
        failures.append(
            {
                "trial_id": row.get("trial_id"),
                "candidate_id": row.get("candidate_id"),
                "failure_reason": row.get("failure_reason"),
            }
        )
    return failures


def stage_statuses(raw_stages: Any, completed: list[Any]) -> list[dict[str, Any]]:
    completed_names = {str(item) for item in completed}
    stages = []
    for item in raw_stages if isinstance(raw_stages, list) else []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "unknown")
        artifact = item.get("artifact")
        exists = Path(artifact).exists() if isinstance(artifact, str) else False
        state = "completed" if name in completed_names else "available" if exists else "pending"
        stages.append(
            {
                "name": name,
                "state": state,
                "remote": bool(item.get("remote")),
                "artifact": artifact,
                "artifact_exists": exists,
            }
        )
    return stages


def overall_state(stages: list[dict[str, Any]], trial_summary: dict[str, Any], has_summary: bool) -> str:
    if trial_summary.get("failed", 0) > 0:
        return "failed"
    if has_summary and stages and all(stage["state"] == "completed" for stage in stages if stage["name"] in {"plan", "preview", "run"}):
        return "completed"
    if any(stage["state"] == "completed" for stage in stages):
        return "running"
    return "planned"


def render_execution_status_html(status: dict[str, Any]) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Execution Status</title>",
            f"  <style>{CSS}</style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            f"    <section class=\"hero\"><div><h1>Execution Status</h1><p>{escape(str(status.get('run_dir')))}</p></div><strong>{escape(str(status.get('overall_state')))}</strong></section>",
            render_trial_summary(status.get("trial_summary", {})),
            render_stage_table(status.get("stages", [])),
            render_failure_table(status.get("failures", [])),
            render_artifact_table(status.get("artifacts", {})),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def render_trial_summary(summary: Any) -> str:
    if not isinstance(summary, dict):
        summary = {}
    by_status = summary.get("by_status", {})
    chips = []
    if isinstance(by_status, dict):
        for name in sorted(by_status):
            chips.append(f"<span>{escape(str(name))}: <strong>{escape(str(by_status[name]))}</strong></span>")
    return f"""
    <section class="panel">
      <h2>Trial summary</h2>
      <div class="chips"><span>total: <strong>{escape(str(summary.get("total", 0)))}</strong></span>{''.join(chips)}</div>
    </section>"""


def render_stage_table(stages: Any) -> str:
    rows = []
    for stage in stages if isinstance(stages, list) else []:
        if not isinstance(stage, dict):
            continue
        rows.append(
            f"<tr><td>{escape(str(stage.get('name')))}</td><td>{escape(str(stage.get('state')))}</td><td>{escape(str(stage.get('remote')))}</td><td><code>{escape(str(stage.get('artifact')))}</code></td></tr>"
        )
    return table_panel("Stages", "<thead><tr><th>Name</th><th>State</th><th>Remote</th><th>Artifact</th></tr></thead>", rows)


def render_failure_table(failures: Any) -> str:
    rows = []
    for failure in failures if isinstance(failures, list) else []:
        if not isinstance(failure, dict):
            continue
        rows.append(
            f"<tr><td>{escape(str(failure.get('trial_id')))}</td><td>{escape(str(failure.get('candidate_id') or 'n/a'))}</td><td>{escape(str(failure.get('failure_reason') or 'n/a'))}</td></tr>"
        )
    return table_panel("Failures", "<thead><tr><th>Trial</th><th>Candidate</th><th>Reason</th></tr></thead>", rows)


def render_artifact_table(artifacts: Any) -> str:
    rows = []
    if isinstance(artifacts, dict):
        for name in sorted(artifacts):
            item = artifacts[name]
            if isinstance(item, dict):
                rows.append(
                    f"<tr><td>{escape(str(name))}</td><td>{escape(str(item.get('exists')))}</td><td><code>{escape(str(item.get('path')))}</code></td></tr>"
                )
    return table_panel("Artifacts", "<thead><tr><th>Name</th><th>Exists</th><th>Path</th></tr></thead>", rows)


def table_panel(title: str, head: str, rows: list[str]) -> str:
    body = "".join(rows) or '<tr><td colspan="4">No rows</td></tr>'
    return f'<section class="panel"><h2>{escape(title)}</h2><table>{head}<tbody>{body}</tbody></table></section>'


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


CSS = """
:root { --bg:#f5f7fb; --ink:#131820; --muted:#657284; --panel:#fff; --line:#dbe3ee; --accent:#216e63; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.shell { max-width:1120px; margin:0 auto; padding:32px 22px 48px; }
.hero { display:flex; justify-content:space-between; gap:18px; align-items:flex-start; margin-bottom:18px; }
h1 { margin:0 0 8px; font-size:42px; letter-spacing:0; }
h2 { margin:0 0 14px; font-size:20px; letter-spacing:0; }
p { margin:0; color:var(--muted); overflow-wrap:anywhere; }
.hero strong { background:#dff7ee; color:var(--accent); border-radius:6px; padding:8px 10px; }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:18px; margin-bottom:16px; box-shadow:0 18px 45px rgba(20,24,31,.07); }
.chips { display:flex; flex-wrap:wrap; gap:10px; }
.chips span { border:1px solid var(--line); border-radius:6px; padding:8px 10px; color:var(--muted); }
table { width:100%; border-collapse:collapse; table-layout:fixed; }
th, td { text-align:left; border-bottom:1px solid var(--line); padding:11px 9px; overflow-wrap:anywhere; vertical-align:top; }
th { color:var(--muted); font-size:12px; text-transform:uppercase; }
code { font-family:"Cascadia Mono", Consolas, monospace; font-size:.9em; }
@media (max-width:760px) { .hero { flex-direction:column; } h1 { font-size:32px; } }
"""
