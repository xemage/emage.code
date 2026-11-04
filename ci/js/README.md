# ci/js — JavaScript tooling for CI

Based on: `docs/tasks/task-T732.md` (SEC-T677-01, the user's decision of 2026-11-02 "Add a JS parser").

This directory holds the only npm dependency of the test suite: the [acorn](https://github.com/acornjs/acorn)
JavaScript parser. `tests/functional/test_function_size.py` calls `measure-functions.mjs`, which parses
each `.mjs`, `.js` and `.cjs` file with acorn and prints every function with its first and last line, so
the 50-line standard of AGENTS.md is measured on the syntax tree instead of by line heuristics.

| File | Purpose |
|------|---------|
| `package.json` | `"private": true`, one dependency pinned to an exact version, no scripts |
| `package-lock.json` | lockfile v3: the resolved tarball URL and its `sha512` integrity hash |
| `measure-functions.mjs` | the measurer (`node measure-functions.mjs FILE...` or `--stdin NAME`), JSON on stdout |

## Pinned version

- `acorn@8.19.0`, published to npm on 2026-10-05 (four weeks before it was pinned on 2026-11-02), MIT,
  no dependencies, no install scripts. It has no npm provenance attestation; the maintainers are the acorn
  core team (`marijn`, `adrianheine`, `rreverser`).

## Install

```bash
npm ci --ignore-scripts --prefix ci/js
```

`npm ci` installs exactly the lockfile and fails on a mismatch with `package.json` or a hash mismatch.
`--ignore-scripts` runs no lifecycle script (acorn declares none, but the flag keeps it that way if a
version adds one). The CI `unit-tests` job runs this command (with `--no-audit --no-fund`) before the
suite, after `apk add 'npm~=11'`. `node_modules/` is ignored by the root `.gitignore` and is never committed.

Without the parser, the JavaScript checks of `test_function_size.py` **skip locally** with the reason
and the install command, and **fail when `CI` is set**, so a broken CI image cannot hide them. The Python
and Bash checks run either way.

## Update rule

1. Pick a version published **at least 14 days** before the update day (`npm view acorn time --json`),
   with no new runtime dependency and no install script
   (`npm view acorn@<v> dependencies scripts --json`; acorn's `prepare` script runs only in its own
   repository, not on install).
2. Set the exact version in `package.json`, then regenerate the lock from this directory:
   `npm install --package-lock-only --ignore-scripts --no-audit --no-fund --registry=https://registry.npmjs.org/`.
3. Check that the lock's `integrity` equals `npm view acorn@<v> dist.integrity`, and that the lock holds no
   other package (`test_lockfile_carries_integrity_hashes_and_matches_the_pin` fails on a new dependency:
   a new dependency needs a review first).
4. `npm ci --ignore-scripts --prefix ci/js`, run `python3 -m unittest tests.functional.test_function_size`
   and the full suite, and update the version and date above.
5. Optionally prove the install in the pinned CI image, as in `docs/wiki/mcp-pin-bump-checklist.md` § 3.
