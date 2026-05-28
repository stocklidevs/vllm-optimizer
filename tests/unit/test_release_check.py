from pathlib import Path

from vllm_optimizer.release_check import (
    build_release_check,
    check_active_speckit_completion_status,
    check_public_alpha_files,
    render_release_check_markdown,
)


def test_release_check_passes_for_current_repository() -> None:
    report = build_release_check(Path("."))

    assert report["schema_version"] == "1.0"
    assert report["overall_status"] == "pass"
    checks = {check["id"]: check for check in report["checks"]}
    assert checks["version-metadata"]["status"] == "pass"
    assert checks["readme-version-badge"]["status"] == "pass"
    assert checks["active-speckit-feature"]["status"] == "pass"
    assert checks["active-speckit-completion-status"]["status"] == "pass"
    assert checks["artifact-contracts-command"]["status"] == "pass"
    assert checks["public-alpha-files"]["status"] == "pass"


def test_release_check_markdown_summarizes_checks() -> None:
    report = build_release_check(Path("."))
    markdown = render_release_check_markdown(report)

    assert markdown.startswith("# vLLM Optimizer Release Check")
    assert "- Overall status: `pass`" in markdown
    assert "version-metadata" in markdown


def test_public_alpha_files_check_fails_when_required_docs_missing(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("README\n", encoding="utf-8")

    check = check_public_alpha_files(tmp_path)

    assert check.status == "fail"
    assert "public alpha files are missing" in check.message
    assert any(path.endswith("LICENSE") for path in check.paths)


def test_release_check_fails_when_completed_active_spec_still_looks_in_progress(tmp_path: Path) -> None:
    feature_dir = tmp_path / "specs/999-stale"
    feature_dir.mkdir(parents=True)
    specify_dir = tmp_path / ".specify"
    specify_dir.mkdir()
    (specify_dir / "feature.json").write_text(
        '{"feature_directory":"specs/999-stale"}',
        encoding="utf-8",
    )
    (feature_dir / "spec.md").write_text("**Status**: Implementing\n", encoding="utf-8")
    (feature_dir / "plan.md").write_text("**Status**: Completed\n", encoding="utf-8")
    (feature_dir / "tasks.md").write_text("- [x] Done\n", encoding="utf-8")

    check = check_active_speckit_completion_status(tmp_path)

    assert check.status == "fail"
    assert "Draft/Implementing" in check.message
