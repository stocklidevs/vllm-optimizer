# Data Model: vLLM Flag Catalog

## FlagPolicy

- `policy_id`
- `categories`: Map of category name to flag entries.
- `rationale`: Safety rationale per flag.

## ParsedFlag

- `name`: Long flag name without leading dashes.
- `aliases`: Any additional aliases.
- `source_line`: Help line where the flag appeared.

## FlagCatalog

- `policy_id`
- `vllm_version`
- `flag_count`
- `categories`
- `unavailable_policy_flags`
- `unclassified_flags`
- `artifact_paths`

## FlagCaptureArtifact

- `version`
- `serve_help`
- `catalog`
- `redaction`
