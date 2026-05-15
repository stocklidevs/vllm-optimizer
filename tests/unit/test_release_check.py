from pathlib import Path

from vllm_optimizer.release_check import build_release_check, render_release_check_markdown


def test_release_check_passes_for_current_repository() -> None:
    report = build_release_check(Path("."))

    assert report["schema_version"] == "1.0"
    assert report["overall_status"] == "pass"
    checks = {check["id"]: check for check in report["checks"]}
    assert checks["version-metadata"]["status"] == "pass"
    assert checks["readme-version-badge"]["status"] == "pass"
    assert checks["active-speckit-feature"]["status"] == "pass"
    assert checks["artifact-contracts-command"]["status"] == "pass"


def test_release_check_markdown_summarizes_checks() -> None:
    report = build_release_check(Path("."))
    markdown = render_release_check_markdown(report)

    assert markdown.startswith("# vLLM Optimizer Release Check")
    assert "- Overall status: `pass`" in markdown
    assert "version-metadata" in markdown

