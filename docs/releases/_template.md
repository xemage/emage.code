# Release vX.Y.Z

Copy this file to `docs/releases/vX.Y.Z.md` on the `release/vX.Y.Z` branch before the tag is cut, and delete this paragraph. It is the release's one document: `scripts/verify-release-docs.py --tag vX.Y.Z` checks it, its sections follow skill `release-workflow` § 4, the release job publishes it whole as the GitLab Release description, and `/prepare-release` step 7 writes the release gate verdict into it. Keep the first line as `# Release vX.Y.Z`. Do not quote the verdict section's heading text above that section. Cite repository files as code spans or absolute URLs, not relative links.

## Summary

<1-3 sentences: what this release contains>

## Install

Latest release: vX.Y.Z

Install with the installer from a clone of this repository:

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target <your-project> --platform <name>
```

| Platform | `--platform` value |
|----------|-------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| Claude Code | `claude-code` |
| Cline | `cline` |
| All platforms | `all` |

Update an existing install: add `--update`. `scripts/install.sh --help` lists every option.

Set the MCP environment variables named in the generated MCP config, then run
`/new-project "Your idea"` in your assistant.

## Highlights

- Feature one — what users get in this release
- Feature two — …

## Breaking changes

- None (or one entry per breaking change; the verdict count equals the number of entries)

## Migration Guide

<if applicable — steps to upgrade from the previous version>

## Changelog

<one line per entry: description, task ID, artifact version references>

### Features

### Fixes

### Internal

## Known Issues

- <any known issues shipping with this release>

## Gate Verdicts

- Architecture: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD
- Implementation: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD
- Integration: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD
- Security: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD
- Release: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD (the same value as the Status below)

## RELEASE VERDICT

Release gate outcome for this version, per step 7 of `/prepare-release`. This document is the
declared home for the block; fill in every field before the tag is cut.

- **Version**: vX.Y.Z
- **Status**: PASS | CONDITIONAL_PASS | FAIL
- **Features included**: <count>
- **Fixes included**: <count>
- **Breaking changes**: <count>
- **Open blockers**: <count>
- **Quality gates passed**: [list gates: code-review, security-audit, test-coverage, ...]
- **Quality gates failed**: [list any failed gates]
- **Blocker IDs**: [if FAIL — list blocking issues with owners]
- **Release manager**: release-manager
- **Timestamp**: <ISO-8601>

## Rollback Plan

<steps to roll back if critical issues are discovered after the release; state whether they were tested>
