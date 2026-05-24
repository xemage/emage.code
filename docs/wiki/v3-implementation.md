# v3 Implementation

emage.code v3 is the schema-first implementation stream. It keeps the same
27-agent permission model, but adds managed cookbooks, trigger workflows,
packaging, adapter smoke tests, and a stricter validation super-gate.

## What to use v3 for

Use v3 when you need:

- cookbook-driven orchestration definitions
- trigger-based execution with policy guardrails
- package install / update / uninstall workflows
- adapter smoke testing and compatibility checks
- stronger validation around schema integrity and projection drift

## Quick start

From the repository root:

```bash
python3 v3/implementation/scripts/check-v3.py --root v3/implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
node v3/implementation/scripts/verify-v3.mjs --root v3/implementation
```

## Main entry points

- [v3 implementation README](https://gitlab.com/em-age/emage.code/-/blob/main/v3/implementation/README.md)
- [Agents Overview](agents-overview)
- [Quick Start](quick-start)
- [Contributing Workflow](contributing-workflow)

## Notes

- v3 is ready for controlled use, but it still follows the same repository
  release and documentation gate model as v2.
- Keep `v3/implementation/README.md` and the wiki page in sync when command
  examples change.
