# Witness Signing Keys (T232)

This directory holds **DEV-ONLY** Ed25519 public keys used for release-gate
witness verification.

## Files

| File | Committed? | Purpose |
|------|-----------|---------|
| `witness-dev.pub` | Yes (public) | Dev public key for verifying example/CI witnesses |
| `*.ed25519.key` | **NEVER** | Private signing keys — git-ignored, generated locally |

## Generating a local keypair

```bash
python3 -c "
import importlib.util, pathlib
p = pathlib.Path('implementation/adapters/sia-target/release_gate.py')
spec = importlib.util.spec_from_file_location('rg', p)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(m.generate_keypair('implementation/adapters/sia-target/keys'))
"
```

This writes `witness-dev.ed25519.key` (private, `0600`) and `witness-dev.pub`.
The private key is git-ignored (`**/keys/*.key`, `*.ed25519.key`) and must
never be committed.

## Signing key source at runtime

The private key path is supplied via argument or the `SIA_WITNESS_PRIVATE_KEY`
environment variable. No key material lives in source.

## ⚠️ Production warning

These keys are **for development and CI only**. Production witness signing MUST
use a managed KMS/HSM signer with key rotation and audit logging. See
`docs/artifacts/release-gate-witness-v1.md` for the production debt items.
