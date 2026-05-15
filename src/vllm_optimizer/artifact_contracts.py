from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .artifacts import write_json


CATALOG_SCHEMA_VERSION = "1.0"


def build_artifact_contract_catalog() -> dict[str, Any]:
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "tool_version": __version__,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "contracts": artifact_contracts(),
    }


def artifact_contracts() -> list[dict[str, Any]]:
    return [
        {
            "artifact_type": "canonical-report",
            "artifact_schema_version": "1.0",
            "producer_command": "canonical-report",
            "stability": "stable",
            "required_fields": [
                "schema_version",
                "generated_at",
                "source",
                "recommendation",
                "objectives",
                "candidates",
                "chart_datasets",
                "provenance",
            ],
            "optional_fields": ["markdown"],
            "consumers": ["report-viewer", "future web dashboard"],
            "notes": "Source of truth for recommendation, ranking, chart, and provenance views.",
        },
        {
            "artifact_type": "execution-status",
            "artifact_schema_version": "1.0",
            "producer_command": "execution-status",
            "stability": "stable",
            "required_fields": [
                "schema_version",
                "generated_at",
                "run_dir",
                "overall_status",
                "stages",
                "trial_counts",
                "artifacts",
            ],
            "optional_fields": ["failures", "latest_artifact_mtime"],
            "consumers": ["execution-status HTML", "future web execution dashboard"],
            "notes": "Local snapshot for pipeline progress and artifact availability.",
        },
        {
            "artifact_type": "knob-group-catalog",
            "artifact_schema_version": "1.0",
            "producer_command": "knob-groups",
            "stability": "stable",
            "required_fields": [
                "schema_version",
                "generated_at",
                "config_root",
                "groups",
                "summary",
            ],
            "optional_fields": ["html_path"],
            "consumers": ["pipeline-control", "future web knob selector"],
            "notes": "Selectable optimization families with risk tiers and command families.",
        },
        {
            "artifact_type": "pipeline-control-manifest",
            "artifact_schema_version": "1.0",
            "producer_command": "pipeline-control",
            "stability": "stable",
            "required_fields": [
                "schema_version",
                "generated_at",
                "group",
                "stages",
                "required_gates",
                "artifacts",
            ],
            "optional_fields": ["html_path"],
            "consumers": ["future web pipeline controller"],
            "notes": "Ordered local and remote stages for a selected knob group, including safety gates.",
        },
    ]


def write_artifact_contract_catalog(out_path: Path, markdown_out: Path | None = None) -> dict[str, str]:
    catalog = build_artifact_contract_catalog()
    write_json(out_path, catalog)
    artifacts = {"catalog_path": out_path.as_posix()}
    if markdown_out is not None:
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(render_contract_markdown(catalog), encoding="utf-8")
        artifacts["markdown_path"] = markdown_out.as_posix()
    return artifacts


def render_contract_markdown(catalog: dict[str, Any]) -> str:
    lines = [
        "# vLLM Optimizer Artifact Contracts",
        "",
        f"- Catalog schema: `{catalog['schema_version']}`",
        f"- Tool version: `{catalog['tool_version']}`",
        "",
    ]
    for contract in catalog["contracts"]:
        lines.extend(
            [
                f"## {contract['artifact_type']}",
                "",
                f"- Artifact schema: `{contract['artifact_schema_version']}`",
                f"- Producer: `{contract['producer_command']}`",
                f"- Stability: `{contract['stability']}`",
                f"- Required fields: {_format_list(contract['required_fields'])}",
                f"- Optional fields: {_format_list(contract['optional_fields'])}",
                f"- Consumers: {_format_list(contract['consumers'])}",
                f"- Notes: {contract['notes']}",
                "",
            ]
        )
    return "\n".join(lines)


def _format_list(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values)
