**Status:** done
**Completed:** 2026-05-23
# Task T018 — Package and install workflow

## Objective
Implement package and installation workflows for reusable v3 knowledge packs.

## Inputs
- v3 registry artifacts
- package/install patterns from ecosystem research

## Expected outputs
- v3/implementation/commands/package-*.md
- v3/implementation/scripts/package-v3.*
- Installer/update/uninstall documentation

## Acceptance criteria
- Local pack install, update, and uninstall flows work deterministically.
- Package metadata validates against schema.
- Workflow supports HTTPS git sources and local paths.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
