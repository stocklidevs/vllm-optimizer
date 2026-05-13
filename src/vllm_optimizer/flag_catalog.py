from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .artifacts import read_json, write_json
from .discovery import DiscoveryTarget
from .redaction import REDACTION, redact_data
from .serve_profiles import ServeProfile
from .ssh import Executor


class FlagCatalogError(ValueError):
    """Raised when vLLM flag catalog inputs are invalid."""


FLAG_PATTERN = re.compile(r"(?<![\w-])--([a-zA-Z0-9][a-zA-Z0-9-]*)")


def parse_serve_help(help_text: str) -> list[dict[str, Any]]:
    if not help_text.strip():
        raise FlagCatalogError("help text is empty")
    flags: dict[str, dict[str, Any]] = {}
    for line in help_text.splitlines():
        matches = FLAG_PATTERN.findall(line)
        for name in matches:
            flags.setdefault(name, {"name": name, "aliases": [], "source_line": line.strip()})
    if not flags:
        raise FlagCatalogError("no vLLM serve flags found in help text")
    return [flags[name] for name in sorted(flags)]


def load_policy(path: Path) -> dict[str, Any]:
    policy = read_json(path)
    policy_id = policy.get("policy_id")
    categories = policy.get("categories")
    if not isinstance(policy_id, str) or not policy_id:
        raise FlagCatalogError("policy_id is required")
    if not isinstance(categories, dict) or not categories:
        raise FlagCatalogError("categories must be a non-empty object")
    for category, entries in categories.items():
        if not isinstance(category, str) or not isinstance(entries, dict):
            raise FlagCatalogError("each category must map to an object of flags")
    return policy


def build_flag_catalog(
    policy: dict[str, Any],
    help_text: str,
    version_text: str = "",
    artifact_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    parsed_flags = parse_serve_help(help_text)
    available = {flag["name"] for flag in parsed_flags}
    categories: dict[str, list[dict[str, Any]]] = {}
    unavailable: list[dict[str, str]] = []
    classified_names: set[str] = set()
    for category, entries in policy["categories"].items():
        rows = []
        for flag_name, rationale in sorted(entries.items()):
            if flag_name in available:
                classified_names.add(flag_name)
                rows.append({"name": flag_name, "rationale": str(rationale), "available": True})
            else:
                unavailable.append(
                    {"name": flag_name, "category": category, "rationale": str(rationale)}
                )
        categories[category] = rows
    unclassified = sorted(available - classified_names)
    return {
        "policy_id": policy["policy_id"],
        "vllm_version": parse_version(version_text),
        "flag_count": len(parsed_flags),
        "parsed_flags": parsed_flags,
        "categories": categories,
        "unavailable_policy_flags": unavailable,
        "unclassified_flags": unclassified,
        "artifact_paths": artifact_paths or {},
    }


def generate_catalog_from_files(
    policy_path: Path, help_path: Path, out_path: Path, version_path: Path | None = None
) -> dict[str, Any]:
    policy = load_policy(policy_path)
    help_text = help_path.read_text(encoding="utf-8")
    version_text = version_path.read_text(encoding="utf-8") if version_path else ""
    catalog = build_flag_catalog(policy, help_text, version_text, {"help": str(help_path)})
    write_json(out_path, catalog)
    return catalog


def capture_flag_catalog(
    target: DiscoveryTarget,
    profile: ServeProfile,
    policy_path: Path,
    executor: Executor,
    out_dir: Path,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    timeout = timeout_seconds or target.timeout_seconds
    version_command = f"{profile.vllm_executable} --version"
    help_command = f"{profile.vllm_executable} serve --help=all"
    version_result = executor.run("vllm-version", version_command, timeout)
    help_result = executor.run("vllm-serve-help", help_command, timeout)
    if version_result.exit_code != 0 or help_result.exit_code != 0:
        raise FlagCatalogError(
            f"flag capture failed: version exit={version_result.exit_code}, help exit={help_result.exit_code}"
        )
    policy = load_policy(policy_path)
    paths = {
        "version": out_dir / "version.txt",
        "serve_help": out_dir / "serve-help.txt",
        "catalog": out_dir / "catalog.json",
        "redaction": out_dir / "redaction-report.json",
    }
    catalog = build_flag_catalog(
        policy,
        help_result.stdout,
        version_result.stdout,
        {key: str(path) for key, path in paths.items()},
    )
    secrets = list(target.redact_values)
    redacted_version, version_count = redact_data(version_result.stdout, secrets)
    redacted_help, help_count = redact_data(help_result.stdout, secrets)
    redacted_catalog, catalog_count = redact_data(catalog, secrets)
    paths["version"].parent.mkdir(parents=True, exist_ok=True)
    paths["version"].write_text(str(redacted_version), encoding="utf-8")
    paths["serve_help"].write_text(str(redacted_help), encoding="utf-8")
    write_json(paths["catalog"], redacted_catalog)
    redaction = {
        "replacement": REDACTION,
        "redacted_value_count": version_count + help_count + catalog_count,
        "artifact_paths": {key: str(path) for key, path in paths.items()},
        "commands": [
            {"probe_id": "vllm-version", "classification": "read-only"},
            {"probe_id": "vllm-serve-help", "classification": "read-only"},
        ],
    }
    write_json(paths["redaction"], redaction)
    return {"catalog": redacted_catalog, "artifact_paths": redaction["artifact_paths"], "redaction": redaction}


def parse_version(version_text: str) -> str | None:
    stripped = version_text.strip()
    if not stripped:
        return None
    for token in stripped.replace(",", " ").split():
        if token[0].isdigit():
            return token
    return stripped.splitlines()[0]
