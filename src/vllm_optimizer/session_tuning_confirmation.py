from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .ab_confirmation import AbConfirmationInputs, build_ab_confirmation_report
from .artifacts import write_json
from .benchmark import load_prompt_set, run_baseline_benchmark
from .discovery import DiscoveryTarget
from .serve_profiles import load_serve_profile
from .session_tuning import load_session_tuning_profile


class SessionTuningConfirmationError(ValueError):
    """Raised when session tuning confirmation cannot run safely."""


BenchmarkRunner = Callable[[Any, Any, Any, Path, int, Any | None], dict[str, Any]]


@dataclass(frozen=True)
class SessionTuningConfirmationRequest:
    target: DiscoveryTarget
    profile_path: Path
    prompts_path: Path
    session_tuning_path: Path
    out_dir: Path
    repetitions: int = 5
    current_label: str = "current"
    tuned_label: str = "tuned"
    timeout_seconds: int = 1200
    allow_session_tuning: bool = False
    noise_percent: float = 1.0
    benchmark_runner: BenchmarkRunner | None = None


def run_session_tuning_confirmation(request: SessionTuningConfirmationRequest) -> dict[str, Any]:
    validate_request(request)
    profile = load_serve_profile(request.profile_path)
    prompts = load_prompt_set(request.prompts_path)
    session_tuning = load_session_tuning_profile(request.session_tuning_path)
    runner = request.benchmark_runner or benchmark_runner_adapter
    current_summaries: list[Path] = []
    tuned_summaries: list[Path] = []
    for index in range(1, request.repetitions + 1):
        current_dir = request.out_dir / f"current-r{index}"
        tuned_dir = request.out_dir / f"tuned-r{index}"
        runner(request.target, profile, prompts, current_dir, request.timeout_seconds, None)
        runner(request.target, profile, prompts, tuned_dir, request.timeout_seconds, session_tuning)
        current_summaries.append(current_dir / "summary.json")
        tuned_summaries.append(tuned_dir / "summary.json")
    report = build_ab_confirmation_report(
        AbConfirmationInputs(
            original_label=request.current_label,
            recommended_label=request.tuned_label,
            original_summaries=tuple(current_summaries),
            recommended_summaries=tuple(tuned_summaries),
            prompt_set_id=prompts.prompt_set_id,
            noise_percent=request.noise_percent,
        )
    )
    report_json = request.out_dir / "confirmation-report.json"
    report_markdown = request.out_dir / "confirmation-report.md"
    summary_path = request.out_dir / "summary.json"
    write_json(report_json, report)
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.write_text(report["markdown"], encoding="utf-8")
    summary = {
        "profile_path": request.profile_path.as_posix(),
        "prompts_path": request.prompts_path.as_posix(),
        "session_tuning_path": request.session_tuning_path.as_posix(),
        "repetitions": request.repetitions,
        "current_label": request.current_label,
        "tuned_label": request.tuned_label,
        "decision": report["decision"],
        "artifact_paths": {
            "confirmation_report": report_json.as_posix(),
            "confirmation_markdown": report_markdown.as_posix(),
            "summary": summary_path.as_posix(),
            "current_summaries": [path.as_posix() for path in current_summaries],
            "tuned_summaries": [path.as_posix() for path in tuned_summaries],
        },
    }
    write_json(summary_path, summary)
    return summary


def validate_request(request: SessionTuningConfirmationRequest) -> None:
    if not request.allow_session_tuning:
        raise SessionTuningConfirmationError("session tuning confirmation requires --allow-session-tuning")
    if request.repetitions < 1:
        raise SessionTuningConfirmationError("repetitions must be positive")


def benchmark_runner_adapter(
    target: DiscoveryTarget,
    profile,
    prompt_set,
    out_dir: Path,
    timeout_seconds: int,
    session_tuning,
) -> dict[str, Any]:
    return run_baseline_benchmark(target, profile, prompt_set, out_dir, timeout_seconds, session_tuning)
