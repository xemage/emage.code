# T691 — Ruling: release self-review (P112-P41-O1)

**ID:** T691
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T687
**Affects:** —
**Created:** 2026-10-24
**Completed:** 2026-10-24
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-24: T691)
- The user's decisions of 2026-10-24 (replies to the decision list of `docs/artifacts/tracked-debt-register-v2.md` section 5.2): "O1 have the Solution Architect rule on it"
- `docs/artifacts/tracked-debt-register-v2.md` (P112-P41-O1), `implementation/knowledge/agents/orchestrator.md` (lines ~217 and ~259), `implementation/knowledge/agents/release-manager.md` (lines ~15 to 27), `implementation/knowledge/skills/validation-gates/SKILL.md` (~188), `docs/decisions/ADR-008-knowledge-document-authority.md`, the code review of the release v8 (`docs/artifacts/code-review-release-v8-v1.md`, SIGNOFF-CR649)

## 1. What and why

Rule on P112-P41-O1: the orchestrator delegates both the release preparation and the Release validation gate to `@release-manager`, so the same agent prepares and gates the release (a self-review). Read the three places and the authority rules of ADR-008 (step A or the P5 path named in the register), and write a ruling artifact `docs/artifacts/ruling-p112-p41-o1-release-self-review-v1.md` (immutable-artifact format, date, Based on): what the texts say today, the options (for example: keep and document; the Release gate verdict by a different reviewer such as `@tech-lead`/`@qa-engineer` or by the top-level session after its own verification, which is how releases are actually gated here; split preparation and gate in the role texts), the recommendation, exactly which lines of which knowledge files would change, and what it costs. **Decision artifact only; no knowledge edit**: if the ruling needs one, the orchestrator creates the follow-up task. The user asked the Solution Architect to rule; the user may overrule. *Acceptance:* the ruling artifact with the options, a recommendation and the lines to change.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

- This agent has no shell: write the artifact with the Write tool; the orchestrator commits it.
## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol


Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
