# Research: GX10 Read-Only Discovery

## Decision: Local JSON config with ignored real files

**Rationale**: JSON is already used by the MVP and avoids new dependencies.
`config/gx10.example.json` documents the shape while `config/local*.json`
remains ignored for real IPs, usernames, and redaction values.

**Alternatives considered**: TOML was reasonable but would add another config
shape. Environment-only configuration was rejected because redaction lists and
timeouts are easier to audit in a local file.

## Decision: Mock executor first, SSH executor interface only

**Rationale**: The user asked to do everything possible until connection is
needed. A mock executor proves parsing, safety, redaction, and artifacts
without touching the GX10.

**Alternatives considered**: Implementing real SSH immediately was deferred to
avoid accidental remote contact before the discovery contract is tested.

## Decision: Fixed read-only probe catalog

**Rationale**: A fixed catalog is easier to audit and test than accepting
operator-provided shell commands. Each probe has a purpose, command,
classification, timeout, and parser.

**Alternatives considered**: User-provided arbitrary probes were rejected for
this feature because they would weaken the safety boundary.

## Decision: Redact before writing artifacts

**Rationale**: Raw artifacts are valuable, but they must still be safe to store.
Every artifact write receives already-redacted data, and tests assert secrets
do not appear in saved JSON.

**Alternatives considered**: Redacting only reports was rejected because raw
probe logs are also retained.
