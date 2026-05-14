from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .artifacts import read_json, write_json


class SessionTuningError(ValueError):
    """Raised when session tuning input is unsafe or invalid."""


@dataclass(frozen=True)
class SessionTuningProfile:
    profile_id: str
    classification: str
    environment: dict[str, str]
    ulimits: dict[str, int]
    description: str = ""


APPROVED_ENV_PREFIXES = ("VLLM_", "CUDA_", "NCCL_", "TORCH_")
APPROVED_ULIMITS = {"nofile"}


def load_session_tuning_profile(path: Path) -> SessionTuningProfile:
    data = read_json(path)
    errors: list[str] = []
    profile_id = data.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id:
        errors.append("profile_id is required")
        profile_id = ""
    classification = data.get("classification")
    if classification != "session-mutating":
        errors.append("classification must be session-mutating")
        classification = ""
    description = data.get("description", "")
    if not isinstance(description, str):
        errors.append("description must be a string")
        description = ""
    environment = parse_environment(data.get("environment", {}), errors)
    ulimits = parse_ulimits(data.get("ulimits", {}), errors)
    if errors:
        raise SessionTuningError("; ".join(errors))
    return SessionTuningProfile(
        profile_id=profile_id,
        classification=classification,
        description=description,
        environment=environment,
        ulimits=ulimits,
    )


def parse_environment(value: Any, errors: list[str]) -> dict[str, str]:
    if not isinstance(value, dict):
        errors.append("environment must be an object")
        return {}
    parsed = {}
    for key, item in sorted(value.items()):
        if not isinstance(key, str) or not key:
            errors.append("environment keys must be non-empty strings")
            continue
        if not key.startswith(APPROVED_ENV_PREFIXES):
            errors.append(f"environment.{key} is not an approved session env var")
            continue
        if not isinstance(item, str):
            errors.append(f"environment.{key} must be a string")
            continue
        parsed[key] = item
    return parsed


def parse_ulimits(value: Any, errors: list[str]) -> dict[str, int]:
    if not isinstance(value, dict):
        errors.append("ulimits must be an object")
        return {}
    parsed = {}
    for key, item in sorted(value.items()):
        if key not in APPROVED_ULIMITS:
            errors.append(f"ulimits.{key} is not approved")
            continue
        if not isinstance(item, int) or isinstance(item, bool) or item < 1:
            errors.append(f"ulimits.{key} must be a positive integer")
            continue
        parsed[key] = item
    return parsed


def build_session_tuning_preview(
    profile: SessionTuningProfile,
    catalog_path: Path | None = None,
) -> dict[str, Any]:
    catalog = read_json(catalog_path) if catalog_path is not None and catalog_path.exists() else {}
    validate_against_catalog(profile, catalog)
    actions = []
    for key, value in sorted(profile.environment.items()):
        actions.append(
            {
                "kind": "environment",
                "name": key,
                "value": value,
                "classification": "session-mutating",
                "command": f"export {key}={shlex.quote(value)}",
            }
        )
    for key, value in sorted(profile.ulimits.items()):
        if key == "nofile":
            actions.append(
                {
                    "kind": "ulimit",
                    "name": key,
                    "value": value,
                    "classification": "session-mutating",
                    "command": f"ulimit -n {value}",
                }
            )
    preview = {
        "profile_id": profile.profile_id,
        "classification": profile.classification,
        "will_execute": False,
        "catalog_path": catalog_path.as_posix() if catalog_path else None,
        "actions": actions,
    }
    preview["prelude"] = render_session_tuning_prelude(preview)
    return preview


def validate_against_catalog(profile: SessionTuningProfile, catalog: dict[str, Any]) -> None:
    entries = catalog.get("entries", {}) if isinstance(catalog, dict) else {}
    if profile.environment:
        ensure_catalog_allows(entries, "vllm.env")
    if profile.ulimits:
        ensure_catalog_allows(entries, "kernel.open_file_limit")


def ensure_catalog_allows(entries: dict[str, Any], key: str) -> None:
    if not entries:
        return
    entry = entries.get(key)
    if not isinstance(entry, dict):
        raise SessionTuningError(f"catalog entry {key!r} is missing")
    if entry.get("future_action_classification") != "session-mutating":
        raise SessionTuningError(f"catalog entry {key!r} is not session-mutating")


def render_session_tuning_prelude(preview: dict[str, Any]) -> str:
    commands = [str(action["command"]) for action in preview.get("actions", [])]
    if not commands:
        return ""
    return "\n".join(["# session tuning prelude", *commands])


def write_session_tuning_preview(profile_path: Path, catalog_path: Path | None, out_path: Path) -> dict[str, Any]:
    preview = build_session_tuning_preview(load_session_tuning_profile(profile_path), catalog_path)
    write_json(out_path, preview)
    return preview
