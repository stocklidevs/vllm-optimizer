from pathlib import Path

from vllm_optimizer import __version__


def test_setup_guide_documents_safe_release_workflows() -> None:
    setup = Path("docs/SETUP.md").read_text(encoding="utf-8")

    assert "uv sync" in setup
    assert "uv run pytest" in setup
    assert "artifact-contracts" in setup
    assert "release-check" in setup
    assert "config/local.gx10.json" in setup
    assert "--allow-promotion" in setup


def test_readme_links_setup_guide() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "[Setup Guide](docs/SETUP.md)" in readme


def test_readme_links_public_alpha_docs() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "public alpha" in readme.lower()
    assert "[Optimization Results](docs/RESULTS.md)" in readme
    assert "[Public Release Checklist](docs/PUBLIC_RELEASE.md)" in readme
    assert "[Contributing](CONTRIBUTING.md)" in readme
    assert "[Security](SECURITY.md)" in readme
    assert "[License](LICENSE)" in readme


def test_public_results_explain_aggregate_throughput() -> None:
    results = Path("docs/RESULTS.md").read_text(encoding="utf-8")

    assert "aggregate throughput" in results
    assert "not per-user streaming speed" in results
    assert "98.415 / 8 = 12.302" in results
    for model_name in (
        "Qwen3 Coder Next",
        "Gemma 4 E4B IT",
        "GLM 4.7 Flash",
        "Qwen3.6 27B",
        "Qwen3.5 27B",
        "DeepSeek Coder V2 Lite Instruct",
    ):
        assert model_name in results


def test_changelog_contains_current_version_release_notes() -> None:
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")

    assert f"## {__version__} -" in changelog
    assert "artifact-contracts" in changelog
    assert "release-check" in changelog
