from __future__ import annotations

from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from .artifacts import read_json, write_json


class PipelineControlError(ValueError):
    """Raised when a pipeline control manifest cannot be generated."""


def write_pipeline_control_manifest(
    catalog_path: Path,
    group_id: str,
    out_path: Path,
    html_out: Path | None = None,
) -> dict[str, str]:
    if not catalog_path.exists():
        raise PipelineControlError(f"catalog path does not exist: {catalog_path}")
    manifest = build_pipeline_control_manifest(read_json(catalog_path), group_id)
    write_json(out_path, manifest)
    artifacts = {"manifest_path": out_path.as_posix()}
    if html_out is not None:
        html_out.parent.mkdir(parents=True, exist_ok=True)
        html_out.write_text(render_pipeline_control_html(manifest), encoding="utf-8")
        artifacts["html_path"] = html_out.as_posix()
    return artifacts


def build_pipeline_control_manifest(catalog: dict[str, Any], group_id: str) -> dict[str, Any]:
    group = find_group(catalog, group_id)
    stages = stages_for_group(group)
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "group": group,
        "stages": stages,
        "promotion": {
            "automatic": False,
            "available": any(stage["name"] == "promote" for stage in stages),
            "required_gate": "--allow-promotion",
            "note": "Promotion remains disabled unless an explicit promotion gate is used.",
        },
    }


def find_group(catalog: dict[str, Any], group_id: str) -> dict[str, Any]:
    groups = catalog.get("groups")
    if not isinstance(groups, list):
        raise PipelineControlError("catalog has no groups")
    for group in groups:
        if isinstance(group, dict) and group.get("id") == group_id:
            return dict(group)
    raise PipelineControlError(f"group id not found: {group_id}")


def stages_for_group(group: dict[str, Any]) -> list[dict[str, Any]]:
    command_kind = group.get("command_kind")
    if command_kind == "system-tuning-discover":
        return [
            stage(
                "discover",
                "system-tuning-discover",
                ["--config", str(group.get("config_path")), "--executor", "ssh", "--out", "ARTIFACT_DIR"],
                remote=True,
                artifact="ARTIFACT_DIR/catalog.json",
            )
        ]
    if command_kind == "session-tuning-sweep":
        gates = ["--allow-session-tuning"] if group.get("requires_opt_in") else []
        return [
            stage("plan", "session-tuning-sweep-plan", ["--sweep", str(group.get("config_path")), "--out", "ARTIFACT_DIR/plan.json"], artifact="ARTIFACT_DIR/plan.json"),
            stage("preview", "session-tuning-sweep-preview", ["--plan", "ARTIFACT_DIR/plan.json", "--out", "ARTIFACT_DIR/preview.json"], artifact="ARTIFACT_DIR/preview.json"),
            stage("run", "session-tuning-sweep-run", ["--config", "config/local.gx10.json", "--plan", "ARTIFACT_DIR/plan.json", "--out", "ARTIFACT_DIR/live", *gates], remote=True, required_gates=gates, artifact="ARTIFACT_DIR/live/results.jsonl"),
            stage("rank", "session-tuning-sweep-rank", ["--plan", "ARTIFACT_DIR/plan.json", "--results", "ARTIFACT_DIR/live/results.jsonl", "--out", "ARTIFACT_DIR/live/ranking.json"], artifact="ARTIFACT_DIR/live/ranking.json"),
            stage("report", "canonical-report", ["--family", "session-tuning-sweep", "--label", str(group.get("id")), "--ranking", "ARTIFACT_DIR/live/ranking.json", "--out", "ARTIFACT_DIR/canonical-report.json"], artifact="ARTIFACT_DIR/canonical-report.json"),
        ]
    gates = ["--allow-risky-session-flags"] if group.get("safety_tier") == "risky-session" else []
    return [
        stage("plan", "optimize-workload", ["--mode", "plan", "--sweep", str(group.get("config_path")), "--out", "ARTIFACT_DIR"], artifact="ARTIFACT_DIR/pipeline-plan.json"),
        stage("preview", "optimize-workload", ["--mode", "preview", "--sweep", str(group.get("config_path")), "--out", "ARTIFACT_DIR", *gates], required_gates=gates, artifact="ARTIFACT_DIR/sweep-preview.json"),
        stage("run", "optimize-workload", ["--mode", "run", "--sweep", str(group.get("config_path")), "--out", "ARTIFACT_DIR", "--config", "config/local.gx10.json", *gates], remote=True, required_gates=gates, artifact="ARTIFACT_DIR/live/results.jsonl"),
        stage("report", "optimize-workload", ["--mode", "report", "--sweep", str(group.get("config_path")), "--out", "ARTIFACT_DIR", *gates], required_gates=gates, artifact="ARTIFACT_DIR/report.json"),
        stage("confirm", "optimize-workload", ["--mode", "confirm", "--sweep", str(group.get("config_path")), "--out", "ARTIFACT_DIR"], artifact="ARTIFACT_DIR/confirmation/confirmation-report.json"),
        stage("promote", "promote-confirmed-profile", ["--confirmation-report", "ARTIFACT_DIR/confirmation/confirmation-report.json", "--ranking", "ARTIFACT_DIR/live/ranking.json", "--force"], required_gates=["--allow-promotion"], artifact="PROFILE_OUT"),
    ]


def stage(
    name: str,
    command: str,
    args: list[str],
    *,
    remote: bool = False,
    required_gates: list[str] | None = None,
    artifact: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "command": command,
        "args": args,
        "command_hint": "uv run vllm-optimizer " + " ".join([command, *args]),
        "remote": remote,
        "required_gates": required_gates or [],
        "artifact": artifact,
    }


def render_pipeline_control_html(manifest: dict[str, Any]) -> str:
    group = manifest.get("group", {})
    rows = []
    for item in manifest.get("stages", []):
        if not isinstance(item, dict):
            continue
        rows.append(
            f"""
            <tr>
              <td>{escape(str(item.get('name')))}</td>
              <td>{escape(str(item.get('remote')))}</td>
              <td>{escape(', '.join(item.get('required_gates') or []) or 'none')}</td>
              <td><code>{escape(str(item.get('command_hint')))}</code></td>
            </tr>"""
        )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Pipeline Control</title>",
            f"  <style>{CSS}</style>",
            "</head>",
            "<body>",
            '<main class="shell">',
            f"<header><h1>Pipeline Control</h1><p>{escape(str(group.get('label') or group.get('id')))}</p></header>",
            f"<section class=\"panel\"><h2>Safety</h2><p>Tier: <strong>{escape(str(group.get('safety_tier')))}</strong>. Promotion automatic: <strong>{escape(str(manifest.get('promotion', {}).get('automatic')))}</strong>.</p></section>",
            f"<section class=\"panel\"><h2>Stages</h2><table><thead><tr><th>Name</th><th>Remote</th><th>Gates</th><th>Command</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>",
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


CSS = """
:root { --bg:#f6f8fb; --ink:#141820; --muted:#657284; --panel:#fff; --line:#d9e2ec; --accent:#245f9d; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.shell { max-width:1160px; margin:0 auto; padding:34px 22px 48px; }
header { margin-bottom:20px; }
h1 { margin:0 0 8px; font-size:42px; letter-spacing:0; }
h2 { margin:0 0 12px; font-size:20px; letter-spacing:0; }
p { color:var(--muted); }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:18px; margin-bottom:16px; box-shadow:0 18px 45px rgba(20,24,31,.07); }
table { width:100%; border-collapse:collapse; table-layout:fixed; }
th,td { padding:11px 9px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; overflow-wrap:anywhere; }
th { color:var(--muted); font-size:12px; text-transform:uppercase; }
code { font-family:"Cascadia Mono", Consolas, monospace; font-size:.9em; }
"""
