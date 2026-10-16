# plan-085 — The installer can leak this repository's memory index into client projects

**Created:** 2026-09-30
**Based on:** MR !427 (T552, T553); `docs/tasks/task-T553.md`; `scripts/install.sh`.
**Scopes:** `T555`.

## 1. Finding

T553's implementer found that under `--update` without `rsync`, `sync_tree_into`'s fallback copies the
source's **excluded** paths into a target that lacks its own. The orchestrator then checked what that
means in practice: `implementation/runtime/memory/_index/` is **populated** in this checkout (3 files,
460 KB, under a directory named for this repository), gitignored but present in the working tree the
installer reads. On any host without `rsync`, updating a client project from this checkout **copies
this repository's memory index into the client's project**. That is information disclosure.

It predates T552/T553 (measured on `fda6a90`); !427 does not widen it for `_index/`. The fresh-install
path is safe.

## 2. Why P1, and why now

Confidentiality, not correctness: a client project receiving another project's memory index is the
kind of defect `security-guidelines.md`'s Immutable Security Constraints exist to prevent. `**Affects:**
—`, so the P1 row cannot block merges. `scripts/install.sh` is free now that !427 has merged, so it runs
immediately; T554 (knowledge + golden) runs in parallel on disjoint files once T538 lands.

## 3. Parked from !427's hand-back

| # | Item | Trigger |
|---|---|---|
| P17 | `--target <repo>/implementation --update` still writes the source (re-renders `implementation/AGENTS.md` over itself, creates `implementation/implementation/`); the new guard already stops the `.cursor/` deletion. Refuse any target `-ef` `$IMPLEMENTATION`. | next `install.sh` task after T555 |
| P18 | `--update`'s help line "never rewritten beyond its task rows" understates that the ledger file is rewritten | next `install.sh` task |
