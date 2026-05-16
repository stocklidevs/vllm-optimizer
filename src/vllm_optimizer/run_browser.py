from __future__ import annotations

from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from . import __version__
from .artifacts import write_json


SCHEMA_VERSION = "1.0"
KNOWN_ARTIFACTS = {
    "summary.json": "summary",
    "ranking.json": "ranking",
    "canonical-report.json": "canonical_report",
    "execution-status.json": "execution_status",
    "pipeline-summary.json": "pipeline_summary",
    "results.jsonl": "results",
}


class RunBrowserError(ValueError):
    """Raised when run browser artifacts cannot be generated."""


def write_run_index(artifacts_root: Path, out_path: Path, html_out: Path | None = None) -> dict[str, str]:
    index = build_run_index(artifacts_root)
    write_json(out_path, index)
    artifacts = {"index_path": out_path.as_posix()}
    if html_out is not None:
        html_out.parent.mkdir(parents=True, exist_ok=True)
        html_out.write_text(render_run_browser_html(index), encoding="utf-8")
        artifacts["html_path"] = html_out.as_posix()
    return artifacts


def build_run_index(artifacts_root: Path) -> dict[str, Any]:
    if not artifacts_root.exists():
        raise RunBrowserError(f"artifacts root does not exist: {artifacts_root}")
    root = artifacts_root.resolve()
    by_dir: dict[Path, dict[str, str]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        artifact_type = KNOWN_ARTIFACTS.get(path.name)
        if artifact_type is None:
            continue
        by_dir.setdefault(path.parent, {})[artifact_type] = path.as_posix()

    runs = []
    for directory, artifact_paths in sorted(by_dir.items(), key=lambda item: item[0].as_posix()):
        relative_dir = directory.relative_to(root).as_posix()
        mtimes = [(Path(path).stat().st_mtime) for path in artifact_paths.values() if Path(path).exists()]
        runs.append(
            {
                "run_id": labelize(relative_dir),
                "relative_dir": relative_dir,
                "artifact_types": sorted(artifact_paths),
                "artifact_paths": dict(sorted(artifact_paths.items())),
                "modified_at": _timestamp(max(mtimes) if mtimes else directory.stat().st_mtime),
            }
        )
    runs.sort(key=lambda run: (run["modified_at"], run["relative_dir"]), reverse=True)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": __version__,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "artifacts_root": artifacts_root.as_posix(),
        "run_count": len(runs),
        "runs": runs,
    }


def render_run_browser_html(index: dict[str, Any]) -> str:
    rows = []
    for run in _list_of_dicts(index.get("runs")):
        rows.append(
            f"""
            <tr>
              <td><strong>{escape(str(run.get('run_id')))}</strong><br><small>{escape(str(run.get('relative_dir')))}</small></td>
              <td>{escape(', '.join(str(item) for item in run.get('artifact_types', [])))}</td>
              <td>{escape(str(run.get('modified_at') or 'n/a'))}</td>
                <td>{render_artifact_paths(run.get('artifact_paths'))}</td>
            </tr>"""
        )
    table_body = "".join(rows) or '<tr><td colspan="4">No runs found.</td></tr>'
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Run Browser</title>",
            f"  <style>{CSS}</style>",
            "</head>",
            "<body>",
            '<main class="shell">',
            "<header><p>vLLM Optimizer</p><h1>Run Browser</h1></header>",
            f"<p>{escape(str(index.get('run_count', 0)))} local run directories indexed.</p>",
            f"<table><thead><tr><th>Run</th><th>Artifacts</th><th>Modified</th><th>Paths</th></tr></thead><tbody>{table_body}</tbody></table>",
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def render_artifact_paths(value: Any) -> str:
    if not isinstance(value, dict):
        return "n/a"
    return "".join(f"<div><code>{escape(str(key))}</code>: <code>{escape(str(path))}</code></div>" for key, path in sorted(value.items()))


def labelize(relative_dir: str) -> str:
    text = relative_dir.strip("/").replace("/", "-").replace("_", "-")
    return text or "artifacts-root"


def _timestamp(value: float) -> str:
    return datetime.fromtimestamp(value, UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


CSS = """
:root { color-scheme: dark; --bg:#050912; --panel:#0b1422; --ink:#e7f4ff; --muted:#8da4bb; --line:#24435f; --cyan:#37d8ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:Inter, ui-sans-serif, system-ui, sans-serif; }
.shell { max-width:1180px; margin:0 auto; padding:34px 22px 48px; }
header { margin-bottom:20px; }
header p { color:var(--cyan); text-transform:uppercase; font-weight:760; font-size:12px; }
h1 { margin:0; font-size:42px; letter-spacing:0; }
p, small { color:var(--muted); }
table { width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line); border-radius:8px; overflow:hidden; }
th, td { padding:12px 10px; border-bottom:1px solid rgba(55,216,255,.13); text-align:left; vertical-align:top; overflow-wrap:anywhere; }
th { color:var(--muted); font-size:12px; text-transform:uppercase; }
code { color:#dff9ff; font-family:"Cascadia Mono", Consolas, monospace; font-size:.9em; }
"""
