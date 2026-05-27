# Implementation Plan: Public Branch Cleanup

**Branch**: `codex/public-release-cleanup` | **Date**: 2026-05-27 |
**Spec**: [spec.md](spec.md)

## Summary

Prepare the project for the final pre-public branch review by adding CI,
publication checklist documentation, release-check coverage for the new public
files, and verification evidence. Do not push or publish the branch.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Existing Python standard-library package; pinned npm
dev dependency `playwright@1.60.0` for UI QA support

**Testing**: pytest, release-check, npm ci, npm audit

**Constraints**: No live GX10 execution, no public push, no private config
changes, no new runtime dependencies

## Constitution Check

- **Deterministic Experiments**: PASS. No benchmark behavior changes.
- **Complete Traceability**: PASS. Publication gates are documented and tested.
- **Remote Safety and Reversibility**: PASS. Cleanup is local-only.
- **Objective-Driven Optimization**: PASS. Objective is public branch readiness.
- **Testable, Modular Automation**: PASS. CI and release-check cover the new
  public branch gates.
