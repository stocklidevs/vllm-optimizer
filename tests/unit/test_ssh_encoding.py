import subprocess

from vllm_optimizer.ssh import SshExecutor


def test_ssh_executor_uses_utf8_replacement_decoding(monkeypatch) -> None:
    captured = {}

    def fake_run(command, **kwargs):
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    SshExecutor("user@example.invalid").run("probe", "hostname", 10)

    assert captured["kwargs"]["encoding"] == "utf-8"
    assert captured["kwargs"]["errors"] == "replace"
