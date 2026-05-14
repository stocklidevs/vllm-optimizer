from vllm_optimizer.discovery import DiscoveryTarget
from vllm_optimizer.ssh import MockExecutor
from vllm_optimizer.system_tuning import (
    PROBES,
    SystemTuningError,
    TuningProbe,
    run_system_tuning_discovery,
    validate_probe_catalog,
)

import pytest


def test_system_tuning_discovery_builds_catalog(tmp_path):
    target = DiscoveryTarget("gx10", "mock@example", ("mock@example",), timeout_seconds=10)
    executor = MockExecutor(
        {
            "nvidia-driver": {"exit_code": 0, "stdout": "575.51.03\n"},
            "gpu-power": {"exit_code": 0, "stdout": "250.00 W, 600.00 W\n"},
            "gpu-clocks": {"exit_code": 0, "stdout": "210, 2400, P2\n"},
            "gpu-persistence": {"exit_code": 0, "stdout": "Enabled\n"},
            "cpu-governor": {"exit_code": 0, "stdout": "performance\n"},
            "cpu-topology": {"exit_code": 0, "stdout": "CPU(s): 20\n"},
            "memory": {"exit_code": 0, "stdout": "MemTotal: 1000 kB\nSwapTotal: 0 kB\n"},
            "transparent-hugepages": {"exit_code": 0, "stdout": "always [madvise] never\n"},
            "kernel-limits": {"exit_code": 0, "stdout": "1048576\n"},
            "vllm-env": {"exit_code": 0, "stdout": "CUDA_VISIBLE_DEVICES=0\n"},
        }
    )

    result = run_system_tuning_discovery(target, executor, tmp_path)

    catalog = result["catalog"]
    assert catalog["status"] == "completed"
    assert catalog["entries"]["nvidia.driver_version"]["current_value"] == "575.51.03"
    assert catalog["entries"]["gpu.persistence_mode"]["future_action_classification"] == "session-mutating"
    assert catalog["entries"]["memory.transparent_hugepages"]["current_value"] == "madvise"
    assert (tmp_path / "raw-probes.json").exists()
    assert (tmp_path / "catalog.json").exists()


def test_system_tuning_discovery_marks_missing_optional_probe_unavailable(tmp_path):
    target = DiscoveryTarget("gx10", "mock@example", (), timeout_seconds=10)
    executor = MockExecutor({})

    result = run_system_tuning_discovery(target, executor, tmp_path)

    catalog = result["catalog"]
    assert catalog["status"] == "completed-with-unavailable"
    assert catalog["entries"]["nvidia.driver_version"]["status"] == "unavailable"
    assert "missing mock output" in catalog["entries"]["nvidia.driver_version"]["reason"]


def test_system_tuning_probe_catalog_rejects_mutating_probe():
    probes = (
        *PROBES,
        TuningProbe(
            "bad",
            "gpu",
            "bad",
            "sudo nvidia-smi -pm 1",
            "session-mutating",
            "line",
        ),
    )

    with pytest.raises(SystemTuningError, match="non-read-only"):
        validate_probe_catalog(probes)
