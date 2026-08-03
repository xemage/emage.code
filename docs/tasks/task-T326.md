# Task T326 — Plan-017 closing evidence pack (FINAL GATE)

**ID:** T326
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T318, T319, T320, and (if reached) T321-T325
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md

## Objective
Produce the single evidence pack proving plan-017's documentation-repair and (if reached)
registry-hardening claims are real, not asserted.

## Inputs
- Outputs of T318, T319, T320, T321-T325 (whichever were reached)

## Expected outputs
- This file's Execution notes containing every applicable check's literal output.

## Acceptance criteria
1. `make sync && make verify` → exit 0.
2. `python3 docs/tasks/validate-tasks.py` → exit 0.
3. `grep -c "deploy/local-dev" docs/deployment/README.md` → 0.
4. `test -f implementation/runtime/cwso/README.md` → exists.
5. `grep -rc "Not yet validated end-to-end" docs/deployment/{proxmox-lxc-guide,gcp-cloud-run-guide}.md`
   → 1 each.
6. IF Wave 5 was reached (T322 was READY and T323-T325 completed): additionally
   `docker compose -f deploy/docker-compose-t226.yml ps` → 4 services healthy/Up.
7. IF Wave 5 was NOT reached: state that explicitly as the plan's honest disposition — this is a
   valid, complete outcome for Waves 0-4, not a failure of this task. Do not claim Wave 5 is done
   if it isn't.
8. Complete the ledger lifecycle for every task actually finished (atomic 4-step). Leave any
   not-yet-reached Wave 5 tasks in `active-tasks.md` as `pending`/`blocked` with an honest note
   pointing back to T322's disposition.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03

### Closing evidence (all checks run and pasted below)

#### `make sync && make verify` → exit 0
```
Done - 505 files written.
OK - no drift across 505 files.
```

#### `python3 docs/tasks/validate-tasks.py` → PASS
```
TASK LEDGER: PASS (5 active, 162 completed)
```

#### `grep -c "deploy/local-dev" docs/deployment/README.md` → 0
```
0
```

#### `test -f implementation/runtime/cwso/README.md` → exists
```
-rw-r--r-- 1 emage emage 8099 Aug  3 implementation/runtime/cwso/README.md
```

#### `grep -rc "Not yet validated end-to-end" docs/deployment/{proxmox-lxc-guide,gcp-cloud-run-guide}.md` → 1 each
```
docs/deployment/proxmox-lxc-guide.md:1
docs/deployment/gcp-cloud-run-guide.md:1
```

### Wave 5 disposition

Wave 5 (T323-T325) was **NOT reached**. T322 found:
- `orchestrator`: published ✓
- `git-shadow`: published ✓
- `merge-engine`: NOT published ✗
- `rollout`: NOT published ✗

T323-T325 remain in `active-tasks.md` as `blocked`, waiting on CWSO's team to act on the T321
hand-off (T178/T179 in ../CWSO). This is the plan's honest, complete disposition for Waves 0-4.
No claim of Wave 5 completion is made.

### Summary

Plan-017 Waves 0-4 **COMPLETE AND VERIFIED**:
- Wave 0 (T317): Baseline recorded
- Wave 1 (T318, T319): Stale README fixed; Pattern A usage guide authored
- Wave 2 (T320): Disclaimer banners added to both unvalidated guides
- Wave 3 (T321): CWSO registry CI gap hand-off written into ../CWSO (T178/T179 task briefs + artifact + plan)
- Wave 4 (T322): NOT READY — Wave 5 blocked

**Status: DONE** (Waves 0-4 complete; Wave 5 deferred pending CWSO registry publication)
