from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from .ab_confirmation import AbConfirmationInputs, build_ab_confirmation_report
from .artifacts import read_json, write_json
from .benchmark import load_prompt_set
from .discovery import load_target
from .promotion import write_confirmed_promoted_profile, write_promoted_profile
from .report import ReportInputs, build_comparison_report
from .sweep import (
    build_sweep_plan,
    build_sweep_preview,
    load_sweep_definition,
    load_sweep_results,
    rank_sweep_results,
    run_sweep,
)


PipelineMode = Literal["plan", "preview", "run", "report", "confirm"]


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
    current_profile_path: Path | None = None
    prompts_path: Path | None = None
    candidate_profile_out: Path | None = None
    confirmed_profile_out: Path | None = None
    promotion_summary_out: Path | None = None
    confirmation_repetitions: int = 3
    original_label: str = "current"
    recommended_label: str = "candidate"
    allow_promotion: bool = False


def run_optimizer_pipeline(request: OptimizerPipelineRequest) -> dict[str, Any]:
    artifacts = pipeline_artifacts(request.out_dir)
    request.out_dir.mkdir(parents=True, exist_ok=True)
    pipeline_plan = build_pipeline_plan(request, artifacts)
    write_json(Path(artifacts["pipeline_plan"]), pipeline_plan)

    completed = ["plan"]
    if request.mode in {"preview", "run", "report", "confirm"}:
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
        write_pipeline_report(sweep_plan, artifacts)
        completed.append("report")
    if request.mode == "confirm":
        sweep_plan = ensure_sweep_plan(request, artifacts)
        write_pipeline_report(sweep_plan, artifacts)
        completed.append("report")
        confirmation = run_confirmation_stage(request, artifacts)
        completed.append("confirm")
    else:
        confirmation = {}

    summary = build_summary(request, artifacts, completed, confirmation)
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
            {"name": "confirm", "artifact": artifacts["confirmation_report_json"], "remote": False},
        ],
        "remote_actions": [] if request.mode in {"plan", "preview", "report", "confirm"} else ["run live sweep"],
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


def write_pipeline_report(sweep_plan: dict[str, Any], artifacts: dict[str, str]) -> None:
    ensure_ranking(sweep_plan, artifacts)
    report = build_comparison_report(
        ReportInputs(
            baseline=Path(sweep_plan["baseline_summary_path"]) if sweep_plan.get("baseline_summary_path") else None,
            sweep_ranking=Path(artifacts["ranking"]),
        )
    )
    write_json(Path(artifacts["report_json"]), report)
    Path(artifacts["report_markdown"]).write_text(report["markdown"], encoding="utf-8")


def run_confirmation_stage(request: OptimizerPipelineRequest, artifacts: dict[str, str]) -> dict[str, Any]:
    validate_confirmation_request(request)
    candidate_profile = request.candidate_profile_out
    current_profile = read_json(request.current_profile_path)  # type: ignore[arg-type]
    fallback_profile_id = request.confirmed_profile_out.stem if request.confirmed_profile_out else "confirmed"
    current_profile_id = str(current_profile.get("profile_id") or fallback_profile_id)
    confirmation_report = Path(artifacts["confirmation_report_json"])
    confirmation_markdown = Path(artifacts["confirmation_report_markdown"])
    write_promoted_profile(
        ranking_path=Path(artifacts["ranking"]),
        profile_out=candidate_profile,  # type: ignore[arg-type]
        summary_out=Path(artifacts["candidate_summary_markdown"]),
        profile_id=(candidate_profile.stem if candidate_profile is not None else "candidate"),
        force=True,
    )
    original_summaries = confirmation_summary_paths(
        Path(artifacts["confirmation_dir"]), "current", request.confirmation_repetitions
    )
    recommended_summaries = confirmation_summary_paths(
        Path(artifacts["confirmation_dir"]), "candidate", request.confirmation_repetitions
    )
    prompt_set_id = str(read_json(request.prompts_path).get("prompt_set_id"))  # type: ignore[arg-type]
    report = build_ab_confirmation_report(
        AbConfirmationInputs(
            original_label=request.original_label,
            recommended_label=request.recommended_label,
            original_summaries=tuple(original_summaries),
            recommended_summaries=tuple(recommended_summaries),
            prompt_set_id=prompt_set_id,
        )
    )
    write_json(confirmation_report, report)
    confirmation_markdown.parent.mkdir(parents=True, exist_ok=True)
    confirmation_markdown.write_text(report["markdown"], encoding="utf-8")
    promoted = False
    if request.allow_promotion:
        if request.confirmed_profile_out is None:
            raise OptimizerPipelineError("confirmed profile output is required when promotion is allowed")
        write_confirmed_promoted_profile(
            confirmation_report_path=confirmation_report,
            ranking_path=Path(artifacts["ranking"]),
            profile_out=request.confirmed_profile_out,
            summary_out=request.promotion_summary_out or Path(artifacts["promotion_summary_markdown"]),
            profile_id=current_profile_id,
            expected_recommended_label=request.recommended_label,
            force=True,
        )
        promoted = True
    return {
        "confirmation_report": confirmation_report.as_posix(),
        "candidate_profile": candidate_profile.as_posix() if candidate_profile else None,
        "allowed": request.allow_promotion,
        "promoted": promoted,
        "decision": report.get("decision", {}),
    }


def validate_confirmation_request(request: OptimizerPipelineRequest) -> None:
    missing = []
    for name, value in (
        ("current profile", request.current_profile_path),
        ("prompts", request.prompts_path),
        ("candidate profile output", request.candidate_profile_out),
    ):
        if value is None:
            missing.append(name)
    if missing:
        raise OptimizerPipelineError("confirm mode requires " + ", ".join(missing))
    if request.confirmation_repetitions < 1:
        raise OptimizerPipelineError("confirmation repetitions must be positive")


def confirmation_summary_paths(root: Path, prefix: str, count: int) -> list[Path]:
    paths = [root / f"{prefix}-r{index}" / "summary.json" for index in range(1, count + 1)]
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise OptimizerPipelineError(f"confirmation summaries are missing: {', '.join(path.as_posix() for path in missing)}")
    return paths


def build_summary(
    request: OptimizerPipelineRequest,
    artifacts: dict[str, str],
    completed: list[str],
    confirmation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "generated_at": _now(),
        "mode": request.mode,
        "completed_stages": completed,
        "artifacts": artifacts,
        "promotion": {"automatic": False, **(confirmation or {})},
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
        "confirmation_dir": (out_dir / "confirmation").as_posix(),
        "confirmation_report_json": (out_dir / "confirmation" / "confirmation-report.json").as_posix(),
        "confirmation_report_markdown": (out_dir / "confirmation" / "confirmation-report.md").as_posix(),
        "candidate_summary_markdown": (out_dir / "confirmation" / "candidate-profile.md").as_posix(),
        "promotion_summary_markdown": (out_dir / "confirmation" / "promotion-summary.md").as_posix(),
    }


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
