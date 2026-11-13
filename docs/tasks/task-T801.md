# T801 — Apply ADR-015 (C1, C2), text pins, regenerate

**ID:** T801
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-156-apply-adr-015.md` (task T801, § Facts)
- `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md` (§ Decision; § Files and lines, rows C1 to C4)
- `docs/decisions/ADR-012-medium-acceptance-record.md` (rows B1, B3; § Validation)

## 1. What and why

ADR-015 (Accepted by the user on 2026-11-12) adds two rules to the accepted-MEDIUM procedure. Put them into the two knowledge sources it names, pin the new text by test, and regenerate the mirrors and the registry.

## 2. Output

Commits on `agent/backend-developer/T801`, in the worktree `/home/emage/Code/emage/worktrees/agent-backend-developer-T801`:

1. **C1**, `implementation/knowledge/skills/validation-gates/SKILL.md`, § Verdict Rules, the paragraph that opens with "**Security findings never qualify for CONDITIONAL_PASS, except one graded medium as stated below.**": add ADR-015's C1 text after the owner-change sentence, in the same paragraph. You may adjust wording for grammar, but not the rule, and every element of the rule must stay: the three conditions; the closer may be the user; the Security Engineer's review confirms and the question cites it; the review date is the deadline with no other limit than being still ahead at shipping; the owner records the outcome in the tracked-debt register on that date; a passed deadline (after an earlier release or before this one ships) is cured by the user's new, dated acceptance with a new plan and a deadline still ahead; the Conditions line says the old deadline passed and names its date and the release of the old acceptance.
2. **C2**, `implementation/knowledge/agents/release-manager.md`, the Conditions line under "### Conditions (if CONDITIONAL_PASS)": the two insertions ADR-015 gives, in the `mitigation=[...]` and `deadline=[...]` slots.
3. **Pins**, `tests/functional/test_release_self_review_text.py`: update `B3_LINE` and its clause map for C2; add clause pins for C1 in the B1 paragraph (one named clause per element listed in item 1) and for C2's two insertions. Follow the file's existing style (constants, clause maps, a mutation test per clause if the file has them for B1/B3). Add ADR-015 to the file's header list.
4. **The other hits** named in plan-156 § Facts: read each, and report for each whether it is a pointer (no edit) or a copy of the rule (then edit it the same way and say so). C3 and C4 need no edit per ADR-015; confirm by reading `security-engineer.md` (SLA paragraph) and `release-manager.md` (Release Gate Policy item 2).
5. **Regenerate**: `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`; commit the generated changes separately from the source edits. Do not run `scripts/install.sh` and do not touch the top-level `.claude/`, `.github/`, `.opencode/`, `.cline/`, `.clinerules/` folders; report the root drift that `python3 -m tests.functional.test_root_install_parity --print-drift` prints, and declare it the way earlier tasks did if a test requires a declaration (look at how T790 or T779 declared drift; say what you did).

## 3. Constraints

- Conventional Commits, each ending with `Co-Authored-By: Claude <noreply@anthropic.com>`. Do not push, do not merge, never create a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md`, any brief's Status line, or any ADR.
- `tests/golden/` is protected: change nothing under it. Never open `tests/golden/held-out/` and never write a held-out case id; recursive searches over `tests/` need `--exclude-dir=held-out`.
- No `docker` command. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never print a secret value. Do not read the CWSO repository.
- Functions of at most 50 lines and 4 parameters.
- Tests: run the files you touch and the gates below with a `timeout`. Do not run the full suite (the orchestrator does, in a clean worktree) and run no mutation tool; a mutation test inside the test file is fine.
- Do not delete anything under `/tmp` that you did not create; say what you created and removed.
- Token budget: 120k, counting context. Report your usage honestly.

## 4. Acceptance criteria

- `timeout 600 python3 -m unittest tests.functional.test_release_self_review_text` passes, and fails when any one new clause is removed from its source (show this for at least the C2 insertions and two C1 clauses, on a copy or by a test in the file, not by leaving the source changed).
- These pass: `python3 docs/tasks/validate-tasks.py`; `timeout 300 python3 -m unittest tests.functional.test_link_integrity`; `python3 -m unittest discover -s tests -p 'test_team_health*.py'`; `python3 scripts/scorecard.py --check`; `node implementation/scripts/sync.mjs --root implementation --check`; `python3 implementation/scripts/generate-registry.py --check`.
- `git status` is clean, and `git diff develop --stat` shows no path under `tests/golden/` or a top-level platform folder.
- The report lists: each commit; each of the other hits with pointer or copy; the root drift list; anything **(unverified)**; token usage.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`). If a golden case or scorecard baseline fails because of the new text, stop and report; do not edit the fixture or the baseline.
