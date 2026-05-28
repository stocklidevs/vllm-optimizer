# Security Policy

## Supported Versions

The public alpha supports the current `0.56.x` line only. Older local snapshots
may contain experimental GX10 automation and cockpit code that is not maintained
as a supported security surface.

## Reporting A Vulnerability

Please do not open a public issue for vulnerabilities involving credentials,
remote command execution, SSH access, local config leakage, or unsafe live-run
behavior. Use GitHub private vulnerability reporting if it is enabled for the
repository. If it is not enabled, request a private contact channel from the
maintainer without including exploit details in the public request.

Useful reports include:

- Affected command or web cockpit action.
- Whether the issue requires a live GX10 config or can reproduce locally.
- Minimal reproduction steps using redacted paths, hostnames, and tokens.
- Expected impact and any relevant artifact paths.

## Scope

In scope:

- Local CLI command behavior.
- Local web cockpit behavior.
- Artifact parsing, report generation, and release-check behavior.
- Handling of ignored local configs and generated artifacts.
- SSH command preview/run boundaries for live GX10 workflows.

Out of scope for the public alpha:

- Attacks requiring access to a maintainer's private GX10, private network account,
  SSH key, password, or local workstation.
- Persistent system tuning, Docker cleanup, firmware, kernel, boot, service, or
  credential changes that are explicitly outside the supported optimizer scope.
- Third-party model, vLLM, PyTorch, CUDA, or operating-system vulnerabilities
  unless vLLM Optimizer materially worsens exposure.

## Safety Defaults

The optimizer should keep live actions gated, deterministic previews visible,
and promotion explicit. A security fix should preserve those defaults even when
it improves ergonomics.
