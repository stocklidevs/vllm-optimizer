---
name: Bug report
about: Report a reproducible CLI, artifact, or cockpit problem
title: "[bug]: "
labels: bug
assignees: ""
---

## What Happened?

Describe the failure and what you expected instead.

## Reproduction

```powershell
# Paste the smallest command sequence that reproduces the issue.
```

## Environment

- vLLM Optimizer version:
- Python version:
- OS:
- vLLM version, if live:
- Model/profile, if live:
- Local-only or live SSH/GX10:

## Artifacts

List relevant local artifact paths, after redacting private hostnames, usernames,
tokens, and absolute private paths.

## Safety Context

- Did the command use live SSH execution?
- Did it use `--allow-risky-session-flags`, `--allow-session-tuning`, or
  `--allow-promotion`?
- Did it start or stop vLLM?
