# Data Model: GX10 Read-Only Discovery

## DiscoveryTarget

Fields:
- `target_label`: stable label such as `gx10`
- `ssh_destination`: local SSH destination string
- `timeout_seconds`: default per-probe timeout
- `redact_values`: secret values to redact from artifacts

Validation:
- Must include target label and SSH destination.
- Must not be committed when it contains real private values.

## ProbeDefinition

Fields:
- `probe_id`
- `purpose`
- `command`
- `classification`
- `timeout_seconds`
- `parser`

Validation:
- Classification must be `read-only`.
- Commands are from a fixed catalog.

## ProbeResult

Fields:
- `probe_id`
- `command`
- `classification`
- `status`
- `exit_code`
- `stdout`
- `stderr`
- `timed_out`
- `duration_ms`

State:
- `success`
- `failed`
- `skipped`

## HostFacts

Fields:
- `connectivity`
- `hostname`
- `os`
- `kernel`
- `gpu`
- `nvidia_driver`
- `cuda_visible`
- `python`
- `vllm`
- `unavailable`

## DiscoveryRun

Fields:
- `run_id`
- `target_label`
- `started_at`
- `completed_at`
- `tool_version`
- `git_commit`
- `probes`
- `facts`
- `status`
- `artifact_paths`

## RedactionReport

Fields:
- `redacted_value_count`
- `replacement`
- `artifact_paths`
