import pytest

from vllm_optimizer.cli import main


def test_cli_cockpit_server_help_is_available() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["cockpit-server", "--help"])
    assert exc.value.code == 0
