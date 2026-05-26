# Contract: Model Catalog

The model catalog is a deterministic JSON document used by CLI and cockpit
surfaces to describe which models can be selected.

Required top-level fields:

- `schema_version`: Catalog contract version.
- `generated_at`: Timestamp or `static` marker for committed catalogs.
- `models`: Ordered array of model candidates.

Required model fields:

- `model_id`
- `display_name`
- `runtime`
- `source_model`
- `served_model_name`
- `support_status`
- `tool_support`
- `baseline_notes`
- `source_urls`

Optional model fields:

- `profile_path`
- `default_objectives`
- `warnings`
- `external_baseline_notes`

Rules:

- Local vLLM candidates must include `profile_path`.
- External API baselines must not include a local vLLM profile path.
- Untested models must not use `support_status=measured`.
- Models are ordered by recommended validation priority.
