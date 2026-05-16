from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .artifacts import write_json
from .optimizer_pipeline import OptimizerPipelineRequest, run_optimizer_pipeline
from .sweep import build_sweep_plan, build_sweep_preview, load_sweep_definition


PipelineRunner = Callable[[OptimizerPipelineRequest], dict[str, Any]]


class CockpitControllerError(ValueError):
    """Raised when a cockpit controller request is outside its safety envelope."""


@dataclass(frozen=True)
class CockpitPreviewRequest:
    sweep_path: Path
    out_dir: Path
    allow_risky_session_flags: bool = False


@dataclass(frozen=True)
class CockpitRunRequest:
    sweep_path: Path
    config_path: Path
    out_dir: Path
    confirm_live_run: bool = False
    timeout_seconds: int = 1200
    continue_on_failure: bool = False
    allow_risky_session_flags: bool = False
    pipeline_runner: PipelineRunner | None = None


def run_cockpit_preview(request: CockpitPreviewRequest) -> dict[str, Any]:
    _require_under(request.sweep_path, Path("config"), "sweep_path")
    _require_under(request.out_dir, Path("artifacts"), "out_dir")

    definition = load_sweep_definition(request.sweep_path)
    plan = build_sweep_plan(
        definition,
        allow_risky_session_flags=request.allow_risky_session_flags,
    )
    preview = build_sweep_preview(plan)
    preview_exit_code = 2 if preview["blocked"] else 0

    plan_path = request.out_dir / "sweep-plan.json"
    preview_path = request.out_dir / "sweep-preview.json"
    result_path = request.out_dir / "controller-result.json"

    result = {
        "action": "preview",
        "status": "blocked" if preview["blocked"] else "ready",
        "blocked": preview["blocked"],
        "sweep_path": request.sweep_path.as_posix(),
        "out_dir": request.out_dir.as_posix(),
        "plan_path": plan_path.as_posix(),
        "preview_path": preview_path.as_posix(),
        "result_path": result_path.as_posix(),
        "preview_exit_code": preview_exit_code,
        "remote_execution": False,
        "promotion": False,
    }

    write_json(plan_path, plan)
    write_json(preview_path, preview)
    write_json(result_path, result)
    return result


def run_cockpit_live(request: CockpitRunRequest) -> dict[str, Any]:
    if not request.confirm_live_run:
        raise CockpitControllerError("live run control requires --confirm-live-run")
    _require_under(request.sweep_path, Path("config"), "sweep_path")
    _require_under(request.config_path, Path("config"), "config_path")
    _require_under(request.out_dir, Path("artifacts"), "out_dir")

    pipeline_request = OptimizerPipelineRequest(
        mode="run",
        sweep_path=request.sweep_path,
        out_dir=request.out_dir,
        config_path=request.config_path,
        timeout_seconds=request.timeout_seconds,
        continue_on_failure=request.continue_on_failure,
        allow_risky_session_flags=request.allow_risky_session_flags,
    )
    runner = request.pipeline_runner or run_optimizer_pipeline
    summary = runner(pipeline_request)
    result_path = request.out_dir / "controller-result.json"
    result = {
        "action": "run",
        "status": "submitted",
        "confirmed": True,
        "remote_execution": True,
        "promotion": False,
        "sweep_path": request.sweep_path.as_posix(),
        "config_path": request.config_path.as_posix(),
        "out_dir": request.out_dir.as_posix(),
        "result_path": result_path.as_posix(),
        "pipeline_summary": summary,
    }
    write_json(result_path, result)
    return result


def _require_under(path: Path, root: Path, label: str) -> None:
    base = (Path.cwd() / root).resolve()
    target = (Path.cwd() / path).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise CockpitControllerError(
            f"{label} must stay under {root.as_posix()}: {path.as_posix()}"
        ) from exc
