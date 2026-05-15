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


def test_changelog_contains_current_version_release_notes() -> None:
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")

    assert f"## {__version__} - 2026-05-15" in changelog
    assert "artifact-contracts" in changelog
    assert "release-check" in changelog
