# plan-086 — Round close: T538, T555 archived; three items parked

**Created:** 2026-10-01
**Based on:** MRs !427, !429; T538 (finished by the orchestrator); `docs/plans/plan-085-index-leak.md`.
**Scopes:** none new. T554 remains the one active row.

## 1. Closed

- **T555 (P1, security)** — the installer could copy this repository's memory index into client projects
  on rsync-less hosts. Fixed in both `cp` fallbacks; 0 of 2,000 fuzz cases now disagree with real `rsync`.
- **T538** — `/team-status` gained the missing `in_review` colour and a `Color code:` bullet, now
  identical to `/sprint-status`. Its agent was stopped by a user interrupt before handing back; at the
  user's choice the orchestrator finished it, treating the leftover worktree as raw material.

## 2. Parked, with triggers (decision 3 of `plan-083`)

| # | Item | Found by | Trigger |
|---|---|---|---|
| P19 | `dependency-graphing` skill colours lifecycle states with `in_progress` blue and `in_review` yellow — swapped relative to both status commands (`in_progress` yellow, `in_review` blue). The same colour means opposite states depending on the tool. | T538 | next knowledge batch |
| P20 | `docs/tasks/__pycache__/` ships on every fresh install — the `docs/` copy passes no excludes (minor; no absolute path in the current `.pyc`) | T555 | next `install.sh` task (with P17, P18) |
| P21 | File-versus-directory type conflicts still fail loudly under the `cp` fallback where `rsync` replaces the path (26/300 fuzz cases, down from 58) | T555 | next `install.sh` task |

The full parked set is now P4–P21 (P1–P3 promoted to rows and closed or in flight). Every checkpoint
must enumerate it.

## 3. Next

- **T554** (QA Engineer) — the `/discover-skills` repair, the last open `plan-083` §1 commitment. The
  knowledge group is now free, so it dispatches immediately.
- **`plan-082` §2** — the one human-approved repo-root refresh. It should run when no open task edits
  `implementation/knowledge/`; T554 does, so it follows T554. The declared drift list is 86 paths.
