from pathlib import Path

import pytest

from vllm_optimizer.model_catalog import (
    ModelCatalogError,
    build_model_smoke_plan,
    load_model_catalog,
    select_model_candidate,
)


def test_load_model_catalog_lists_local_candidates() -> None:
    catalog = load_model_catalog(Path("config/model-catalog.json"))

    model_ids = [model.model_id for model in catalog.models]

    assert model_ids[:2] == ["qwen3-coder-next-awq", "gemma-4-e4b-it"]
    assert "glm-4-7-flash" in model_ids
    assert "qwen3-6-27b" in model_ids
    assert "qwen3-5-27b" in model_ids
    assert "deepseek-coder-v2-lite-instruct" in model_ids
    assert {model.runtime for model in catalog.models} == {"local-vllm"}


def test_select_model_candidate_requires_known_model() -> None:
    catalog = load_model_catalog(Path("config/model-catalog.json"))

    with pytest.raises(ModelCatalogError, match="unknown model_id"):
        select_model_candidate(catalog, "not-here")


def test_build_model_smoke_plan_includes_model_readiness_metadata() -> None:
    catalog = load_model_catalog(Path("config/model-catalog.json"))
    candidate = select_model_candidate(catalog, "gemma-4-e4b-it")

    plan = build_model_smoke_plan(candidate)

    assert plan["model_id"] == "gemma-4-e4b-it"
    assert plan["display_name"] == "Gemma 4 E4B IT"
    assert plan["support_status"] == "recipe-captured"
    assert plan["tool_support"] == "supported"
    assert plan["profile_path"] == "config/profiles/gemma-4-e4b-it.json"
    assert "--chat-template" in plan["serve_plan"]["serve_command"]
    assert plan["readiness_categories"] == ["serve", "chat", "tool", "cleanup"]
