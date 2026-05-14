from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from .artifacts import read_json, write_json
from .discovery import load_target
from .report import ReportInputs, build_comparison_report
from .sweep import (
    build_sweep_plan,
    build_sweep_preview,
    load_sweep_definition,
    load_sweep_results,
    rank_sweep_results,
    run_sweep,
)
from .benchmark import load_prompt_set


PipelineMode = Literal["plan", "preview", "run", "report"]


class OptimizerPipelineError(ValueError):
    """Raised when an optimization pipeline stage cannot run."""


@dataclass(frozen=True)
class OptimizerPipelineRequest:
    mode: PipelineMode
    sweep_path: Path
    out_dir: Path
    config_path: Path | None = None
    timeout_seconds: int = 1200
    continue_on_failure: bool = False
    allow_risky_session_flags: bool = False


def run_optimizer_pipeline(request: OptimizerPipelineRequest) -> dict[str, Any]:
    artifacts = pipeline_artifacts(request.out_dir)
    request.out_dir.mkdir(parents=True, exist_ok=True)
    pipeline_plan = build_pipeline_plan(request, artifacts)
    write_json(Path(artifacts["pipeline_plan"]), pipeline_plan)

    completed = ["plan"]
    if request.mode in {"preview", "run", "report"}:
        sweep_plan = ensure_sweep_plan(request, artifacts)
        preview = build_sweep_preview(sweep_plan)
        write_json(Path(artifacts["sweep_preview"]), preview)
        completed.append("preview")
    if request.mode == "run":
        if request.config_path is None:
            raise OptimizerPipelineError("remote config is required for run mode")
        run_live_sweep(request, sweep_plan, artifacts)
        completed.append("run")
    if request.mode == "report":
        sweep_plan = ensure_sweep_plan(request, artifacts)
        ensure_ranking(sweep_plan, artifacts)
        report = build_comparison_report(
            ReportInputs(
                baseline=Path(sweep_plan["baseline_summary_path"])
                if sweep_plan.get("baseline_summary_path")
                else None,
                sweep_ranking=Path(artifacts["ranking"]),
            )
        )
        write_json(Path(artifacts["report_json"]), report)
        Path(artifacts["report_markdown"]).write_text(report["markdown"], encoding="utf-8")
        completed.append("report")

    summary = build_summary(request, artifacts, completed)
    write_json(Path(artifacts["pipeline_summary"]), summary)
    return summary


def build_pipeline_plan(request: OptimizerPipelineRequest, artifacts: dict[str, str]) -> dict[str, Any]:
    return {
        "generated_at": _now(),
        "mode": request.mode,
        "sweep_path": request.sweep_path.as_posix(),
        "out_dir": request.out_dir.as_posix(),
        "artifacts": artifacts,
        "stages": [
            {"name": "plan", "artifact": artifacts["pipeline_plan"], "remote": False},
            {"name": "preview", "artifact": artifacts["sweep_preview"], "remote": False},
            {"name": "run", "artifact": artifacts["live_dir"], "remote": True},
            {"name": "report", "artifact": artifacts["report_json"], "remote": False},
        ],
        "remote_actions": [] if request.mode in {"plan", "preview", "report"} else ["run live sweep"],
        "promotion": {"automatic": False, "note": "Promotion remains an explicit separate command."},
        "safety": {
            "allow_risky_session_flags": request.allow_risky_session_flags,
            "continue_on_failure": request.continue_on_failure,
        },
    }


def ensure_sweep_plan(request: OptimizerPipelineRequest, artifacts: dict[str, str]) -> dict[str, Any]:
    path = Path(artifacts["sweep_plan"])
    if path.exists():
        return read_json(path)
    definition = load_sweep_definition(request.sweep_path)
    plan = build_sweep_plan(definition, allow_risky_session_flags=request.allow_risky_session_flags)
    write_json(path, plan)
    return plan


def run_live_sweep(request: OptimizerPipelineRequest, sweep_plan: dict[str, Any], artifacts: dict[str, str]) -> None:
    if sweep_plan.get("has_risky_session_flags") and not request.allow_risky_session_flags:
        raise OptimizerPipelineError("risky-session sweep requires --allow-risky-session-flags")
    target = load_target(request.config_path)  # type: ignore[arg-type]
    prompts = load_prompt_set(Path(sweep_plan["prompts_path"]))
    run_sweep(
        target,
        sweep_plan,
        prompts,
        Path(artifacts["live_dir"]),
        request.timeout_seconds,
        request.continue_on_failure,
    )


def ensure_ranking(sweep_plan: dict[str, Any], artifacts: dict[str, str]) -> None:
    ranking_path = Path(artifacts["ranking"])
    if ranking_path.exists():
        return
    results_path = Path(artifacts["results"])
    if not results_path.exists():
        raise OptimizerPipelineError(f"results artifact is required for report mode: {results_path}")
    rows = load_sweep_results(results_path)
    ranking = rank_sweep_results(sweep_plan, rows)
    ranking_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(ranking_path, ranking)


def build_summary(request: OptimizerPipelineRequest, artifacts: dict[str, str], completed: list[str]) -> dict[str, Any]:
    return {
        "generated_at": _now(),
        "mode": request.mode,
        "completed_stages": completed,
        "artifacts": artifacts,
        "promotion": {"automatic": False},
    }


def pipeline_artifacts(out_dir: Path) -> dict[str, str]:
    return {
        "pipeline_plan": (out_dir / "pipeline-plan.json").as_posix(),
        "pipeline_summary": (out_dir / "pipeline-summary.json").as_posix(),
        "sweep_plan": (out_dir / "sweep-plan.json").as_posix(),
        "sweep_preview": (out_dir / "sweep-preview.json").as_posix(),
        "live_dir": (out_dir / "live").as_posix(),
        "results": (out_dir / "live" / "results.jsonl").as_posix(),
        "ranking": (out_dir / "live" / "ranking.json").as_posix(),
        "report_json": (out_dir / "report.json").as_posix(),
        "report_markdown": (out_dir / "report.md").as_posix(),
    }


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
