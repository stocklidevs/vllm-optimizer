import subprocess

from vllm_optimizer.ssh import SshExecutor


def test_ssh_executor_uses_batch_mode_and_destination(monkeypatch) -> None:
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, stdout="gx10\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = SshExecutor("user@example.invalid").run("connectivity", "hostname", 10)

    assert result.exit_code == 0
    assert result.stdout == "gx10\n"
    assert captured["command"] == [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        "user@example.invalid",
        "hostname",
    ]
    assert captured["kwargs"]["timeout"] == 15
