# T805 — Apply ADR-016 (D1, D2) and W1 to W3, text pins, regenerate

**ID:** T805
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-157-confirmation-as-validity-condition.md` (task T805, § User decisions on ADR-016)
- `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md` (Accepted; § Files and lines this decision changes: rows D1 to D4, W1 to W3, and the table "Which record a test compares each text with")
- `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md` (row C1; superseded in part)

## 1. What and why

ADR-016 (Accepted by the user on 2026-11-12) makes the Security Engineer's confirming review a fourth validity condition of a "none possible in the harness" plan. The user also included the three wording-only fixes W1 to W3. Put the texts into the skill, pin them by test, and regenerate the mirrors and the registry.

## 2. Output

Commits on `agent/solution-architect/T804` (the plan's one branch), in the worktree `/home/emage/Code/emage/worktrees/agent-solution-architect-T804`:

1. **D1, D2, W1, W2**, `implementation/knowledge/skills/validation-gates/SKILL.md`, § Verdict Rules, the accepted-MEDIUM paragraph (line 70): apply the four rows exactly as ADR-016 gives them. **W3**, same file, § Gate Input Requirements (near line 120). Apply the texts verbatim; if grammar forces a change, stop and report it instead of rewording.
2. **D3, D4**: no edit. Confirm by reading `implementation/knowledge/agents/release-manager.md:183` that the Conditions line stays as it is.
3. **Pins**, `tests/functional/test_release_self_review_text.py`: follow ADR-016's table "Which record a test compares each text with". Split the whole-C1 comparison with ADR-015: the first sentence (now D1) and D2 compare with ADR-016; C1's second sentence compares with ADR-015 up to "tracked-debt register" and with ADR-016 row W1 for the parenthesis; C1's third sentence stays with ADR-015. ADR-015's own text must stay pinned (as `B3_LINE_ADR_012` does for ADR-012). Add named clauses for: "and only when", "before the user is asked", the citing duty after the semicolon, the consequence sentence ("any one of these four", "not a valid plan", "the acceptance does not hold"), D2 (later release, dated statement, for that release), W1's parenthesis, W2's "An acceptance covers", W3's "and its plan's deadline". Add a mutation per new clause in the file's existing style, including: confirmation moved back outside "only when"; "four" to "three"; D2 removed; W2 back to "It covers". Pin W2's sentence and the sentence "Only the user can accept it; no agent grants, extends or infers an acceptance" if no pin in this file holds them today (SEC-T802-02). Add ADR-016 to the file's header list.
4. **Other copies**: search `implementation/knowledge`, `docs/wiki` and `tests/functional` (with `--exclude-dir=held-out` for anything under `tests/`) for the superseded sentence and for "It covers only the release it was given for"; report each hit as pointer (no edit) or copy (edit the same way and say so). Do not edit anything under `tests/golden/`; if a golden fixture or case would now fail, stop and report it.
5. **Regenerate**: `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`; commit the generated changes separately from the source edits. Do not run `scripts/install.sh` and do not touch the top-level `.claude/`, `.github/`, `.opencode/`, `.cline/`, `.clinerules/` folders. Declare the root drift that `python3 -m tests.functional.test_root_install_parity --print-drift` reports in `tests/_baselines/root-install-drift.json`, with a note in the style of the existing ones (root not refreshed; a separate step that needs the user's approval at that moment).

## 3. Constraints

- Conventional Commits, each ending with `Co-Authored-By: Claude <noreply@anthropic.com>`. Do not push, do not merge, never create a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md`, any brief's Status line, any plan, or any ADR.
- `tests/golden/` is protected: change nothing under it. Never open `tests/golden/held-out/` and never write a held-out case id; recursive searches over `tests/` need `--exclude-dir=held-out`.
- No `docker` command. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never print a secret value. Do not read the CWSO repository.
- Functions of at most 50 lines and 4 parameters.
- Tests: run the files you touch and the gates below with a `timeout`. Do not run the full suite (the orchestrator does, in a clean worktree) and run no mutation tool; a mutation test inside the test file is fine.
- Do not delete anything under `/tmp` that you did not create; say what you created and removed.
- Token budget: 120k, counting context. Report your usage honestly.

## 4. Acceptance criteria

- `timeout 600 python3 -m unittest tests.functional.test_release_self_review_text` passes, and fails when any one new clause is removed from its source (by the mutation test in the file, not by leaving the source changed).
- These pass: `python3 docs/tasks/validate-tasks.py`; `timeout 300 python3 -m unittest tests.functional.test_link_integrity`; `python3 -m unittest discover -s tests -p 'test_team_health*.py'`; `python3 scripts/scorecard.py --check`; `node implementation/scripts/sync.mjs --root implementation --check`; `python3 implementation/scripts/generate-registry.py --check`; `python3 -m unittest tests.functional.test_root_install_parity`.
- `git status` is clean, and `git diff develop --stat` shows no path under `tests/golden/` or a top-level platform folder.
- The report lists: each commit; each other hit with pointer or copy; the root drift list; anything **(unverified)**; token usage.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`). After two failed attempts at the same step, stop and report.
