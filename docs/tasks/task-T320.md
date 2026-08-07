# Task T320 — Add "not validated end-to-end" banners

**ID:** T320
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T317
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md

## Objective
`docs/deployment/proxmox-lxc-guide.md` and `gcp-cloud-run-guide.md` have never been run against
real infrastructure — add an honest, explicit disclaimer so readers don't mistake them for
validated procedures (as `local-docker-desktop-guide.md` now is, per T313).

## Inputs
- `docs/deployment/proxmox-lxc-guide.md`, `docs/deployment/gcp-cloud-run-guide.md`
- `docs/tasks/task-T313.md` (contrast reference — the validated guide)

## Expected outputs
- Both files, with a banner inserted immediately after the title/header block.

## Acceptance criteria
1. Exact banner text inserted (substitute "Proxmox host" / "GCP project" per file):
   ```
   > **⚠️ Not yet validated end-to-end.** This guide was written from the original deployment plan
   > (`docs/plans/plan-013-cwso-deployment-guides.md`) but has not been run against a real
   > [Proxmox host / GCP project] since. Unlike `local-docker-desktop-guide.md` (validated and
   > corrected in `docs/tasks/task-T313.md`), no task in this repo's history confirms this guide
   > works as written. Treat it as a starting point, not a proven procedure, until a future task
   > validates it for real and removes this notice.
   ```
2. No other content in either file is rewritten in this task.
3. `grep -c "Not yet validated end-to-end" docs/deployment/proxmox-lxc-guide.md` → 1.
4. `grep -c "Not yet validated end-to-end" docs/deployment/gcp-cloud-run-guide.md` → 1.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03

Inserted `> **⚠️ Not yet validated end-to-end.**` blockquote banner immediately after each
file's metadata block (before the first numbered step / section):
- `docs/deployment/proxmox-lxc-guide.md` — banner says "Proxmox host"
- `docs/deployment/gcp-cloud-run-guide.md` — banner says "GCP project"

No other content in either file was changed.

### Verify output
```
grep -c "Not yet validated end-to-end" docs/deployment/proxmox-lxc-guide.md
1
```
```
grep -c "Not yet validated end-to-end" docs/deployment/gcp-cloud-run-guide.md
1
```

**Result: PASS**
