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

from .artifacts import write_json
from .cockpit_controller import CockpitPreviewRequest, CockpitRunRequest, run_cockpit_live, run_cockpit_preview
from .optimizer_pipeline import OptimizerPipelineRequest, run_optimizer_pipeline
from .promotion import write_promoted_profile
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

    def wait(self, job_id: str, timeout_seconds: float) -> dict[str, Any]:
        deadline = monotonic() + timeout_seconds
        while monotonic() < deadline:
            job = self.get(job_id)
            if job["status"] in {"completed", "failed", "cancelled"}:
                return job
            threading.Event().wait(0.01)
        return self.get(job_id)

    def cancel(self, job_id: str) -> dict[str, Any]:
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
            return dict(job)

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
                    return
                job["status"] = "completed"
                job["progress_percent"] = 100
                job["result"] = result
                job["plain_summary"] = plain_summary(action, "completed", result)
        except Exception as exc:  # pragma: no cover - defensive job boundary
            with self._lock:
                job = self._jobs[job_id]
                job["status"] = "failed"
                job["progress_percent"] = 100
                job["error"] = str(exc)
                job["plain_summary"] = plain_summary(action, "failed", {"error": str(exc)})


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
                        self._send_json(jobs.cancel(job_id))
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
    status = _read_optional_json(config.status_path)
    report = _read_optional_json(config.report_path) or _read_optional_json(config.out_dir / "report.json")
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


def _source(path: Path | None) -> str | None:
    return path.as_posix() if path is not None else None
