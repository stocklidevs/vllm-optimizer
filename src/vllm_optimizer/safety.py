from __future__ import annotations

from typing import Any

from .types import ActionClass, RemoteAction

ALLOWED_PREFIXES: tuple[str, ...] = (
    "nvidia-smi",
    "python -m vllm.entrypoints.openai.api_server",
    "python -m vllm.benchmarks.benchmark_serving",
    "pkill -f vllm.entrypoints.openai.api_server",
    "mkdir -p",
)


def build_dry_run_preview(plan: dict[str, Any]) -> dict[str, Any]:
    actions = render_actions(plan)
    blocked = [action for action in actions if not action.allowed]
    return {
        "experiment_id": plan["experiment_id"],
        "execution_mode": "dry-run",
        "host_label": plan["target"]["host_label"],
        "blocked_action_count": len(blocked),
        "actions": [action_to_dict(action) for action in actions],
    }


def render_actions(plan: dict[str, Any]) -> list[RemoteAction]:
    experiment_id = str(plan["experiment_id"])
    artifact_dir = f"artifacts/{experiment_id}"
    actions: list[RemoteAction] = [
        make_action(
            action_id="global-001",
            trial_id=None,
            kind="prepare-artifact-dir",
            classification="session-mutating",
            command=f"mkdir -p {artifact_dir}",
            expected_side_effects="Creates the remote artifact directory if live execution is enabled later.",
            cleanup=None,
        ),
        make_action(
            action_id="global-002",
            trial_id=None,
            kind="probe-gpu",
            classification="read-only",
            command="nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader",
            expected_side_effects="Reads GPU identity and driver information.",
            cleanup=None,
        ),
    ]

    for trial in plan.get("trials", []):
        trial_id = trial["trial_id"]
        params = render_vllm_params(trial["parameters"])
        actions.extend(
            [
                make_action(
                    action_id=f"{trial_id}-start",
                    trial_id=trial_id,
                    kind="start-vllm",
                    classification="session-mutating",
                    command=(
                        "python -m vllm.entrypoints.openai.api_server "
                        f"--model {plan['model']['id']} {params}"
                    ).strip(),
                    expected_side_effects="Would start a vLLM server for this trial.",
                    cleanup="Stop the matching vLLM server process.",
                ),
                make_action(
                    action_id=f"{trial_id}-benchmark",
                    trial_id=trial_id,
                    kind="run-benchmark",
                    classification="session-mutating",
                    command=(
                        "python -m vllm.benchmarks.benchmark_serving "
                        f"--backend vllm --num-prompts {trial['concurrency']}"
                    ),
                    expected_side_effects="Would send benchmark requests to the trial server.",
                    cleanup=None,
                ),
                make_action(
                    action_id=f"{trial_id}-cleanup",
                    trial_id=trial_id,
                    kind="stop-vllm",
                    classification="session-mutating",
                    command="pkill -f vllm.entrypoints.openai.api_server",
                    expected_side_effects="Would stop the vLLM server started for this trial.",
                    cleanup=None,
                ),
            ]
        )

    return actions


def make_action(
    *,
    action_id: str,
    trial_id: str | None,
    kind: str,
    classification: ActionClass,
    command: str,
    expected_side_effects: str,
    cleanup: str | None,
) -> RemoteAction:
    return RemoteAction(
        action_id=action_id,
        trial_id=trial_id,
        kind=kind,
        classification=classification,
        command=command,
        allowed=is_allowed(command),
        expected_side_effects=expected_side_effects,
        cleanup=cleanup,
    )


def is_allowed(command: str) -> bool:
    return any(command.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def render_vllm_params(parameters: dict[str, Any]) -> str:
    parts = []
    for key in sorted(parameters):
        cli_name = key.replace("_", "-")
        value = parameters[key]
        parts.append(f"--{cli_name} {value}")
    return " ".join(parts)


def action_to_dict(action: RemoteAction) -> dict[str, Any]:
    return {
        "action_id": action.action_id,
        "trial_id": action.trial_id,
        "kind": action.kind,
        "classification": action.classification,
        "command": action.command,
        "allowed": action.allowed,
        "expected_side_effects": action.expected_side_effects,
        "cleanup": action.cleanup,
    }
