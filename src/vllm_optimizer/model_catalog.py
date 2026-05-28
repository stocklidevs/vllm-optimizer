from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .artifacts import read_json, write_json
from .discovery import DiscoveryTarget
from .serve_profiles import load_serve_profile
from .smoke import build_smoke_serve_plan, run_smoke_serve


class ModelCatalogError(ValueError):
    """Raised when a model catalog entry is invalid."""


@dataclass(frozen=True)
class ModelCandidate:
    model_id: str
    display_name: str
    runtime: str
    source_model: str
    served_model_name: str
    profile_path: Path
    support_status: str
    tool_support: str
    baseline_notes: str
    source_urls: tuple[str, ...]
    default_objectives: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class ModelCatalog:
    schema_version: str
    generated_at: str
    models: tuple[ModelCandidate, ...]


def load_model_catalog(path: Path) -> ModelCatalog:
    return parse_model_catalog(read_json(path))


def parse_model_catalog(data: dict[str, Any]) -> ModelCatalog:
    errors: list[str] = []
    schema_version = _required_str(data, "schema_version", errors)
    generated_at = _required_str(data, "generated_at", errors)
    models_raw = data.get("models")
    if not isinstance(models_raw, list) or not models_raw:
        errors.append("models must be a non-empty array")
        models_raw = []
    models: list[ModelCandidate] = []
    seen: set[str] = set()
    for index, item in enumerate(models_raw):
        if not isinstance(item, dict):
            errors.append(f"models[{index}] must be an object")
            continue
        candidate = _parse_model_candidate(index, item, errors)
        if candidate.model_id in seen:
            errors.append(f"duplicate model_id {candidate.model_id!r}")
            continue
        seen.add(candidate.model_id)
        models.append(candidate)
    if errors:
        raise ModelCatalogError("; ".join(errors))
    return ModelCatalog(schema_version=schema_version, generated_at=generated_at, models=tuple(models))


def write_model_catalog_summary(catalog_path: Path, out_path: Path | None = None) -> dict[str, Any]:
    catalog = load_model_catalog(catalog_path)
    summary = catalog_to_dict(catalog)
    if out_path is not None:
        write_json(out_path, summary)
    return summary


def catalog_to_dict(catalog: ModelCatalog) -> dict[str, Any]:
    models = [model_to_dict(model) for model in catalog.models]
    return {
        "schema_version": catalog.schema_version,
        "generated_at": catalog.generated_at,
        "model_count": len(models),
        "models": models,
    }


def model_to_dict(model: ModelCandidate) -> dict[str, Any]:
    return {
        "model_id": model.model_id,
        "display_name": model.display_name,
        "runtime": model.runtime,
        "source_model": model.source_model,
        "served_model_name": model.served_model_name,
        "profile_path": model.profile_path.as_posix(),
        "support_status": model.support_status,
        "tool_support": model.tool_support,
        "baseline_notes": model.baseline_notes,
        "source_urls": list(model.source_urls),
        "default_objectives": list(model.default_objectives),
        "warnings": list(model.warnings),
    }


def select_model_candidate(catalog: ModelCatalog, model_id: str) -> ModelCandidate:
    for model in catalog.models:
        if model.model_id == model_id:
            return model
    available = ", ".join(model.model_id for model in catalog.models)
    raise ModelCatalogError(f"unknown model_id {model_id!r}; available models: {available}")


def build_model_smoke_plan(candidate: ModelCandidate) -> dict[str, Any]:
    profile = load_serve_profile(candidate.profile_path)
    serve_plan = build_smoke_serve_plan(profile, tool_probe_required=candidate.tool_support == "supported")
    return {
        "model_id": candidate.model_id,
        "display_name": candidate.display_name,
        "runtime": candidate.runtime,
        "source_model": candidate.source_model,
        "served_model_name": candidate.served_model_name,
        "profile_path": candidate.profile_path.as_posix(),
        "support_status": candidate.support_status,
        "tool_support": candidate.tool_support,
        "baseline_notes": candidate.baseline_notes,
        "readiness_categories": serve_plan["readiness_categories"],
        "serve_plan": serve_plan,
        "will_execute": False,
        "classification": serve_plan["classification"],
    }


def write_model_smoke_plan(catalog_path: Path, model_id: str, out_path: Path) -> dict[str, Any]:
    catalog = load_model_catalog(catalog_path)
    candidate = select_model_candidate(catalog, model_id)
    plan = build_model_smoke_plan(candidate)
    write_json(out_path, plan)
    return {"plan_path": out_path.as_posix(), "model_id": model_id}


def run_model_smoke(
    target: DiscoveryTarget,
    catalog_path: Path,
    model_id: str,
    out_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    catalog = load_model_catalog(catalog_path)
    candidate = select_model_candidate(catalog, model_id)
    profile = load_serve_profile(candidate.profile_path)
    result = run_smoke_serve(
        target,
        profile,
        out_dir,
        timeout_seconds,
        model_context=model_to_dict(candidate),
        tool_probe_required=candidate.tool_support == "supported",
    )
    write_json(out_dir / "model-smoke-plan.json", build_model_smoke_plan(candidate))
    return result


def _parse_model_candidate(index: int, data: dict[str, Any], errors: list[str]) -> ModelCandidate:
    model_id = _required_str(data, "model_id", errors, index)
    display_name = _required_str(data, "display_name", errors, index)
    runtime = _required_str(data, "runtime", errors, index)
    if runtime != "local-vllm":
        errors.append(f"models[{index}].runtime must be local-vllm")
    source_model = _required_str(data, "source_model", errors, index)
    served_model_name = _required_str(data, "served_model_name", errors, index)
    profile_path = Path(_required_str(data, "profile_path", errors, index))
    support_status = _required_str(data, "support_status", errors, index)
    if support_status not in {"measured", "recipe-captured", "candidate", "optional"}:
        errors.append(f"models[{index}].support_status is unsupported")
    tool_support = _required_str(data, "tool_support", errors, index)
    if tool_support not in {"supported", "plain-chat-first", "unknown"}:
        errors.append(f"models[{index}].tool_support is unsupported")
    baseline_notes = _required_str(data, "baseline_notes", errors, index)
    source_urls = _string_tuple(data.get("source_urls"), f"models[{index}].source_urls", errors)
    default_objectives = _string_tuple(
        data.get("default_objectives", ["single_user", "balanced", "throughput"]),
        f"models[{index}].default_objectives",
        errors,
    )
    warnings = _string_tuple(data.get("warnings", []), f"models[{index}].warnings", errors)
    return ModelCandidate(
        model_id=model_id,
        display_name=display_name,
        runtime=runtime,
        source_model=source_model,
        served_model_name=served_model_name,
        profile_path=profile_path,
        support_status=support_status,
        tool_support=tool_support,
        baseline_notes=baseline_notes,
        source_urls=source_urls,
        default_objectives=default_objectives,
        warnings=warnings,
    )


def _required_str(data: dict[str, Any], field: str, errors: list[str], index: int | None = None) -> str:
    value = data.get(field)
    if isinstance(value, str) and value:
        return value
    prefix = f"models[{index}]." if index is not None else ""
    errors.append(f"{prefix}{field} is required")
    return ""


def _string_tuple(value: Any, field: str, errors: list[str]) -> tuple[str, ...]:
    if not isinstance(value, list):
        errors.append(f"{field} must be an array")
        return ()
    parsed = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            errors.append(f"{field}[{index}] must be a non-empty string")
            continue
        parsed.append(item)
    return tuple(parsed)
