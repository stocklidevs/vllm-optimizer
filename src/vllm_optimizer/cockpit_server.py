from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import monotonic
from typing import Any, Callable

from .artifacts import read_json, read_jsonl, write_json
from .cockpit_controller import CockpitPreviewRequest, CockpitRunRequest, run_cockpit_live, run_cockpit_preview
from .optimizer_pipeline import OptimizerPipelineRequest, run_optimizer_pipeline
from .promotion import write_promoted_profile
from .sweep import load_sweep_definition
from .web_cockpit import read_profile_summaries, render_web_cockpit


class CockpitServerError(ValueError):
    """Raised when an active cockpit request is invalid or unsafe."""


@dataclass(frozen=True)
class CockpitServerConfig:
    sweep_path: Path
    out_dir: Path
    config_path: Path | None = None
    catalog_path: Path | None = None
    manifest_path: Path | None = None
    status_path: Path | None = None
    report_path: Path | None = None
    run_index_path: Path | None = None
    profile_paths: tuple[Path, ...] = ()
    allow_risky_session_flags: bool = False
    allow_promotion: bool = False
    timeout_seconds: int = 1200
    continue_on_failure: bool = False


ActionRunner = Callable[[str, dict[str, Any], CockpitServerConfig], dict[str, Any]]


class CockpitJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._last_job_id: str | None = None
        self._lock = threading.Lock()

    def start(
        self,
        action: str,
        payload: dict[str, Any],
        config: CockpitServerConfig,
        *,
        action_runner: ActionRunner | None = None,
    ) -> dict[str, Any]:
        job_id = uuid.uuid4().hex
        job = {
            "job_id": job_id,
            "action": action,
            "status": "running",
            "progress_percent": 5,
            "cancel_requested": False,
            "started_at_monotonic": monotonic(),
            "plain_summary": plain_summary(action, "running"),
            "result": None,
            "error": None,
        }
        with self._lock:
            self._jobs[job_id] = job
            self._last_job_id = job_id
            snapshot = _job_with_runtime_state(job)
        _persist_job(config, snapshot)
        thread = threading.Thread(
            target=self._run_job,
            args=(job_id, action, payload, config, action_runner or handle_controller_action),
            daemon=True,
        )
        thread.start()
        return self.get(job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            if job_id not in self._jobs:
                raise CockpitServerError(f"unknown job: {job_id}")
            return _job_with_runtime_state(self._jobs[job_id])

    def recent(self, config: CockpitServerConfig) -> dict[str, Any]:
        with self._lock:
            if self._last_job_id and self._last_job_id in self._jobs:
                return _job_with_runtime_state(self._jobs[self._last_job_id])
        path = _last_job_path(config)
        if not path.exists():
            raise CockpitServerError("no recent cockpit job")
        return read_json(path)

    def wait(self, job_id: str, timeout_seconds: float) -> dict[str, Any]:
        deadline = monotonic() + timeout_seconds
        while monotonic() < deadline:
            job = self.get(job_id)
            if job["status"] in {"completed", "failed", "cancelled"}:
                return job
            threading.Event().wait(0.01)
        return self.get(job_id)

    def cancel(self, job_id: str, config: CockpitServerConfig | None = None) -> dict[str, Any]:
        with self._lock:
            if job_id not in self._jobs:
                raise CockpitServerError(f"unknown job: {job_id}")
            job = self._jobs[job_id]
            if job["status"] in {"completed", "failed", "cancelled"}:
                return dict(job)
            job["cancel_requested"] = True
            job["status"] = "cancel-requested"
            job["progress_percent"] = max(int(job["progress_percent"]), 10)
            job["plain_summary"] = plain_summary(job["action"], "cancel-requested")
            snapshot = _job_with_runtime_state(job)
        if config is not None:
            _persist_job(config, snapshot)
        return snapshot

    def _run_job(
        self,
        job_id: str,
        action: str,
        payload: dict[str, Any],
        config: CockpitServerConfig,
        action_runner: ActionRunner,
    ) -> None:
        try:
            result = action_runner(action, payload, config)
            with self._lock:
                job = self._jobs[job_id]
                if job.get("cancel_requested"):
                    job["status"] = "cancel-requested"
                    job["progress_percent"] = max(int(job["progress_percent"]), 90)
                    job["result"] = result
                    job["plain_summary"] = plain_summary(action, "cancel-requested")
                    snapshot = _job_with_runtime_state(job)
                    _persist_job(config, snapshot)
                    return
                job["status"] = "completed"
                job["progress_percent"] = 100
                job["result"] = result
                job["plain_summary"] = plain_summary(action, "completed", result)
                snapshot = _job_with_runtime_state(job)
            _persist_job(config, snapshot)
        except Exception as exc:  # pragma: no cover - defensive job boundary
            diagnostics = failure_diagnostics(action, exc, config)
            with self._lock:
                job = self._jobs[job_id]
                job["status"] = "failed"
                job["progress_percent"] = 100
                job["error"] = str(exc)
                job["diagnostics"] = diagnostics
                job["plain_summary"] = plain_summary(action, "failed", {"error": str(exc), "diagnostics": diagnostics})
                snapshot = _job_with_runtime_state(job)
            _persist_job(config, snapshot)


def handle_controller_action(
    action: str,
    payload: dict[str, Any],
    config: CockpitServerConfig,
    *,
    pipeline_runner: Callable[[OptimizerPipelineRequest], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    runner = pipeline_runner or run_optimizer_pipeline
    if action == "plan":
        summary = runner(
            OptimizerPipelineRequest(
                mode="plan",
                sweep_path=config.sweep_path,
                out_dir=config.out_dir,
                allow_risky_session_flags=config.allow_risky_session_flags,
            )
        )
        result = {
            "action": "plan",
            "status": "completed",
            "remote_execution": False,
            "artifacts": summary["artifacts"],
            "pipeline_summary": summary,
        }
        write_json(config.out_dir / "controller-result.json", result)
        return result
    if action == "report":
        summary = runner(
            OptimizerPipelineRequest(
                mode="report",
                sweep_path=config.sweep_path,
                out_dir=config.out_dir,
                allow_risky_session_flags=config.allow_risky_session_flags,
            )
        )
        result = {
            "action": "report",
            "status": "completed",
            "remote_execution": False,
            "promotion": False,
            "artifacts": summary["artifacts"],
            "pipeline_summary": summary,
        }
        write_json(config.out_dir / "controller-result.json", result)
        return result
    if action == "preview":
        return run_cockpit_preview(
            CockpitPreviewRequest(
                sweep_path=config.sweep_path,
                out_dir=config.out_dir,
                allow_risky_session_flags=config.allow_risky_session_flags,
            )
        )
    if action == "run":
        if not payload.get("confirm_live_run"):
            raise CockpitServerError("run action requires confirm_live_run")
        if config.config_path is None:
            raise CockpitServerError("run action requires config_path")
        return run_cockpit_live(
            CockpitRunRequest(
                sweep_path=config.sweep_path,
                config_path=config.config_path,
                out_dir=config.out_dir,
                confirm_live_run=True,
                timeout_seconds=config.timeout_seconds,
                continue_on_failure=config.continue_on_failure,
                allow_risky_session_flags=config.allow_risky_session_flags,
            )
        )
    if action == "promote":
        if not config.allow_promotion:
            raise CockpitServerError("promote action requires allow_promotion / --allow-promotion")
        candidate_id = payload.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            candidate_id = None
        objective = _promotion_objective(payload.get("objective"))
        profile_id = str(payload.get("profile_id") or "cockpit-selected-candidate")
        promotion_dir = config.out_dir / "promotion"
        profile_out = promotion_dir / "selected-candidate-profile.json"
        summary_out = promotion_dir / "promotion-summary.md"
        promoted = write_promoted_profile(
            ranking_path=config.out_dir / "live" / "ranking.json",
            profile_out=profile_out,
            summary_out=summary_out,
            objective=objective,
            profile_id=profile_id,
            force=True,
            candidate_id=candidate_id,
        )
        selected = str(promoted.get("preview", {}).get("candidate_id") or candidate_id or "")
        result = {
            "action": "promote",
            "status": "completed",
            "remote_execution": False,
            "promotion": True,
            "candidate_id": selected,
            "objective": objective,
            "artifacts": {
                "profile_json": profile_out.as_posix(),
                "summary_markdown": summary_out.as_posix(),
            },
            "pipeline_summary": {
                "mode": "promote",
                "completed_stages": ["plan", "preview", "run", "report", "promote"],
                "artifacts": {
                    "profile_json": profile_out.as_posix(),
                    "summary_markdown": summary_out.as_posix(),
                },
            },
        }
        write_json(config.out_dir / "controller-result.json", result)
        return result
    raise CockpitServerError(f"unsupported controller action: {action}")


def _promotion_objective(value: Any) -> str:
    objective = str(value or "balanced")
    if objective == "performance":
        return "throughput"
    if objective == "single_user":
        return "single_user"
    if objective in {"stability", "tool_use"}:
        return "balanced"
    return objective


def _job_with_runtime_state(job: dict[str, Any]) -> dict[str, Any]:
    visible = dict(job)
    elapsed = max(0, int(monotonic() - float(job.get("started_at_monotonic", monotonic()))))
    visible["elapsed_seconds"] = elapsed
    if visible.get("status") in {"running", "cancel-requested"}:
        heartbeat = min(85, 8 + (elapsed * 2))
        visible["progress_percent"] = max(int(visible.get("progress_percent") or 0), heartbeat)
        visible["plain_summary"] = plain_summary(str(visible.get("action") or "action"), str(visible.get("status") or "running"), visible)
    return visible


def _last_job_path(config: CockpitServerConfig) -> Path:
    return config.out_dir / "controller-last-job.json"


def _persist_job(config: CockpitServerConfig, job: dict[str, Any]) -> None:
    write_json(_last_job_path(config), job)
    if job.get("status") == "failed":
        write_json(config.out_dir / "controller-failure.json", job)


def failure_diagnostics(action: str, error: Exception, config: CockpitServerConfig) -> dict[str, Any]:
    message = str(error) or error.__class__.__name__
    artifacts = {
        "pipeline_plan": (config.out_dir / "pipeline-plan.json").as_posix(),
        "sweep_plan": (config.out_dir / "sweep-plan.json").as_posix(),
        "results": (config.out_dir / "live" / "results.jsonl").as_posix(),
        "ranking": (config.out_dir / "live" / "ranking.json").as_posix(),
        "report": (config.out_dir / "report.json").as_posix(),
        "failure_record": (config.out_dir / "controller-failure.json").as_posix(),
    }
    failed_trials = _failed_trial_context(config.out_dir / "live" / "results.jsonl")
    lowered = message.lower()
    if "no rankable sweep trials" in lowered:
        likely_cause = "No successful trial was available to rank. The live sweep probably failed before any candidate produced benchmark metrics."
        next_steps = [
            "Open live/results.jsonl and inspect the first failed trial reason.",
            "Check the GX10 vLLM serve startup logs for the failed trial.",
            "Retry after fixing the remote serve/config issue, or run with continue-on-failure if you want later candidates to keep going.",
        ]
    elif "stale sweep artifacts" in lowered:
        likely_cause = "The output directory contains artifacts from a different sweep."
        next_steps = [
            "Start a fresh optimization in a sweep-specific output directory.",
            "Use Generate & Review Report only after the current sweep has matching live results.",
        ]
    elif "config_path" in lowered or "remote config" in lowered:
        likely_cause = "The live run is missing the GX10 connection config."
        next_steps = [
            "Launch the cockpit with --config config/local.gx10.json.",
            "Confirm the config file still points at the Tailscale SSH target.",
        ]
    elif "risky-session sweep requires --allow-risky-session-flags" in lowered:
        likely_cause = (
            "This sweep includes risky-session knobs, but the cockpit controller was started without "
            "--allow-risky-session-flags."
        )
        next_steps = [
            "Restart direct cockpit-server or cockpit-run commands with --allow-risky-session-flags.",
            "Use cockpit-launch for default sweeps so sweep-level risky-session allowance is applied automatically.",
            "Choose a safe-session tuning area if you do not want to allow risky-session knobs.",
        ]
    elif "timeout" in lowered or "timed out" in lowered:
        likely_cause = "A remote step timed out before the benchmark completed."
        next_steps = [
            "Check whether the GX10 is reachable over Tailscale SSH.",
            "Inspect the trial server log artifact and increase the timeout if the model is still loading.",
        ]
    else:
        likely_cause = "The controller hit an unexpected error while running the requested cockpit action."
        next_steps = [
            "Open the failure record and the latest trial artifacts.",
            "Fix the reported error, then start a fresh optimization.",
        ]
    if failed_trials:
        first_reason = str(failed_trials[0].get("failure_reason") or "").strip()
        if first_reason:
            next_steps.insert(0, f"First failed trial says: {first_reason}")
    return {
        "action": action,
        "error": message,
        "error_type": error.__class__.__name__,
        "likely_cause": likely_cause,
        "next_steps": next_steps,
        "artifacts": artifacts,
        "failed_trials": failed_trials,
    }


def _failed_trial_context(results_path: Path) -> list[dict[str, Any]]:
    if not results_path.exists():
        return []
    try:
        rows = read_jsonl(results_path)
    except Exception:
        return []
    failed = []
    for row in rows:
        if row.get("status") != "failed" and not row.get("failure_reason"):
            continue
        failed.append(
            {
                "trial_id": row.get("trial_id"),
                "candidate_id": row.get("candidate_id"),
                "failure_reason": row.get("failure_reason") or "benchmark failure",
                "artifact_paths": row.get("artifact_paths", {}),
            }
        )
        if len(failed) >= 3:
            break
    return failed


def plain_summary(action: str, status: str, result: dict[str, Any] | None = None) -> dict[str, str]:
    result = result or {}
    if status == "running":
        elapsed = int(result.get("elapsed_seconds") or 0)
        if action == "run":
            return {
                "what_happened": f"Live optimization is running ({elapsed}s elapsed).",
                "what_it_means": "The cockpit is executing the automatic pipeline and may be using the GX10 for live trials.",
                "next_step": "Keep this page open to watch progress, or request cancel if you need to stop.",
            }
        return {
            "what_happened": f"I am working on {action} ({elapsed}s elapsed).",
            "what_it_means": "The cockpit asked the local controller to do one job.",
            "next_step": "Watch the progress bar.",
        }
    if status == "cancel-requested":
        return {
            "what_happened": "Stop requested.",
            "what_it_means": "The controller will stop if the job is still between safe steps. Remote work may need a moment to finish its current step.",
            "next_step": "Wait for the job status to settle before starting another run.",
        }
    if status == "failed":
        diagnostics = result.get("diagnostics")
        if isinstance(diagnostics, dict):
            next_steps = diagnostics.get("next_steps")
            next_step = (
                str(next_steps[0])
                if isinstance(next_steps, list) and next_steps
                else "Open the failure detail, fix the cause, then start a fresh optimization."
            )
            return {
                "what_happened": f"{action.title()} failed.",
                "what_it_means": str(diagnostics.get("likely_cause") or result.get("error") or "The controller reported an error."),
                "next_step": next_step,
            }
        return {
            "what_happened": f"{action.title()} did not finish.",
            "what_it_means": str(result.get("error") or "The controller reported an error."),
            "next_step": "Read the error, fix the input, then try again.",
        }
    if action == "plan":
        plan_path = str(result.get("artifacts", {}).get("sweep_plan") or result.get("artifacts", {}).get("pipeline_plan") or "the plan file")
        return {
            "what_happened": "I made the plan.",
            "what_it_means": f"This is the blueprint. It lists what we would test and where files go: {plan_path}.",
            "next_step": "Click Preview to check if it is safe.",
        }
    if action == "preview":
        blocked = bool(result.get("blocked"))
        return {
            "what_happened": "I checked the plan.",
            "what_it_means": "It is blocked by a safety gate." if blocked else "It looks safe to run from the current rules.",
            "next_step": "Read the blocked reason before running." if blocked else "Click Run when you are ready.",
        }
    if action == "run":
        return {
            "what_happened": "The run finished.",
            "what_it_means": "The controller completed the remote-capable run request and wrote artifacts.",
            "next_step": "Click Generate & Review Report to rank candidates and open the report.",
        }
    if action == "report":
        return {
            "what_happened": "The report is ready.",
            "what_it_means": "The cockpit generated local report artifacts from the completed run.",
            "next_step": "Review the report, then confirm the candidate if it looks good.",
        }
    if action == "promote":
        candidate = str(result.get("candidate_id") or "the selected candidate")
        return {
            "what_happened": f"Promotion profile written for {candidate}.",
            "what_it_means": "The cockpit wrote a local profile artifact under the output directory using the explicit promotion gate.",
            "next_step": "Review the promoted profile and summary before making it your default configuration.",
        }
    return {
        "what_happened": f"{action.title()} finished.",
        "what_it_means": "The controller wrote the requested artifacts.",
        "next_step": "Continue to the next cockpit step.",
    }


def serve_cockpit(config: CockpitServerConfig, host: str, port: int) -> None:
    handler_class = build_handler(config)
    server = ThreadingHTTPServer((host, port), handler_class)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def build_handler(
    config: CockpitServerConfig,
    *,
    job_store: CockpitJobStore | None = None,
) -> type[BaseHTTPRequestHandler]:
    jobs = job_store or CockpitJobStore()

    class CockpitRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            if self.path in {"/", "/index.html"}:
                self._send_html(render_active_cockpit(config))
                return
            if self.path == "/api/health":
                self._send_json({"status": "ok"})
                return
            if self.path == "/api/jobs/recent":
                try:
                    self._send_json(jobs.recent(config))
                except CockpitServerError as exc:
                    self._send_json({"status": "error", "error": str(exc)}, HTTPStatus.NOT_FOUND)
                return
            job_prefix = "/api/jobs/"
            if self.path.startswith(job_prefix):
                job_id = self.path.removeprefix(job_prefix)
                try:
                    self._send_json(jobs.get(job_id))
                except CockpitServerError as exc:
                    self._send_json({"status": "error", "error": str(exc)}, HTTPStatus.NOT_FOUND)
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
            prefix = "/api/controller/"
            if not self.path.startswith(prefix):
                if self.path.startswith("/api/jobs/") and self.path.endswith("/cancel"):
                    job_id = self.path.removeprefix("/api/jobs/").removesuffix("/cancel")
                    try:
                        self._send_json(jobs.cancel(job_id, config))
                    except CockpitServerError as exc:
                        self._send_json({"status": "error", "error": str(exc)}, HTTPStatus.NOT_FOUND)
                    return
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            action = self.path.removeprefix(prefix)
            try:
                payload = self._read_payload()
                result = jobs.start(action, payload, config)
            except (CockpitServerError, ValueError) as exc:
                self._send_json({"status": "error", "error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(result)

        def log_message(self, _format: str, *args: Any) -> None:
            return

        def _read_payload(self) -> dict[str, Any]:
            length = int(self.headers.get("content-length", "0") or "0")
            if length == 0:
                return {}
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise CockpitServerError("request payload must be a JSON object")
            return data

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, data: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return CockpitRequestHandler


def render_active_cockpit(config: CockpitServerConfig) -> str:
    catalog = _read_json_or_empty(config.catalog_path, {"groups": []})
    manifest = _read_optional_json(config.manifest_path)
    implicit_artifacts_match = _implicit_artifacts_match_config(config)
    status = _read_optional_json(config.status_path)
    if config.status_path is None and not implicit_artifacts_match:
        status = None
    report = _read_optional_json(config.report_path)
    if report is None and implicit_artifacts_match:
        report = _read_optional_json(config.out_dir / "report.json")
    run_index = _read_optional_json(config.run_index_path)
    profiles = read_profile_summaries(config.profile_paths)
    return render_web_cockpit(
        catalog,
        manifest=manifest,
        status=status,
        report=report,
        run_index=run_index,
        profiles=profiles,
        promotion_allowed=config.allow_promotion,
        sources={
            "catalog": _source(config.catalog_path),
            "manifest": _source(config.manifest_path),
            "status": _source(config.status_path),
            "report": _source(config.report_path),
            "run_index": _source(config.run_index_path),
            "profiles": ", ".join(path.as_posix() for path in config.profile_paths) or None,
            "server": "active localhost controller",
        },
    )


def _read_json_or_empty(path: Path | None, fallback: dict[str, Any]) -> dict[str, Any]:
    if path is None or not path.exists():
        return fallback
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise CockpitServerError(f"expected JSON object in {path}")
    return data


def _read_optional_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return _read_json_or_empty(path, {})


def _implicit_artifacts_match_config(config: CockpitServerConfig) -> bool:
    expected_sweep_id = _configured_sweep_id(config.sweep_path)
    if expected_sweep_id is None:
        return True
    sweep_plan = _read_optional_json(config.out_dir / "sweep-plan.json")
    if sweep_plan is not None and sweep_plan.get("sweep_id") != expected_sweep_id:
        return False
    report = _read_optional_json(config.out_dir / "report.json")
    if report is not None and not _report_matches_sweep(report, expected_sweep_id):
        return False
    return True


def _configured_sweep_id(sweep_path: Path) -> str | None:
    try:
        return load_sweep_definition(sweep_path).sweep_id
    except Exception:
        return None


def _report_matches_sweep(report: dict[str, Any], expected_sweep_id: str) -> bool:
    candidates = report.get("candidates")
    candidate_ids: list[str] = []
    if isinstance(candidates, dict):
        candidate_ids = [str(candidate_id) for candidate_id in candidates if isinstance(candidate_id, str)]
    elif isinstance(candidates, list):
        candidate_ids = [
            str(candidate.get("candidate_id"))
            for candidate in candidates
            if isinstance(candidate, dict) and isinstance(candidate.get("candidate_id"), str)
        ]
    if not candidate_ids:
        return True
    return all(candidate_id.startswith(f"{expected_sweep_id}-") for candidate_id in candidate_ids)


def _source(path: Path | None) -> str | None:
    return path.as_posix() if path is not None else None
