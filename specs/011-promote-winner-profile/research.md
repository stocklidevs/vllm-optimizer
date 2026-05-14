# Research: Promote Winner Profile

## Decision: Local-only promotion from ranking artifacts

Rationale: The ranking artifact already contains objective rankings,
candidate aggregates, metrics, and artifact paths. Promotion should reuse that
evidence without rerunning benchmarks or contacting the GX10.

Alternatives considered: Running a fresh confirmation benchmark during
promotion was rejected because it changes the safety class and belongs in a
separate stability-confirmation spec.

## Decision: Two-step preview and write flow

Rationale: Preview lets the operator audit the selected objective/candidate and
provenance before creating tracked configuration. The write command can share
the same selection logic and add output/overwrite guards.

Alternatives considered: A single command that always writes was rejected
because it makes accidental promotion easier.

## Decision: Store provenance inside the generated profile

Rationale: Live artifacts are gitignored, so the checked-in recommended profile
needs enough embedded provenance to explain where the settings came from even
when raw artifacts are not present in a clone.

Alternatives considered: Keeping provenance only in a separate summary was
rejected because the profile could be copied without its summary.

## Decision: Strict fail-closed validation

Rationale: Recommendations should not be produced from missing objectives,
missing aggregates, zero-success candidates, or unreconstructable profile data.

Alternatives considered: Best-effort partial profiles were rejected because
silent gaps would make recommendations less auditable.
