# T906 — TL-T753-05 shipped text

**ID:** T906
**Owner:** technical-writer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-21
**Completed:** 2026-11-21
**Based on:**
- `docs/plans/plan-198-tl-t753-05-root-refresh.md`
- The user's answer of 2026-11-21, verbatim: "Root refresh"

## 1. What and why

Fix TL-T753-05 as specified in plan-198 § Task Decomposition item 1.

## 2. Output

The edited knowledge-source files; a per-place report (old text, new text).

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release. No docker. Never open `tests/golden/held-out/`.
- Never edit `tests/golden/`, a published release document or a derived platform folder (`.claude`, `.cline`, `.github`, `.opencode`).
- Never read secrets or the user's settings files.
- Token budget: 40k.

## 4. Acceptance criteria

- Each of the five places says the script is this repository's maintainer tool and a target lacks it.
- No derived or immutable file edited.

## 5. Blocker protocol

Report each blocker with its type and severity.
