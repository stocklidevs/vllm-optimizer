# Data Model: Qwen Smoke Serve

## SmokeServePlan

Fields:
- `profile_id`
- `serve_command`
- `preflight_checks`
- `readiness`
- `smoke_request`
- `cleanup`
- `will_execute`

## PreflightResult

Fields:
- `port_free`
- `matching_process_absent`
- `details`

## SmokeRunResult

Fields:
- `status`
- `started`
- `pid`
- `readiness`
- `request`
- `cleanup`
- `log_path`

## SmokeArtifact

Fields:
- `plan_path`
- `summary_path`
- `server_log_path`
- `response_path`
- `cleanup_path`
- `redaction_report_path`
