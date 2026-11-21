# plan-198 — TL-T753-05: shipped text that names a script a target lacks, then a root refresh

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v33.md` (§ 5 batch Y, § 7);
- `docs/artifacts/release-v10-audit-v1.md` (the audit's list of places) and `docs/releases/v10.0.0.md` (K-33; immutable, not edited).

**Scopes:** `T906`, `T907`.

## User decision (2026-11-21, verbatim)

> Root refresh

(The user said this right after the v33 report, which named the root refresh for TL-T753-05 as the open optional step. Root drift is empty apart from the user's own uncommitted `.vscode/mcp.json`, so the refresh has content only after the source fix below.)

## Task Decomposition

1. **T906** (technical-writer): reword the five places in the knowledge sources that tell a target to run `scripts/verify-release-docs.py`, which exists only in this authoring repository. Say that it is this repository's maintainer script and that a target does not have it. Change no command line that this repository uses for itself.
   - `implementation/knowledge/agents/orchestrator.md` (Release Documentation Gate, about lines 132, 135, 136);
   - `implementation/knowledge/skills/verification-before-completion/SKILL.md` (about lines 63 and 86);
   - `implementation/docs/wiki/home.md` (about line 25) and `implementation/docs/wiki/README.md` (about line 15), the seeded wiki pages;
   - check `implementation/knowledge/commands/prepare-release.md` (already `audience: authoring`) and `skills/release-workflow/SKILL.md` and leave them if they already say it.
   - No shell: the writer does not commit. The orchestrator commits, regenerates the mirrors, runs the gates and the tests.
2. **T907** (orchestrator): in a second merge request, after T906 is merged, run the root refresh (`scripts/install.sh --update`, as in T793), check the drift is `[]` and that `.vscode/mcp.json`, `.claude/settings*.json` and `.vscode/settings.json` are untouched.

## Constraints

- No `docker`. No push, merge, tag or release by an agent.
- Never read secrets or the user's settings files. Never open `tests/golden/held-out/`. Never edit `tests/golden/`, a published release document, an immutable `-vN` artifact or a derived platform folder by hand.
- Do not write a link-like text with a parenthesis in the target in prose.
- Budget: T906 40k.

## Approval

- [ ] Approved by the user

## Outcome (2026-11-21)

- T906 done: nine edits in six knowledge-source files (no shell for the writer; the orchestrator committed).
- T907 was folded into the same merge request, because the user's word "Root refresh" was the approval for the refresh: `sync.mjs` and `generate-registry.py` regenerated the mirrors (14 mirror files plus `registry/index.json`), then `scripts/install.sh --projections-only` refreshed the root. 14 derived root files changed (`.claude`, `.cline`, `.github`, `.opencode`); `--print-drift` is `[]` in the merge-request tree; no settings file, MCP config or user-local file was touched.
- TL-T753-05 is fixed; the register records it in v34. TL-T753-06 (the manifest `files` list) is not part of this plan.
