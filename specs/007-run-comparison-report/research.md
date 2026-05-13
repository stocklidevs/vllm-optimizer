# Research: Run Comparison Report

## Decision: Prefer Repeated Rankings for Recommendations

Rationale: Repeated sweep rankings include stability metrics and are better
evidence than one-shot sweep rankings.

Alternatives considered: Always choosing the highest one-shot throughput was
rejected because it ignores run-to-run noise.

## Decision: Emit JSON First, Markdown as Optional Companion

Rationale: JSON is scriptable and testable. Markdown makes the same result
easy to read and share.

Alternatives considered: Markdown-only reports were rejected because they would
lose structured traceability.

## Decision: Treat Missing Inputs as Notes

Rationale: The operator may want a report from only a repeated ranking or only
a sweep ranking. Missing optional context should be visible, not fatal.

Alternatives considered: Requiring all inputs was rejected because it would
make partial historical reports harder to generate.
