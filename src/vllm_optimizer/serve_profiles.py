from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .artifacts import read_json


class ServeProfileError(ValueError):
    """Raised when a vLLM serve profile is invalid."""


@dataclass(frozen=True)
class ServeProfile:
    profile_id: str
    vllm_executable: str
    model: str
    served_model_name: str
    host: str
    port: int
    max_model_len: int
    gpu_memory_utilization: float
    enable_auto_tool_choice: bool
    tool_call_parser: str
    optional_flags: dict[str, bool | int | float | str]
    performance_mode: str | None = None
    chat_template: str | None = None
    reasoning_parser: str | None = None
    trust_remote_code: bool = False


OPTIONAL_FLAG_RULES: dict[str, dict[str, Any]] = {
    "max_num_batched_tokens": {"cli": "max-num-batched-tokens", "type": int, "min": 1, "risk_tier": "safe-session"},
    "max_num_seqs": {"cli": "max-num-seqs", "type": int, "min": 1, "risk_tier": "safe-session"},
    "enable_chunked_prefill": {"cli": "enable-chunked-prefill", "type": bool, "risk_tier": "safe-session"},
    "enable_prefix_caching": {"cli": "enable-prefix-caching", "type": bool, "risk_tier": "safe-session"},
    "block_size": {"cli": "block-size", "type": int, "allowed": {8, 16, 32}, "risk_tier": "risky-session"},
    "kv_cache_dtype": {"cli": "kv-cache-dtype", "type": str, "allowed": {"auto", "fp8", "fp8_e5m2"}, "risk_tier": "risky-session"},
    "enforce_eager": {"cli": "enforce-eager", "type": bool, "risk_tier": "risky-session"},
}


def load_serve_profile(path: Path) -> ServeProfile:
    return parse_serve_profile(read_json(path))


def parse_serve_profile(data: dict[str, Any]) -> ServeProfile:
    errors: list[str] = []
    profile_id = _required_str(data, "profile_id", errors)
    vllm_executable = data.get("vllm_executable", "vllm")
    if not isinstance(vllm_executable, str) or not vllm_executable:
        errors.append("vllm_executable must be a non-empty string")
        vllm_executable = "vllm"
    model = _required_str(data, "model", errors)
    served_model_name = _required_str(data, "served_model_name", errors)
    host = _required_str(data, "host", errors)
    tool_call_parser = _required_str(data, "tool_call_parser", errors)
    performance_mode = _optional_str(data, "performance_mode", errors)
    chat_template = _optional_str(data, "chat_template", errors)
    reasoning_parser = _optional_str(data, "reasoning_parser", errors)
    trust_remote_code = data.get("trust_remote_code", False)
    if not isinstance(trust_remote_code, bool):
        errors.append("trust_remote_code must be a boolean")
        trust_remote_code = False
    port = _required_int(data, "port", errors)
    max_model_len = _required_int(data, "max_model_len", errors)
    gpu_memory_utilization = _required_number(data, "gpu_memory_utilization", errors)
    enable_auto_tool_choice = data.get("enable_auto_tool_choice")
    if not isinstance(enable_auto_tool_choice, bool):
        errors.append("enable_auto_tool_choice must be a boolean")
    if port <= 0 or port > 65535:
        errors.append("port must be between 1 and 65535")
    if max_model_len <= 0:
        errors.append("max_model_len must be positive")
    if gpu_memory_utilization <= 0 or gpu_memory_utilization > 1:
        errors.append("gpu_memory_utilization must be > 0 and <= 1")
    optional_flags = parse_optional_flags(data.get("optional_flags", {}), errors)
    if errors:
        raise ServeProfileError("; ".join(errors))
    return ServeProfile(
        profile_id=profile_id,
        vllm_executable=vllm_executable,
        model=model,
        served_model_name=served_model_name,
        host=host,
        port=port,
        max_model_len=max_model_len,
        gpu_memory_utilization=gpu_memory_utilization,
        enable_auto_tool_choice=enable_auto_tool_choice,
        tool_call_parser=tool_call_parser,
        optional_flags=optional_flags,
        performance_mode=performance_mode,
        chat_template=chat_template,
        reasoning_parser=reasoning_parser,
        trust_remote_code=trust_remote_code,
    )


def render_vllm_serve_command(profile: ServeProfile) -> list[str]:
    command = [
        profile.vllm_executable,
        "serve",
        profile.model,
        "--host",
        profile.host,
        "--port",
        str(profile.port),
        "--served-model-name",
        profile.served_model_name,
        "--max-model-len",
        str(profile.max_model_len),
        "--gpu-memory-utilization",
        f"{profile.gpu_memory_utilization:.2f}",
    ]
    if profile.enable_auto_tool_choice:
        command.append("--enable-auto-tool-choice")
    command.extend(["--tool-call-parser", profile.tool_call_parser])
    if profile.reasoning_parser:
        command.extend(["--reasoning-parser", profile.reasoning_parser])
    if profile.chat_template:
        command.extend(["--chat-template", profile.chat_template])
    if profile.performance_mode:
        command.extend(["--performance-mode", profile.performance_mode])
    if profile.trust_remote_code:
        command.append("--trust-remote-code")
    for name in sorted(profile.optional_flags):
        value = profile.optional_flags[name]
        rule = OPTIONAL_FLAG_RULES[name]
        cli_flag = f"--{rule['cli']}"
        if isinstance(value, bool):
            if value:
                command.append(cli_flag)
        else:
            command.extend([cli_flag, str(value)])
    return command


def parse_optional_flags(data: Any, errors: list[str]) -> dict[str, bool | int | float | str]:
    if data is None:
        return {}
    if not isinstance(data, dict):
        errors.append("optional_flags must be an object")
        return {}
    parsed: dict[str, bool | int | float | str] = {}
    for name, value in sorted(data.items()):
        if name not in OPTIONAL_FLAG_RULES:
            errors.append(f"optional flag {name!r} is not approved")
            continue
        rule = OPTIONAL_FLAG_RULES[name]
        expected = rule["type"]
        if expected is bool:
            if not isinstance(value, bool):
                errors.append(f"optional_flags.{name} must be a boolean")
                continue
            parsed[name] = value
        elif expected is int:
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"optional_flags.{name} must be an integer")
                continue
            minimum = rule.get("min")
            if isinstance(minimum, int) and value < minimum:
                errors.append(f"optional_flags.{name} must be >= {minimum}")
                continue
            allowed = rule.get("allowed")
            if isinstance(allowed, set) and value not in allowed:
                errors.append(f"optional_flags.{name} must be one of {sorted(allowed)}")
                continue
            parsed[name] = value
        elif expected is float:
            if not isinstance(value, int | float) or isinstance(value, bool):
                errors.append(f"optional_flags.{name} must be a number")
                continue
            parsed[name] = float(value)
        elif expected is str:
            if not isinstance(value, str) or not value:
                errors.append(f"optional_flags.{name} must be a string")
                continue
            allowed = rule.get("allowed")
            if isinstance(allowed, set) and value not in allowed:
                errors.append(f"optional_flags.{name} must be one of {sorted(allowed)}")
                continue
            parsed[name] = value
        else:
            errors.append(f"optional_flags.{name} has unsupported rule type")
    return parsed


def build_serve_plan(profile: ServeProfile) -> dict[str, Any]:
    command = render_vllm_serve_command(profile)
    return {
        "profile_id": profile.profile_id,
        "mode": "dry-run",
        "classification": "session-mutating",
        "will_execute": False,
        "command": command,
        "command_line": shell_join(command),
        "notes": [
            "This plan renders the vLLM serve command only.",
            "It does not start vLLM or contact the GX10.",
        ],
    }


def _required_str(data: dict[str, Any], field: str, errors: list[str]) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        errors.append(f"{field} is required")
        return ""
    return value


def _optional_str(data: dict[str, Any], field: str, errors: list[str]) -> str | None:
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a non-empty string when provided")
        return None
    return value


def _required_int(data: dict[str, Any], field: str, errors: list[str]) -> int:
    value = data.get(field)
    if not isinstance(value, int):
        errors.append(f"{field} must be an integer")
        return 0
    return value


def _required_number(data: dict[str, Any], field: str, errors: list[str]) -> float:
    value = data.get(field)
    if not isinstance(value, int | float):
        errors.append(f"{field} must be a number")
        return 0.0
    return float(value)


def shell_join(command: list[str]) -> str:
    if command and command[0].startswith("$HOME/"):
        return " ".join([command[0], shlex.join(command[1:])])
    return shlex.join(command)
