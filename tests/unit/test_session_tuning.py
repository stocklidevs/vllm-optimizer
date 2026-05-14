from pathlib import Path

import pytest

from vllm_optimizer.artifacts import read_json, write_json
from vllm_optimizer.session_tuning import (
    SessionTuningError,
    build_session_tuning_preview,
    load_session_tuning_profile,
    render_session_tuning_prelude,
)


def test_session_tuning_preview_renders_env_and_ulimit(tmp_path: Path) -> None:
    profile = tmp_path / "profile.json"
    catalog = tmp_path / "catalog.json"
    _write_catalog(catalog)
    write_json(
        profile,
        {
            "profile_id": "runtime-env",
            "classification": "session-mutating",
            "environment": {"CUDA_MODULE_LOADING": "LAZY", "VLLM_WORKER_MULTIPROC_METHOD": "spawn"},
            "ulimits": {"nofile": 500000},
        },
    )

    preview = build_session_tuning_preview(load_session_tuning_profile(profile), catalog)

    assert preview["will_execute"] is False
    assert preview["classification"] == "session-mutating"
    assert preview["actions"][0]["command"] == "export CUDA_MODULE_LOADING=LAZY"
    assert preview["actions"][2]["command"] == "ulimit -n 500000"
    assert "export VLLM_WORKER_MULTIPROC_METHOD=spawn" in render_session_tuning_prelude(preview)


def test_session_tuning_rejects_persistent_action(tmp_path: Path) -> None:
    profile = tmp_path / "profile.json"
    write_json(
        profile,
        {
            "profile_id": "bad",
            "classification": "persistent-mutating",
            "environment": {},
            "ulimits": {},
        },
    )

    with pytest.raises(SessionTuningError, match="session-mutating"):
        load_session_tuning_profile(profile)


def _write_catalog(path: Path) -> None:
    write_json(
        path,
        {
            "entries": {
                "vllm.env": {"status": "available", "future_action_classification": "session-mutating"},
                "kernel.open_file_limit": {"status": "available", "future_action_classification": "session-mutating"},
            }
        },
    )
