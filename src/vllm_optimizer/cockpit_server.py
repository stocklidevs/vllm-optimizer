from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .artifacts import write_json
from .cockpit_controller import CockpitPreviewRequest, CockpitRunRequest, run_cockpit_live, run_cockpit_preview
from .optimizer_pipeline import OptimizerPipelineRequest, run_optimizer_pipeline
from .web_cockpit import render_web_cockpit


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
    allow_risky_session_flags: bool = False
    timeout_seconds: int = 1200
    continue_on_failure: bool = False


def handle_controller_action(
    action: str,
    payload: dict[str, Any],
    config: CockpitServerConfig,
) -> dict[str, Any]:
    if action == "plan":
        summary = run_optimizer_pipeline(
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
    raise CockpitServerError(f"unsupported controller action: {action}")


def serve_cockpit(config: CockpitServerConfig, host: str, port: int) -> None:
    handler_class = build_handler(config)
    server = ThreadingHTTPServer((host, port), handler_class)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def build_handler(config: CockpitServerConfig) -> type[BaseHTTPRequestHandler]:
    class CockpitRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            if self.path in {"/", "/index.html"}:
                self._send_html(render_active_cockpit(config))
                return
            if self.path == "/api/health":
                self._send_json({"status": "ok"})
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
            prefix = "/api/controller/"
            if not self.path.startswith(prefix):
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            action = self.path.removeprefix(prefix)
            try:
                payload = self._read_payload()
                result = handle_controller_action(action, payload, config)
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
    report = _read_optional_json(config.report_path)
    run_index = _read_optional_json(config.run_index_path)
    return render_web_cockpit(
        catalog,
        manifest=manifest,
        status=status,
        report=report,
        run_index=run_index,
        sources={
            "catalog": _source(config.catalog_path),
            "manifest": _source(config.manifest_path),
            "status": _source(config.status_path),
            "report": _source(config.report_path),
            "run_index": _source(config.run_index_path),
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
