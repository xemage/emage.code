# Command Promotion Readiness — measured baseline

**Version:** v1
**Date:** 2026-09-25
**Measured at:** `develop` @ `be053dc` (immediately after `T522` merged)
**Based on:** `docs/artifacts/maturity-promotion-criteria-v1.md` §3.1/§3.5 (as amended by `-v2`);
`docs/decisions/ADR-007-command-contract-authority.md`;
`docs/artifacts/command-contract-resolution-v1.md`;
`docs/plans/plan-064-roadmap-v8-breadth-and-utility.md` Phase 9.

## 1. Why this artifact exists

`checkpoint-036` lists "re-run command promotion readiness" as outstanding Phase 9 work, alongside
"14 unstarted golden cases for uncovered commands". The `14` was an estimate carried forward, never
a measurement. This artifact replaces it with a measurement.

## 2. Method

Every `command/*` component still at `maturity: experimental` was temporarily set to `stable` in a
throwaway detached worktree, `check-maturity.py --root implementation` was run, the per-component
failure reasons were recorded, and the worktree was discarded. Nothing was committed and no
protected path was touched — the probe edits only `implementation/knowledge/commands/*.md`, which is
not protected.

This is the same technique used to measure `T522` before executing it, and it is reproducible:

```
git worktree add /tmp/probe develop --detach
cd /tmp/probe
for f in implementation/knowledge/commands/*.md; do
  sed -i 's/^maturity: experimental$/maturity: stable/' "$f"
done
python3 implementation/scripts/check-maturity.py --root implementation
```

## 3. Result

**1 of 19 commands is `stable`** (`/security-audit`, promoted by `T522`). The remaining **18 split
cleanly into two groups, and no command is in both.**

### 3.1 Group 1 — blocked by criteria 3 + 7 (an open `tracked_defect` golden case): 4 commands

These commands **have** a golden case, so criterion 4 is satisfied. They fail because that case is
`known_failing` / `tracked_defect`.

| Command | Blocking case | `ADR-007` verdict | State |
|---|---|---|---|
| `/plan` | `plan-real-doc-header-drift` (`open/`) | **A** | Stays red by design — `ADR-007` branch 3b |
| `/prepare-release` | `prepare-release-real-verdict-missing` (`open/`) | **C** | Scoped as `T521`, not yet dispatched |
| *(held-out case, identity withheld)* | *(withheld)* | **H-1** | **Actionable now** — see §4 |
| *(held-out case, identity withheld)* | *(withheld)* | **H-2** | Stays red by design — `ADR-007` branch 3b |

Two of the four blocking cases live in `tests/golden/held-out/`. Their identity — including which
command each belongs to — is withheld here, following the precedent
`command-contract-resolution-v1.md` §H set deliberately, and enforced mechanically by
`tests/functional/test_golden_held_out_isolation.py` Check B, which fails the build on any mention
of a held-out case ID in a file outside `tests/golden/`.

**Only one of these four is actionable.** A and H-2 are `ADR-007` branch-3b outcomes: the corpus is
wrong, the corpus gets fixed, and the case stays failing until it is. Making them green would mean
reclassifying a real defect, which `ADR-007` §5 names explicitly as the thing not to do.

### 3.2 Group 2 — blocked *only* by criterion 4 (no golden case exists at all): 14 commands

```
/batch          /bug-report      /consolidate-memory  /discover-skills
/evaluate-poc   /handoff         /new-poc             /new-project
/poc-demo       /skillify        /sprint-status       /team-status
/validate-tasks /validate-workflow
```

Failure reason, identical for all 14:

```
beta->stable #4 (golden case for this command): no golden case (open/ or held-out/) with command: /<name>
```

**`checkpoint-036`'s estimate of 14 is exactly right**, and this is the first time it has been
confirmed rather than assumed. These 14 are Phase 9's larger pole, and none of them is blocked by a
defect — each is blocked by an absence. They also fail **no other criterion**: criterion 4 is the
sole blocker in every case, so authoring one golden case per command is sufficient, not merely
necessary.

## 4. The one actionable item

**`ADR-007` verdict H-1 is the only Group-1 case that can close without first fixing a corpus.**

Its contract conflict was already resolved: `T520` amended the command's declared filename format to
match `AGENTS.md` § Artifact Versioning, under `ADR-007` branch 1 (authority conflict → amend the
contract). What remains is that the case's `expect.py` still encodes the **pre-amendment** pattern,
so the case cannot flip no matter what the command says.

`T520` correctly refused to touch it: that file was not in `T520`'s §1 authorization table, and
`protected-paths-v1.md` §5.1 forbids the holding agent from extending its own grant. It therefore
needs a **new, named authorization** — scoped as `T523`.

`command-contract-resolution-v1.md`'s claim that H-1 "flips with no fixture change" is **correct
about the fixture and wrong about the checker**. The fixture needs nothing; the checker needs one
token.

## 5. Corrected expectation about agent promotion

A claim made earlier in this repo's session log — that H-1 was the nearer of the two remaining
agent promotions — is **wrong**, and this measurement is what corrects it. The two agents still at
`experimental` are blocked as follows:

| Agent | Blocking case | Verdict | Actionable? |
|---|---|---|---|
| `orchestrator` | `plan-real-doc-header-drift` (`/plan`) | **A** | No — branch 3b, stays red |
| `tech-lead` | *(held-out, identity withheld)* | **H-2** | No — branch 3b, stays red |

**H-1 unblocks a command, not an agent.** Neither remaining agent promotion is near, and neither is
blocked on an authorization — both are blocked on real corpus work that `ADR-007` deliberately
declined to shortcut. The agent category is expected to sit at 26/2 for as long as that work is
outstanding, and that is the correct reading of the ladder rather than a stall.

## 6. Ordered consequence for Phase 9

1. **`T523`** — execute H-1. Smallest remaining unit; takes commands to **2 of 19**.
2. **`T521`** — verdict C, already scoped. Does *not* by itself promote `/prepare-release`; it gives
   `## RELEASE VERDICT` a declared home, which is the corpus-side half of branch 3b.
3. **14 golden cases** — the real remaining bulk, now enumerated in §3.2 rather than estimated.
4. **A and H-2** — corpus fixes, no authorization needed, deliberately not shortcut.
