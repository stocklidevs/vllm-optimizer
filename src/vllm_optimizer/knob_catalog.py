from __future__ import annotations

from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from .artifacts import write_json


class KnobCatalogError(ValueError):
    """Raised when knob group catalog generation fails."""


def write_knob_catalog(config_root: Path, out_path: Path, html_out: Path | None = None) -> dict[str, str]:
    catalog = build_knob_catalog(config_root)
    write_json(out_path, catalog)
    artifacts = {"catalog_path": out_path.as_posix()}
    if html_out is not None:
        html_out.parent.mkdir(parents=True, exist_ok=True)
        html_out.write_text(render_knob_catalog_html(catalog), encoding="utf-8")
        artifacts["html_path"] = html_out.as_posix()
    return artifacts


def build_knob_catalog(config_root: Path) -> dict[str, Any]:
    if not config_root.exists():
        raise KnobCatalogError(f"config root does not exist: {config_root}")
    paths = []
    for relative in ("sweeps", "session-tuning-sweeps"):
        folder = config_root / relative
        if folder.exists():
            paths.extend(sorted(folder.glob("*.json")))
    groups = [classify_group(path) for path in paths]
    groups.append(
        {
            "id": "system-tuning-discovery",
            "label": "System Tuning Discovery",
            "family": "read-only-discovery",
            "safety_tier": "read-only",
            "config_path": "config/local.gx10.json",
            "command_kind": "system-tuning-discover",
            "requires_opt_in": False,
            "description": "Read-only Linux, NVIDIA, and runtime tuning discovery.",
            "action_scope": "read-only",
        }
    )
    groups = sorted(groups, key=lambda group: (group["family"], group["id"]))
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "config_root": config_root.as_posix(),
        "group_count": len(groups),
        "groups": groups,
    }


def classify_group(path: Path) -> dict[str, Any]:
    stem = path.stem
    family = infer_family(path)
    safety_tier = infer_safety(path, family)
    command_kind = "session-tuning-sweep" if "session-tuning-sweeps" in path.as_posix() else "sweep"
    display_label = display_label_for(stem, family)
    return {
        "id": stem,
        "label": labelize(stem),
        "display_label": display_label,
        "display_family": display_family_for(stem, family),
        "family": family,
        "safety_tier": safety_tier,
        "config_path": path.as_posix(),
        "command_kind": command_kind,
        "requires_opt_in": safety_tier in {"risky-session", "session-tuning"},
        "description": description_for(stem, family, safety_tier),
        "knobs_tuned": knobs_tuned_for(stem, family, command_kind),
        "action_scope": action_scope_for(safety_tier),
    }


def infer_family(path: Path) -> str:
    text = path.as_posix().lower()
    name = path.stem.lower()
    if "session-tuning-sweeps" in text:
        return "session-tuning"
    if "concurrency" in name:
        return "concurrency"
    if "high-impact" in name:
        return "workload"
    if "fp8" in name:
        return "fp8"
    if "risky" in name:
        return "risky-session"
    if "scheduler" in name or "expanded" in name or "small-sweep" in name or "top2" in name:
        return "safe-vllm"
    return "safe-vllm"


def infer_safety(path: Path, family: str) -> str:
    name = path.stem.lower()
    if family == "session-tuning":
        return "session-tuning"
    if "risky" in name:
        return "risky-session"
    return "safe-session"


def action_scope_for(safety_tier: str) -> str:
    if safety_tier == "read-only":
        return "read-only"
    if safety_tier in {"risky-session", "session-tuning", "safe-session"}:
        return "session-mutating" if safety_tier != "safe-session" else "vllm-session"
    return "local-only"


def description_for(stem: str, family: str, safety_tier: str) -> str:
    if family == "concurrency":
        return "Explore request concurrency and saturation behavior."
    if family == "workload":
        return "Optimize a workload-specific prompt and request mix."
    if family == "fp8":
        return "Explore FP8/KV cache related candidates and compatibility."
    if family == "session-tuning":
        return "Compare shell-scoped runtime environment tuning profiles."
    if safety_tier == "risky-session":
        return "Explore risky session-only vLLM flags with explicit opt-in."
    return "Explore safe vLLM serve parameter candidates."


def display_label_for(stem: str, family: str) -> str:
    name = stem.lower()
    if family == "concurrency":
        count = concurrency_count(name)
        return f"Concurrency - {count} Request{'s' if count != '1' else ''}" if count else "Concurrency Saturation"
    if family == "fp8":
        workload = workload_label(name)
        return f"FP8 KV Cache - {workload}" if workload else "FP8 KV Cache"
    if family == "workload":
        workload = workload_label(name)
        return f"Workload Shape - {workload}" if workload else "Workload Shape"
    if family == "session-tuning":
        return "Runtime Environment Session Sweep"
    if family == "risky-session":
        return "Risky Session vLLM Flags"
    if "small-sweep" in name:
        return "Safe vLLM Baseline Sweep"
    if "scheduler" in name:
        return "Scheduler and Prefill Sweep"
    if "expanded" in name:
        return "Expanded Safe vLLM Sweep"
    if "top2" in name:
        return "Top Two Stability Sweep"
    return labelize(stem)


def display_family_for(stem: str, family: str) -> str:
    if family == "fp8":
        return "FP8 KV Cache"
    if family == "concurrency":
        return "Concurrency"
    if family == "workload":
        return "Workload Shape"
    if family == "session-tuning":
        return "Runtime Environment"
    if family == "risky-session":
        return "Risky Session Flags"
    if "scheduler" in stem.lower():
        return "Scheduler and Prefill"
    return "Safe vLLM"


def knobs_tuned_for(stem: str, family: str, command_kind: str) -> list[str]:
    name = stem.lower()
    if family == "fp8":
        return ["kv_cache_dtype", "block_size", "max_num_batched_tokens", "max_num_seqs"]
    if family == "concurrency":
        return ["request_concurrency", "gpu_memory_utilization", "max_num_batched_tokens", "max_num_seqs"]
    if family == "workload":
        return ["prompt_set", "workload_mix", "performance_mode", "max_model_len"]
    if command_kind == "session-tuning-sweep":
        return ["environment_variables", "ulimit", "session_scope"]
    if family == "risky-session":
        return ["risky_vllm_flags", "scheduler_flags", "session_only"]
    if "scheduler" in name:
        return ["max_num_batched_tokens", "max_num_seqs", "enable_chunked_prefill", "enable_prefix_caching"]
    return ["gpu_memory_utilization", "max_model_len", "performance_mode", "safe_vllm_flags"]


def concurrency_count(name: str) -> str | None:
    marker = "saturation-c"
    if marker not in name:
        return None
    suffix = name.split(marker, 1)[1].split("-", 1)[0]
    return suffix if suffix.isdigit() else None


def workload_label(name: str) -> str:
    if "interactive" in name:
        return "Interactive Coding"
    if "tool-json" in name:
        return "Tool JSON"
    if "long" in name:
        return "Long Context"
    return ""


def labelize(stem: str) -> str:
    words = [word for word in stem.replace("-", " ").replace("_", " ").split() if word]
    return " ".join(word.upper() if word in {"fp8", "kv"} else word.capitalize() for word in words)


def render_knob_catalog_html(catalog: dict[str, Any]) -> str:
    groups = catalog.get("groups", [])
    cards = []
    for group in groups if isinstance(groups, list) else []:
        if not isinstance(group, dict):
            continue
        opt_in = "requires opt-in" if group.get("requires_opt_in") else "no extra opt-in"
        cards.append(
            f"""
            <article class="card {escape(str(group.get('safety_tier')))}">
              <div class="topline"><span>{escape(str(group.get('display_family') or group.get('family')))}</span><strong>{escape(str(group.get('safety_tier')))}</strong></div>
              <h2>{escape(str(group.get('display_label') or group.get('label')))}</h2>
              <p>{escape(str(group.get('description')))}</p>
              <dl>
                <div><dt>Command</dt><dd>{escape(str(group.get('command_kind')))}</dd></div>
                <div><dt>Knobs tuned</dt><dd>{escape(', '.join(str(item) for item in group.get('knobs_tuned', [])) or 'n/a')}</dd></div>
                <div><dt>Config</dt><dd><code>{escape(str(group.get('config_path')))}</code></dd></div>
                <div><dt>Gate</dt><dd>{escape(opt_in)}</dd></div>
              </dl>
            </article>"""
        )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Tuning Area Selector</title>",
            f"  <style>{CSS}</style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            "    <header>",
            "      <h1>Tuning Area Selector</h1>",
            "      <p>Choose an optimization area. Safety tiers, knobs tuned, and opt-in gates come from the deterministic catalog.</p>",
            "    </header>",
            f"    <section class=\"grid\">{''.join(cards)}</section>",
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


CSS = """
:root { --bg:#f6f8fb; --ink:#141820; --muted:#647184; --panel:#fff; --line:#d9e2ec; --safe:#126b57; --risk:#a2442b; --session:#6d4bb6; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.shell { max-width:1180px; margin:0 auto; padding:34px 22px 48px; }
header { margin-bottom:24px; }
h1 { margin:0 0 10px; font-size:42px; letter-spacing:0; }
header p, .card p { color:var(--muted); line-height:1.55; }
.grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:18px; box-shadow:0 18px 45px rgba(20,24,31,.07); }
.topline { display:flex; justify-content:space-between; gap:12px; color:var(--muted); font-size:12px; text-transform:uppercase; font-weight:760; }
.topline strong { color:var(--safe); }
.risky-session .topline strong { color:var(--risk); }
.session-tuning .topline strong { color:var(--session); }
h2 { margin:16px 0 8px; font-size:21px; letter-spacing:0; }
dl { display:grid; gap:10px; margin:16px 0 0; }
dt { color:var(--muted); font-size:12px; text-transform:uppercase; font-weight:760; }
dd { margin:2px 0 0; overflow-wrap:anywhere; }
code { font-family:"Cascadia Mono", Consolas, monospace; font-size:.9em; }
"""
