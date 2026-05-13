from __future__ import annotations

from dataclasses import dataclass
import subprocess
import time
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int = 0
    timed_out: bool = False


class Executor(Protocol):
    def run(self, probe_id: str, command: str, timeout_seconds: int) -> CommandResult:
        """Run a command for a probe and return its result."""


class MockExecutor:
    def __init__(self, outputs: dict[str, dict[str, object]]) -> None:
        self.outputs = outputs

    def run(self, probe_id: str, command: str, timeout_seconds: int) -> CommandResult:
        del command, timeout_seconds
        output = self.outputs.get(probe_id)
        if output is None:
            return CommandResult(
                exit_code=127,
                stdout="",
                stderr=f"missing mock output for probe {probe_id}",
            )
        return CommandResult(
            exit_code=int(output.get("exit_code", 0)),
            stdout=str(output.get("stdout", "")),
            stderr=str(output.get("stderr", "")),
            duration_ms=int(output.get("duration_ms", 0)),
            timed_out=bool(output.get("timed_out", False)),
        )


class SshExecutor:
    def __init__(self, destination: str) -> None:
        self.destination = destination

    def run(self, probe_id: str, command: str, timeout_seconds: int) -> CommandResult:
        del probe_id
        started = time.monotonic()
        ssh_command = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={timeout_seconds}",
            self.destination,
            command,
        ]
        try:
            completed = subprocess.run(
                ssh_command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds + 5,
            )
            duration_ms = int((time.monotonic() - started) * 1000)
            return CommandResult(
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_ms=duration_ms,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            duration_ms = int((time.monotonic() - started) * 1000)
            return CommandResult(
                exit_code=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "ssh command timed out",
                duration_ms=duration_ms,
                timed_out=True,
            )
