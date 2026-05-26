from pathlib import Path

from vllm_optimizer.artifacts import read_json
from vllm_optimizer.cli import main


def test_cli_smoke_serve_plan_writes_plan(tmp_path: Path) -> None:
    out = tmp_path / "smoke-plan.json"

    code = main(
        [
            "smoke-serve-plan",
            "--profile",
            "config/profiles/qwen3-coder-next-awq.json",
            "--out",
            str(out),
        ]
    )

    assert code == 0
    plan = read_json(out)
    assert plan["mode"] == "dry-run"
    assert plan["readiness"]["url"] == "http://127.0.0.1:8001/v1/models"


def test_cli_model_catalog_writes_summary(tmp_path: Path) -> None:
    out = tmp_path / "model-catalog.json"

    code = main(["model-catalog", "--catalog", "config/model-catalog.json", "--out", str(out)])

    assert code == 0
    catalog = read_json(out)
    assert catalog["model_count"] >= 6
    assert catalog["models"][1]["model_id"] == "gemma-4-e4b-it"


def test_cli_model_smoke_plan_writes_model_aware_plan(tmp_path: Path) -> None:
    out = tmp_path / "gemma-smoke-plan.json"

    code = main(
        [
            "model-smoke-plan",
            "--catalog",
            "config/model-catalog.json",
            "--model",
            "gemma-4-e4b-it",
            "--out",
            str(out),
        ]
    )

    assert code == 0
    plan = read_json(out)
    assert plan["model_id"] == "gemma-4-e4b-it"
    assert plan["serve_plan"]["serve_command"][2] == "google/gemma-4-E4B-it"
    assert "tool" in plan["readiness_categories"]
