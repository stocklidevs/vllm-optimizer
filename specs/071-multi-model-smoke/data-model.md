# Data Model: Multi-Model Registry and Smoke Workflow

## Model Candidate

- `model_id`: Stable internal identifier.
- `display_name`: User-facing model name.
- `runtime`: `local-vllm` or `external-api`.
- `source_model`: Upstream model identifier or API family.
- `served_model_name`: Name expected by OpenAI-compatible requests.
- `profile_path`: Local serve profile path when runnable through vLLM.
- `support_status`: `measured`, `recipe-captured`, `candidate`, `optional`, or `deferred`.
- `tool_support`: `supported`, `plain-chat-first`, `unknown`, or `external`.
- `baseline_notes`: Short readiness/performance baseline summary.
- `source_urls`: Upstream validation links.

## Model Smoke Plan

- `model_id`: Catalog model identifier.
- `profile_id`: Serve profile identifier.
- `will_execute`: Always false for dry-run planning.
- `classification`: `session-mutating` for live smoke.
- `serve_command`: Tokenized vLLM serve command.
- `preflight_checks`: Port, process, template, and dependency checks.
- `readiness_probe`: Local vLLM models endpoint probe.
- `chat_probe`: Deterministic plain chat request.
- `tool_probe`: Optional deterministic tool-call request.
- `cleanup`: Managed process termination steps.

## Model Smoke Result

- `model_id`: Catalog model identifier.
- `status`: `passed`, `failed`, `partial`, `unsupported`, or `refused`.
- `started_at` / `completed_at`: Run timestamps.
- `serve_ready`: Readiness outcome.
- `chat_ready`: Plain chat outcome.
- `tool_ready`: Tool-call outcome or unsupported marker.
- `cleanup_ready`: Cleanup outcome.
- `artifact_paths`: Raw plan, logs, responses, cleanup, and redaction artifacts.
- `failure_detail`: User-facing failure explanation when available.

## Model Readiness Summary

- `model_id`: Catalog model identifier.
- `latest_smoke_status`: Latest known smoke result status.
- `latest_performance_baseline`: Latest measured throughput/latency baseline, if any.
- `recommended_next_action`: Smoke, benchmark, sweep, inspect failure, or defer.
