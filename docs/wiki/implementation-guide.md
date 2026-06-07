# Implementation Guide

emage.code uses a **version-independent** `implementation/` tree at the repository
root. It provides schema-first canonical knowledge, managed cookbooks, trigger
workflows, packaging, and validation super-gates (current release: v5.0.0).

## What to use it for

- cookbook-driven orchestration definitions
- trigger-based execution with policy guardrails
- package install / update / uninstall workflows
- adapter smoke testing and compatibility checks
- mandatory workflow skills (`/discover-skills`, `/handoff`, safety guards)

## Install

**Recommended:** use the installer from the repo root:

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target <your-project> --platform cursor
```

Or see [Quick Start](quick-start) and [`docs/releases/v5.0.0.md`](https://gitlab.com/em-age/emage.code/-/blob/main/docs/releases/v5.0.0.md).

Supported projections: GitHub Copilot, Gemini CLI, Opencode, Cursor, Pi.

## Validate (maintainers)

From the repository root:

```bash
python3 implementation/scripts/check-v3.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
node implementation/scripts/verify-v3.mjs --root implementation
```

## Main entry points

- [Implementation README](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/README.md)
- [Agents Overview](agents-overview)
- [Quick Start](quick-start)
- [Archive](https://gitlab.com/em-age/emage.code/-/tree/main/archive) — frozen v1/v2 streams

## Notes

- Edit canonical files under `implementation/knowledge/` only; run `make sync`.
- Previous version paths live under `archive/v1`, `archive/v2`, `archive/v3`.
