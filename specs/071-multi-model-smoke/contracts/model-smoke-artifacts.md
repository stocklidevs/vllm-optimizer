# Contract: Model Smoke Artifacts

Smoke artifacts live under a model-specific artifact directory and must be
readable without contacting the GX10.

Required artifacts:

- `smoke-plan.json`: Dry-run action preview and rendered command.
- `summary.json`: Structured outcome with status and failure details.
- `server-log.json`: Redacted vLLM server log.
- `smoke-response.json`: Redacted plain-chat and optional tool-call responses.
- `cleanup.json`: Managed process cleanup outcome.
- `redaction-report.json`: Redaction count and artifact path index.

Required summary fields:

- `model_id`
- `profile_id`
- `status`
- `serve_ready`
- `chat_ready`
- `tool_ready`
- `cleanup_ready`
- `artifact_paths`

Status rules:

- `passed`: serve, chat, required tool probes, and cleanup succeeded.
- `partial`: serve/chat passed but optional tool probe failed or was skipped.
- `failed`: readiness or required plain chat failed.
- `refused`: preflight safety checks blocked execution.
- `unsupported`: model runtime cannot be smoked through local vLLM.
