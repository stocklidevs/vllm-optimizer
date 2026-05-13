from pathlib import Path
import tomllib

from vllm_optimizer import __version__
from vllm_optimizer.cli import main


def test_package_version_matches_project_metadata() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert __version__ == pyproject["project"]["version"]


def test_cli_version(capsys) -> None:
    try:
        main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0

    assert __version__ in capsys.readouterr().out
