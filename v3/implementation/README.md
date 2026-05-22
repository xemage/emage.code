# emage.code v3 implementation

v3 contains the next-generation implementation stream for schema-first knowledge,
managed cookbooks, and validation super-gates.

## Validation commands

Run from repository root:

```bash
python3 v3/implementation/scripts/check-v3.py --root v3/implementation --required --schemas --cookbooks
```

Projection drift checks:

```bash
node v3/implementation/scripts/verify-v3.mjs --root ../../v2/implementation
```

Notes:
- During migration, `verify-v3.mjs` can target `v2/implementation` with `--root`
  for compatibility validation.
- Once v3 canonical knowledge and platform manifests are fully populated, run
  drift checks directly against `v3/implementation`.

## CI integration

Recommended CI stage order:

1. `python3 v3/implementation/scripts/check-v3.py --root v3/implementation --required --schemas --cookbooks`
2. `node v3/implementation/scripts/verify-v3.mjs --root ../../v2/implementation`
3. v3 functional tests:
   `python3 -m unittest tests.functional.test_v3_validation_gate -v`

The gate must fail on unresolved references, missing required files, malformed
cookbook manifests, and projection drift.
