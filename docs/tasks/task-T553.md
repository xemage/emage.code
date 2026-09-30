# T553 — `install.sh` never installs `implementation/runtime/handoff/`, so `/handoff` step 3 dangles

**ID:** T553
**Owner:** DevOps Engineer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** T550
**Created:** 2026-09-30
**Based on:** `docs/plans/plan-083-four-decisions-and-batching.md` §4 (P1, trigger fired);
`docs/artifacts/command-audience-resolution-v1.md` §6; `scripts/install.sh`.

## 1. The defect

`/handoff` is `maturity: stable`. Its step 3 says: *"Draft handoff payload conforming to
`implementation/runtime/handoff/schema-v1.json`"*. `install.sh` installs only `runtime/memory/` and
`runtime/security/` into a target (`install_mcp_server_runtime`), so in an installed project that path
does not exist and step 3 cannot be followed.

`implementation/runtime/handoff/` contains `schema-v1.json`, `validator.py`, `examples/` (and a
`__pycache__/`).

## 2. The decided repair — T546, `command-audience-resolution-v1.md` §6

**Repair the installer; do not touch the command.** Add one `install_tree_into` for
`runtime/handoff` beside its two siblings in `install_mcp_server_runtime`, excluding `__pycache__`, on
that function's own stated rationale. The path in `/handoff` then resolves identically in both
audiences. This is `plan-083` §4's P1, whose trigger ("T550 merged") has fired.

Decide whether `examples/` and `validator.py` ship too, or only the schema, and say why.

## 3. Interaction with T552 — same function, batched

`install_mcp_server_runtime` is exactly where T552's data-loss defect lives: at the repository root,
`src == dest`. **Adding a third `install_tree_into` there adds a third directory to that defect** —
`implementation/runtime/handoff/` would also be deleted by `--update` at the root without `rsync`.
So **T552's fix must land in the same MR, before or with this change.** Prove with a test that
`runtime/handoff/` survives `--update` at a synthetic repo root under the `cp` fallback.

## 4. Constraints and verification

As T552 §5–§6: write scope `scripts/install.sh` and new `tests/functional/` files; a test that a fresh
install into a temp target now contains `implementation/runtime/handoff/schema-v1.json`; every other
invocation unchanged in what it writes, compared **in place**; commit locally, never push or merge.
`/handoff`'s golden case (`handoff-payload-schema-fields-real`) embeds its own schema in its fixture
and is not affected — do not read or edit `tests/golden/**`.

**This changes what every future install writes into a target.** That is intended; state it plainly
in the commit message.
