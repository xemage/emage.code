# Task T403 — Relocate CWSO deployment guides out of `docs/deployment/`

**ID:** T403
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-12
**Completed:** —
**Based on:** docs/plans/plan-035-roadmap-v7-ground-up.md (Phase 0, §2.4)

This brief is self-contained.

## Objective
`docs/deployment/` in the emage.code repo currently holds 7 files, 6 of which are full CWSO
deployment guides that do not belong in this repo — emage.code is a knowledge-projection layer,
not the CWSO orchestrator; deployment instructions for CWSO belong in the CWSO repo. Replace the
6 guides with a single `docs/deployment/README.md` that covers **usage only**: how and why an
emage.code user would use CWSO (what it is, when you'd reach for it, how emage.code talks to it),
linking out to the CWSO repo for actual deployment instructions.

## Confirmed current state (verified at brief-authoring time — re-verify before editing)
`docs/deployment/` contains exactly these 7 files:
- `README.md` — currently itself a full deployment hub (429 lines: environment comparison tables,
  install commands, troubleshooting, migration procedures, cost optimization, production
  checklists for Docker Desktop / Proxmox LXC / GCP Cloud Run). **This entire file needs to be
  replaced**, not merely trimmed — its current content is deployment instruction, which is exactly
  what this task removes.
- `local-docker-desktop-guide.md` — relocate
- `gcp-cloud-run-guide.md` — relocate
- `proxmox-lxc-guide.md` — relocate
- `cwso-overview-and-agent-integration-guide.md` — relocate
- `cwso-emage-orchestrator-connection-guide.md` — relocate
- `troubleshooting-guide.md` — relocate

## Coupling constraint — read before acting
Per `plan-035`'s §2.5 (Track C coupling points), **this task must not land before the CWSO repo
(Track C, task T473 there) is ready to receive the 6 relocated guides, or the guides are
orphaned.** This orchestrator run does not have T473 scheduled or executed — T473 is Track C
(CWSO repo) work, entirely out of scope for this Phase 0 run, and no evidence has been gathered
that the CWSO repo has a receiving location ready.

**Therefore, for this task, "relocate" means:**
1. Remove the 6 guide files from `docs/deployment/` in **this** repo (emage.code), since leaving
   deployment instructions for another system in this repo is exactly the drift this task exists
   to fix.
2. Do **not** silently discard their content — before deleting, copy the 6 files' full content
   into a location outside `docs/deployment/` that preserves them for hand-off, specifically
   `docs/archiv/cwso-deployment-guides-pending-t473-handoff/` (create this directory), with a short
   `README.md` inside it stating: these files were relocated out of `docs/deployment/` by T403
   (plan-035 Phase 0) and are staged here pending CWSO repo T473 (Track C, not yet scheduled)
   receiving them; once T473 lands in the CWSO repo, this staging directory should be deleted.
3. Since this is a staging/archive move, it is exempt from T400's version-consistency check (excluded
   path prefix `docs/archiv/`) — confirm your staged copies don't trip that check regardless.
4. This satisfies Phase 0's acceptance criterion ("`docs/deployment/` contains no deployment
   instructions for any target") without permanently destroying content ahead of the receiving
   side being ready — a deliberate, documented compromise given the coupling constraint above.

## Inputs
- All 7 files currently in `docs/deployment/` (read each fully before acting)
- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.5 — the three named coupling points between
  this repo and the CWSO repo (this task only concerns coupling point #1)

## Expected outputs
- `docs/deployment/README.md` — rewritten as a short, usage-only document. Suggested structure
  (adapt as needed, this is guidance not a rigid template):
  - What CWSO is, one paragraph, from an emage.code user's perspective
  - When you'd use it (e.g. CWSO permission tiers referenced in `docs/artifacts/
    role-mapping-cwso-v1.md`, concurrent multi-agent code-editing via shadow workspaces — consult
    that artifact and the `cwso-awareness` skill referenced in `AGENTS.md` for accurate framing,
    do not invent capabilities)
  - How emage.code connects to it (reference the MCP contract / `cwso` MCP server entry in
    `implementation/knowledge/mcp/servers.yaml` if present — check, don't assume)
  - A single link out: "for deployment instructions, see the CWSO repo" (use whatever the actual
    CWSO repo reference is elsewhere in this codebase, e.g. `/home/emage/Code/emage/CWSO` locally
    or its remote URL if documented — check `docs/wiki/mcp-servers.md` or similar for the
    canonical reference, don't fabricate one)
  - No install commands, no environment comparison tables, no troubleshooting steps, no migration
    procedures — all of that is deployment instruction and belongs in the CWSO repo, not here.
- `docs/deployment/local-docker-desktop-guide.md`, `gcp-cloud-run-guide.md`, `proxmox-lxc-guide.md`,
  `cwso-overview-and-agent-integration-guide.md`, `cwso-emage-orchestrator-connection-guide.md`,
  `troubleshooting-guide.md` — removed from `docs/deployment/`, staged (verbatim copy) under
  `docs/archiv/cwso-deployment-guides-pending-t473-handoff/` with the explanatory `README.md`
  described above.
- A grep sweep for any other file in this repo linking to the 6 relocated guides at their old
  `docs/deployment/<guide>.md` path — fix any broken link found (e.g. update to point at the new
  staged location, or remove the link if it's no longer appropriate) rather than leaving a
  dangling reference.

## Acceptance criteria
1. `docs/deployment/` contains no deployment instructions for any target (Docker Desktop, Proxmox,
   GCP) — only the new usage-only `README.md`.
2. No content is silently destroyed — the 6 guides' full text is preserved verbatim under
   `docs/archiv/cwso-deployment-guides-pending-t473-handoff/`.
3. `docs/deployment/README.md` contains zero install commands, zero environment-comparison tables,
   zero troubleshooting/migration procedures.
4. No dangling link anywhere in the repo points at a now-removed `docs/deployment/<guide>.md` path.
5. The staging directory's own `README.md` clearly states the pending-handoff nature and names
   T473 as the eventual receiving task, so a future reader (or the T403→T473 coupling check) isn't
   confused about why deployment guides live under `docs/archiv/`.

## Note on tooling access
Per `.claude/rules/security-guidelines.md`, you (Technical Writer) do not have Bash/git access.
Use Write/Edit for content changes; for the file moves (removing from `docs/deployment/`, creating
`docs/archiv/cwso-deployment-guides-pending-t473-handoff/`), draft the exact target file paths and
content and hand them to the orchestrator to execute the actual move/delete and commit, since that
requires filesystem operations beyond Edit/Write's create-or-modify-in-place model for a clean
directory relocation. State clearly in your completion report which files should be created,
which content goes where, and which original files should be deleted.

## Blocker protocol
- If you find `docs/deployment/README.md`'s current content contains information that is *not*
  deployment-instruction (e.g. a security consideration relevant to emage.code users specifically,
  not CWSO's deployment) — flag it, don't silently drop it; decide case-by-case whether it belongs
  in the new usage-only README or elsewhere.
- If no canonical CWSO repo reference/URL can be found anywhere in this codebase to link to —
  `type: unclear_requirements`, `severity: minor` — report and use a clearly-marked placeholder
  rather than fabricating a URL.

## Git workflow
Same shared branch as T400–T402: `feature/T400-phase0-ground-truth-v6.11.0`. Orchestrator executes
the file moves and commits with a Conventional Commit message, e.g.:
```
docs(deployment): relocate CWSO deployment guides out of this repo

docs/deployment/ held 6 full CWSO deployment guides that belong in
the CWSO repo, not emage.code. Replaced docs/deployment/README.md
with a usage-only doc; staged the 6 guides under
docs/archiv/cwso-deployment-guides-pending-t473-handoff/ pending
CWSO repo T473 (Track C) receiving them per plan-035 Sec 2.5's
coupling constraint.

Refs T403
```

## Constraints
- Token budget: ≤20k tokens.
- File ownership: `docs/deployment/*`, new `docs/archiv/cwso-deployment-guides-pending-t473-
  handoff/*`. Fix dangling links wherever found, but do not otherwise edit unrelated files.
