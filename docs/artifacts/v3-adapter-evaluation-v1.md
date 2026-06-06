# v3 Adapter Evaluation v1

Status: Experimental
Based on: [implementation/triggers/spec-v1.md](../../implementation/triggers/spec-v1.md)

## Scope

Evaluate two optional adapter prototypes that map trigger framework inputs into portable execution payloads:
- Antigravity-style runtime orchestration adapter.
- Opencode automation-script adapter.

## Prototype outputs

- [implementation/adapters/antigravity_adapter.py](../../implementation/adapters/antigravity_adapter.py)
- [implementation/adapters/opencode_adapter.py](../../implementation/adapters/opencode_adapter.py)
- [implementation/adapters/smoke.py](../../implementation/adapters/smoke.py)

## Security constraints

- Adapters are disabled by default behind feature flags.
- Global gate: `V3_EXPERIMENTAL_ADAPTERS` must be enabled.
- Per-adapter gates: `V3_ADAPTER_ANTIGRAVITY` and `V3_ADAPTER_OPENCODE`.
- Opencode adapter enforces `allowArbitraryShell=false` and maps to fixed workflow commands.
- No adapter logs secrets from trigger payloads; smoke output contains only mapped fields.

## Portability constraints

- Prototypes do not import external SDK packages.
- Payload contracts are plain JSON and deterministic.
- Adapter output is transport-neutral and can be handed to runtime-specific wrappers later.

## Smoke test matrix

| Adapter | Command | Expected |
|---|---|---|
| antigravity | `python3 implementation/adapters/smoke.py --adapter antigravity --input tests/fixtures/adapters/sample-input.json` | exit 0 + normalized orchestration payload |
| opencode | `python3 implementation/adapters/smoke.py --adapter opencode --input tests/fixtures/adapters/sample-input.json` | exit 0 + guarded automation script |
| disabled flag | same command with flags unset | exit 2 + `adapter_disabled` |

## Recommendation

Go for controlled experimental use only.

Conditions before production go-live:
1. Replace static workflow mapping with signed policy-backed mapping.
2. Add adapter-specific JSON schemas and strict validation on input and output.
3. Integrate telemetry parity checks against v3 trajectory schema.

Follow-up scope:
- Add real SDK integrations behind separate dependency extras.
- Add compatibility tests for Copilot, Gemini, and Opencode runtime surfaces.
