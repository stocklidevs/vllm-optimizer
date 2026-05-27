from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import json
import re
import tomllib

from . import __version__
from .artifact_contracts import build_artifact_contract_catalog
from .artifacts import write_json


SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class ReleaseCheck:
    id: str
    status: str
    severity: str
    message: str
    paths: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "paths": list(self.paths),
        }


def build_release_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    checks = [
        check_version_metadata(root),
        check_readme_version_badge(root),
        check_active_speckit_feature(root),
        check_active_speckit_completion_status(root),
        check_artifact_contracts_command(root),
        check_release_documentation(root),
        check_public_alpha_files(root),
        check_essential_files(root),
    ]
    status = "fail" if any(check.status == "fail" and check.severity == "error" for check in checks) else "pass"
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": __version__,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "overall_status": status,
        "checks": [check.as_dict() for check in checks],
    }


def write_release_check(root: Path, out_path: Path, markdown_out: Path | None = None) -> dict[str, str]:
    report = build_release_check(root)
    write_json(out_path, report)
    artifacts = {"report_path": out_path.as_posix()}
    if markdown_out is not None:
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(render_release_check_markdown(report), encoding="utf-8")
        artifacts["markdown_path"] = markdown_out.as_posix()
    return artifacts


def render_release_check_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# vLLM Optimizer Release Check",
        "",
        f"- Overall status: `{report['overall_status']}`",
        f"- Tool version: `{report['tool_version']}`",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        paths = ", ".join(f"`{path}`" for path in check.get("paths", [])) or "n/a"
        lines.append(
            f"- `{check['id']}`: `{check['status']}` ({check['severity']}) - {check['message']} Paths: {paths}"
        )
    lines.append("")
    return "\n".join(lines)


def check_version_metadata(root: Path) -> ReleaseCheck:
    pyproject_path = root / "pyproject.toml"
    try:
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        package_version = pyproject["project"]["version"]
    except (OSError, KeyError, tomllib.TOMLDecodeError) as exc:
        return ReleaseCheck("version-metadata", "fail", "error", f"could not read package version: {exc}", _paths(pyproject_path))
    if package_version != __version__:
        return ReleaseCheck(
            "version-metadata",
            "fail",
            "error",
            f"pyproject version {package_version} does not match package version {__version__}",
            _paths(pyproject_path, root / "src/vllm_optimizer/__init__.py"),
        )
    return ReleaseCheck("version-metadata", "pass", "error", f"package version is {__version__}", _paths(pyproject_path))


def check_readme_version_badge(root: Path) -> ReleaseCheck:
    readme_path = root / "README.md"
    try:
        readme = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        return ReleaseCheck("readme-version-badge", "fail", "error", f"could not read README: {exc}", _paths(readme_path))
    match = re.search(r"badge/version-([0-9]+\.[0-9]+\.[0-9]+)-blue\.svg", readme)
    if not match:
        return ReleaseCheck("readme-version-badge", "fail", "error", "README version badge is missing", _paths(readme_path))
    badge_version = match.group(1)
    if badge_version != __version__:
        return ReleaseCheck(
            "readme-version-badge",
            "fail",
            "error",
            f"README badge version {badge_version} does not match package version {__version__}",
            _paths(readme_path),
        )
    return ReleaseCheck("readme-version-badge", "pass", "error", f"README badge version is {badge_version}", _paths(readme_path))


def check_active_speckit_feature(root: Path) -> ReleaseCheck:
    feature_path = root / ".specify/feature.json"
    try:
        feature = json.loads(feature_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ReleaseCheck("active-speckit-feature", "fail", "error", f"could not read active feature: {exc}", _paths(feature_path))
    feature_dir = feature.get("feature_directory")
    if not isinstance(feature_dir, str) or not feature_dir:
        return ReleaseCheck("active-speckit-feature", "fail", "error", "active feature_directory is missing", _paths(feature_path))
    required = [root / feature_dir / name for name in ("spec.md", "plan.md", "tasks.md")]
    missing = [path for path in required if not path.exists()]
    if missing:
        return ReleaseCheck(
            "active-speckit-feature",
            "fail",
            "error",
            "active SpecKit feature is missing required files",
            _paths(feature_path, *missing),
        )
    return ReleaseCheck("active-speckit-feature", "pass", "error", f"active feature is {feature_dir}", _paths(feature_path, *required))


def check_active_speckit_completion_status(root: Path) -> ReleaseCheck:
    feature_path = root / ".specify/feature.json"
    try:
        feature = json.loads(feature_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ReleaseCheck(
            "active-speckit-completion-status",
            "fail",
            "error",
            f"could not read active feature: {exc}",
            _paths(feature_path),
        )
    feature_dir = feature.get("feature_directory")
    if not isinstance(feature_dir, str) or not feature_dir:
        return ReleaseCheck(
            "active-speckit-completion-status",
            "fail",
            "error",
            "active feature_directory is missing",
            _paths(feature_path),
        )
    spec_path = root / feature_dir / "spec.md"
    plan_path = root / feature_dir / "plan.md"
    tasks_path = root / feature_dir / "tasks.md"
    missing = [path for path in (spec_path, plan_path, tasks_path) if not path.exists()]
    if missing:
        return ReleaseCheck(
            "active-speckit-completion-status",
            "fail",
            "error",
            "active SpecKit completion files are missing",
            _paths(feature_path, *missing),
        )
    tasks = tasks_path.read_text(encoding="utf-8")
    has_incomplete_tasks = bool(re.search(r"(?m)^- \[ \]", tasks))
    if has_incomplete_tasks:
        return ReleaseCheck(
            "active-speckit-completion-status",
            "pass",
            "warning",
            "active SpecKit feature still has incomplete tasks",
            _paths(spec_path, plan_path, tasks_path),
        )
    stale_status_paths = [
        path
        for path in (spec_path, plan_path)
        if re.search(r"(?im)^\*\*Status\*\*:\s*(Draft|Implementing)\s*$", path.read_text(encoding="utf-8"))
    ]
    if stale_status_paths:
        return ReleaseCheck(
            "active-speckit-completion-status",
            "fail",
            "error",
            "completed active SpecKit feature still has Draft/Implementing status",
            _paths(*stale_status_paths, tasks_path),
        )
    return ReleaseCheck(
        "active-speckit-completion-status",
        "pass",
        "error",
        "completed active SpecKit feature status is up to date",
        _paths(spec_path, plan_path, tasks_path),
    )


def check_artifact_contracts_command(root: Path) -> ReleaseCheck:
    catalog = build_artifact_contract_catalog()
    contract_types = {contract.get("artifact_type") for contract in catalog.get("contracts", [])}
    expected = {"canonical-report", "execution-status", "knob-group-catalog", "pipeline-control-manifest"}
    missing = sorted(expected - contract_types)
    if missing:
        return ReleaseCheck("artifact-contracts-command", "fail", "error", f"missing artifact contracts: {', '.join(missing)}")
    return ReleaseCheck(
        "artifact-contracts-command",
        "pass",
        "error",
        f"artifact contract catalog exposes {len(contract_types)} contracts",
        _paths(root / "src/vllm_optimizer/artifact_contracts.py"),
    )


def check_release_documentation(root: Path) -> ReleaseCheck:
    readme_path = root / "README.md"
    try:
        readme = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        return ReleaseCheck("release-documentation", "fail", "error", f"could not read README: {exc}", _paths(readme_path))
    missing = [term for term in ("artifact-contracts", "release-check") if term not in readme]
    if missing:
        return ReleaseCheck("release-documentation", "fail", "error", f"README missing release workflow terms: {', '.join(missing)}", _paths(readme_path))
    return ReleaseCheck("release-documentation", "pass", "warning", "README documents release metadata workflows", _paths(readme_path))


def check_public_alpha_files(root: Path) -> ReleaseCheck:
    required = [
        root / "LICENSE",
        root / "CONTRIBUTING.md",
        root / "SECURITY.md",
        root / "docs/PUBLIC_RELEASE.md",
        root / "docs/RESULTS.md",
        root / "docs/SETUP.md",
        root / "docs/PROJECT_STATUS.md",
        root / "CHANGELOG.md",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        return ReleaseCheck("public-alpha-files", "fail", "error", "public alpha files are missing", _paths(*missing))
    return ReleaseCheck("public-alpha-files", "pass", "error", "public alpha files exist", _paths(*required))


def check_essential_files(root: Path) -> ReleaseCheck:
    required = [
        root / "README.md",
        root / "pyproject.toml",
        root / "uv.lock",
        root / "AGENTS.md",
        root / "specs/000-project-roadmap-autonomy/spec.md",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        return ReleaseCheck("essential-files", "fail", "error", "release-essential files are missing", _paths(*missing))
    return ReleaseCheck("essential-files", "pass", "error", "release-essential files exist", _paths(*required))


def _paths(*paths: Path) -> tuple[str, ...]:
    return tuple(path.as_posix() for path in paths)
