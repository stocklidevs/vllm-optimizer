# Contract: Public Release Checklist

The public release checklist is a Markdown document at `docs/PUBLIC_RELEASE.md`.

Required sections:

- `# Public Release Checklist`
- `## Release Label`
- `## Required Public Files`
- `## Verification Gates`
- `## Fresh Checkout Smoke`
- `## Safety And Scope`
- `## Known Limitations`
- `## Publication Steps`

Required content:

- The release label must identify the project as public alpha.
- Required public files must list README, LICENSE, CONTRIBUTING, SECURITY, CHANGELOG, setup docs, results docs, and project status docs.
- Verification gates must include full pytest and `release-check`.
- Fresh checkout smoke must include a no-GX10 local path.
- Safety and scope must state that live GX10 runs require local config and SSH access.
- Known limitations must mention GX10 specificity and experimental cockpit status.
