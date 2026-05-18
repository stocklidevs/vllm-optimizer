from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .cockpit_server import CockpitServerConfig, serve_cockpit
from .knob_catalog import write_knob_catalog
from .pipeline_control import write_pipeline_control_manifest
from .run_browser import write_run_index


class CockpitLaunchError(ValueError):
    """Raised when the one-command cockpit launcher cannot prepare artifacts."""


@dataclass(frozen=True)
class CockpitLaunchRequest:
    sweep_path: Path = Path("config/sweeps/qwen-small-sweep.json")
    config_path: Path | None = None
    config_root: Path = Path("config")
    artifacts_root: Path = Path("artifacts")
    out_dir: Path = Path("artifacts/controller/cockpit-active")
    catalog_path: Path = Path("artifacts/catalog/knob-groups.json")
    manifest_path: Path | None = None
    run_index_path: Path = Path("artifacts/catalog/run-index.json")
    host: str = "127.0.0.1"
    port: int = 8787
    allow_risky_session_flags: bool = False
    timeout_seconds: int = 1200
    continue_on_failure: bool = False


ServerRunner = Callable[[CockpitServerConfig, str, int], None]


def launch_cockpit(
    request: CockpitLaunchRequest,
    *,
    server_runner: ServerRunner = serve_cockpit,
) -> dict[str, Any]:
    prepared = prepare_cockpit_launch(request)
    server_runner(prepared["server_config"], request.host, request.port)
    return prepared


def prepare_cockpit_launch(request: CockpitLaunchRequest) -> dict[str, Any]:
    sweep_path = request.sweep_path
    if not sweep_path.exists():
        raise CockpitLaunchError(f"sweep path does not exist: {sweep_path}")
    config_path = request.config_path or default_config_path()
    group_id = sweep_path.stem
    manifest_path = request.manifest_path or Path("artifacts/catalog") / f"{group_id}-control.json"

    request.artifacts_root.mkdir(parents=True, exist_ok=True)
    request.out_dir.mkdir(parents=True, exist_ok=True)
    write_knob_catalog(request.config_root, request.catalog_path)
    write_pipeline_control_manifest(request.catalog_path, group_id, manifest_path)
    write_run_index(request.artifacts_root, request.run_index_path)

    server_config = CockpitServerConfig(
        sweep_path=sweep_path,
        config_path=config_path,
        out_dir=request.out_dir,
        catalog_path=request.catalog_path,
        manifest_path=manifest_path,
        run_index_path=request.run_index_path,
        allow_risky_session_flags=request.allow_risky_session_flags,
        timeout_seconds=request.timeout_seconds,
        continue_on_failure=request.continue_on_failure,
    )
    return {
        "url": f"http://{request.host}:{request.port}",
        "host": request.host,
        "port": request.port,
        "group_id": group_id,
        "sweep_path": sweep_path.as_posix(),
        "config_path": config_path.as_posix() if config_path else None,
        "out_dir": request.out_dir.as_posix(),
        "catalog_path": request.catalog_path.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "run_index_path": request.run_index_path.as_posix(),
        "server_config": server_config,
    }


def default_config_path() -> Path:
    local = Path("config/local.gx10.json")
    if local.exists():
        return local
    return Path("config/gx10.example.json")
