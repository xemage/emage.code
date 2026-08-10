# Task T385 — Time-boxed re-attempt to resolve Pi's MCP config format (P2)

**ID:** T385
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Depends on:** T381
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-09)

This brief is self-contained. You do not need to read plan-033 to execute this task, though you
should read `docs/tasks/task-T360.md`'s Pi row (cited in full below) so you don't repeat its
already-exhausted research approach.

## Objective
`implementation/platforms/pi.json`'s manifest sets `mcp.format: "cursor"`, meaning `sync.mjs`
generates `.pi/mcp.json` using the byte-identical code branch as Cursor's `.cursor/mcp.json`
(`{ "url": s.url }` for remote servers, no `"type"` field). T360's audit (plan-030) already tried to
confirm or refute this is actually correct for Pi and came back explicitly inconclusive — no
distinct, authoritative official "Pi" MCP config doc was found; the generator's choice is "inherited
from Cursor by analogy," not independently verified. This task gives that question exactly one more,
**differently-sourced** attempt (T360 did not use the `context7` MCP tool available in this
environment — that is the new angle for this attempt) and requires closing the question either way,
not leaving it open a third time.

## Inputs (read before starting)

**T360's exhausted approach (read-only reference — do not repeat this without a new angle):**
```
docs/tasks/task-T360.md, the "Pi" row of the audit table (search for
"Pi (`cursor` format reused verbatim, `pi.json`)"):

"Inconclusive — no distinct authoritative official 'Pi' MCP doc source located.
Checked docs/tasks/task-T046.md (only says 'Pi platform' with no identifying
product detail beyond the generic name; artifacts listed are internal repo
paths, not an external product reference), docs/decisions/ (grepped all ADRs
for 'pi' as a whole word — zero matches), and docs/wiki/quick-start.md (lists
Pi -> pi format id and .pi/ output dir alongside Gemini/Opencode/Claude Code
for instruction-file format, but gives no vendor URL or distinguishing
detail). A live web search for an official 'Pi' coding-agent/CLI product with
its own MCP config docs returned only unrelated third-party/community
projects (oh-my-pi, pi-mcp-adapter, pi-mcp-server, LobeHub listings) — none
is a first-party vendor doc for a product this repo's pi.json manifest can be
confirmed to target."
```
T360 used WebFetch/WebSearch against docs/decisions/, docs/tasks/, docs/wiki/quick-start.md, and
general web search. It did **not** use the `context7` MCP tool (per this session's own global
instructions: `context7` should be preferred over web search for library/CLI-tool documentation
lookups, and can resolve library identity/existence questions that a generic web search may miss).
This is your new angle — use `context7`'s `library`/`docs` lookup commands to attempt to resolve
what "Pi" (as referenced by `implementation/platforms/pi.json`'s `"pi"` platform id and `.pi/`
output directory) actually is, and whether it publishes MCP config documentation.

**Current generator state (read-only reference):**
`implementation/platforms/pi.json`'s `mcp` field: `{"tags": ["core", "extended"], "outputFile":
"mcp.json", "format": "cursor"}` — the `"format": "cursor"` value is what you may change, ONLY if
your research finds a confirmed, cited, distinct correct format for Pi.

`implementation/scripts/sync.mjs`'s `emitMcp()` function currently has branches for `vscode`,
`cursor` (shared with `pi` via the manifest, not a separate `pi` branch), `gemini`, `opencode`,
`claude-code`, `cline` — re-read the current function (search for `function emitMcp`) to get exact
current line numbers before making any change; they are not restated here since T385's outcome
determines whether you touch this file at all.

## Time-box
**60 minutes of active research**, or 3 distinct new-angle attempts (context7 lookup, plus up to 2
follow-up searches informed by whatever context7 returns), whichever comes first. State your actual
elapsed effort/attempt count in your task report. Do not exceed this — if inconclusive at the
time-box, stop and record the "inconclusive, closed" outcome per Step 3 below rather than continuing
to search.

## Allow-list (files you may touch)
- **If, and only if,** your research within the time-box confirms a distinct, correct, cited MCP
  config format for Pi that differs from Cursor's:
  - `implementation/scripts/sync.mjs` — add a new `pi`-specific branch to `emitMcp()` (or correct
    the existing shared branch, whichever is structurally appropriate given what you find).
  - `implementation/platforms/pi.json` — change `mcp.format` from `"cursor"` to the new distinct
    value your `emitMcp()` change introduces.
  - Regenerated `implementation/.pi/mcp.json` (produced only via
    `node implementation/scripts/sync.mjs --root implementation`, never hand-edited).
- **In either outcome (fix found, or still inconclusive):**
  - `docs/wiki/mcp-servers.md` — update the existing Pi row in the "Remote-server transport encoding
    differs per platform" table (added by T364) to record your finding and decision, whichever it
    is.
  - `implementation/platforms/pi.json` — add or update an inline comment recording the decision and
    reasoning, even if `mcp.format` itself doesn't change (JSON has no native comment syntax; if
    `pi.json` has no existing precedent for comments, do NOT invent one — record the decision in
    `docs/wiki/mcp-servers.md` only, and note in your task report that `pi.json` was left unannotated
    because JSON manifests in this repo carry no comment convention).

## Deny-list (do not touch — no exceptions)
- Do NOT change any other platform's `emitMcp()` branch (`vscode`, `gemini`, `opencode`,
  `claude-code`, `cline`) or any other platform's manifest.
- Do NOT change `pi.json`'s `mcp.format` (or any other field) without a confirmed, cited source
  backing the new value — an inconclusive result must leave `mcp.format: "cursor"` exactly as-is.
- Do NOT regenerate any platform tree other than `.pi/` if you do make a `sync.mjs` change (run
  `node implementation/scripts/sync.mjs --root implementation` as usual — it will only produce a
  diff for `.pi/mcp.json`'s content if your change is correctly scoped to the `pi` branch alone;
  confirm this with `git diff --stat` after regenerating, and treat any other file changing as a
  sign your `emitMcp()` change leaked into a shared branch incorrectly).
- Do NOT edit any other row of the "Remote-server transport encoding differs per platform" table in
  `docs/wiki/mcp-servers.md` beyond the Pi row.
- Do NOT create any new branch beyond the one specified in Git workflow below.

## Step 1 — Research within the time-box
Use `context7`'s CLI (`npx ctx7@latest library "<candidate name>" "MCP configuration"` and similar)
to attempt to identify the specific "Pi" product `implementation/platforms/pi.json` targets and
whether it has MCP config documentation. Try reasonable candidate names (e.g. "Pi", "pi.dev",
whatever this repo's own docs suggest as the fuller name — T360 found `docs/wiki/quick-start.md`
references "Pi" without a vendor URL; also check `implementation/PREREQUISITES.md`'s per-platform
requirement row for Pi, which lists a candidate URL — read it fresh, do not trust T360's or this
brief's memory of it, it may have changed). Record every distinct search/lookup attempt and its
result (even "no match found") — your task report must show your work, not just a conclusion.

## Step 2 — Decide
- **If a confirmed, cited, authoritative source is found** describing Pi's actual MCP config shape,
  and it differs from Cursor's `{ "url": s.url }` (no `"type"`) shape: implement the fix (see
  Allow-list), regenerate, verify no other platform's output changed, and record the citation.
- **If a confirmed, cited, authoritative source is found** and it happens to confirm Cursor's shape
  IS correct for Pi after all (i.e. `"format": "cursor"` was right all along, now provably so rather
  than by unverified analogy): make no code change, but record the citation in
  `docs/wiki/mcp-servers.md`'s Pi row, upgrading its current "not independently verified" language to
  a cited confirmation.
- **If still inconclusive** after the full time-box: make no code change. Record in
  `docs/wiki/mcp-servers.md`'s Pi row an explicit, reasoned decision to KEEP the `cursor`-format
  assumption, with the reasoning stated (e.g. "no authoritative source found after two independent
  research attempts (T360's web search, T385's context7 lookup); retaining the Cursor-format
  assumption as the least-risky default since it's the only remote-transport shape that has never
  been found stale for any platform sharing it, and changing to a guessed alternative would introduce
  new unverified risk rather than remove existing unverified risk"). This is a closed decision, not
  an open question — do not phrase it as "still needs investigation."

## Step 3 — Update docs/wiki/mcp-servers.md's Pi row
Regardless of outcome, the Pi row in the "Remote-server transport encoding differs per platform"
table must be updated to reflect a CLOSED decision (not "no independently-confirmed official Pi MCP
doc has been located... treat this row as... not independently verified," which is the current
open-question phrasing). Replace it with either a cited-confirmation or an explicit
kept-by-reasoned-decision statement per Step 2's two closing outcomes.

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. IF you changed `sync.mjs`/`pi.json`:
   ```
   node implementation/scripts/sync.mjs --root implementation
   git diff --stat
   ```
   PASS = only `.pi/mcp.json`-related files under `implementation/.pi/` changed (plus your
   `sync.mjs`/`pi.json` source edits) — no other platform's generated output changed.
   ```
   node implementation/scripts/sync.mjs --root implementation --check
   ```
   PASS = drift-free after your own regeneration (re-running produces no further diff).

2. Markdown link check on your `docs/wiki/mcp-servers.md` edit — same script as T384 test 1:
   ```
   python3 -c "
   import re
   text = open('docs/wiki/mcp-servers.md', encoding='utf-8').read()
   for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
       url = m.group(2)
       if url.startswith(('http://', 'https://', 'mailto:', '#')):
           continue
       print('local link to check manually:', url)
   "
   ```

3. Full verification bar:
   ```
   make verify
   python3 implementation/scripts/generate-registry.py --root implementation --check
   python3 docs/tasks/validate-tasks.py
   python3 tests/run.py
   ```
   PASS = all four exit 0 per the standard conditions documented in prior briefs.

## Acceptance criteria (all must be true)
- [ ] Research was genuinely time-boxed (task report states elapsed effort/attempt count) and used
      at least one angle T360 did not try (`context7`) — not a repeat of T360's exact web-search
      approach with no new information source.
- [ ] The question is closed with a recorded decision either way (Step 2/3) — the Pi row in
      `docs/wiki/mcp-servers.md` no longer reads as an open question.
- [ ] If a code change was made: `emitMcp()`'s change is scoped to Pi only (test 1's `--stat` check);
      regeneration is drift-free after your own run; the change is backed by a cited source stated
      in both the commit message and the doc update.
- [ ] If no code change was made: `pi.json`'s `mcp.format` is unchanged; the doc update states the
      reasoned decision to keep it, not an open question.
- [ ] The full verification bar passes.
- [ ] No other platform's `emitMcp()` branch, manifest, or generated output changed.

## Blocker protocol
This task's nature (a research task with an explicitly time-boxed, closeable-either-way outcome)
means most "no confirmed source found" results are NOT blockers — they are the expected, acceptable
Step 2 "still inconclusive" outcome. Only STOP and report an actual blocker if:
- The current `implementation/platforms/pi.json`'s `mcp` field doesn't match what's quoted above
  (format already changed by a prior task, outputFile different) → `type: dependency`, `severity:
  minor` — re-verify against the current file before proceeding.
- You believe a code change is warranted but implementing it would require touching a shared
  `emitMcp()` branch other platforms also use, with no way to cleanly isolate a Pi-only path →
  `type: technical`, `severity: minor` — report the structural conflict; do not force a shared-branch
  edit that risks other platforms' output.
- Any verification command fails → `type: technical`, `severity: major`, include exact output.

Max 2 retries before escalating to the orchestrator with full context (only for a genuine blocker —
an inconclusive research result within the time-box is not a blocker, it's a valid Step 2 outcome).

## Git workflow
Branch name depends on your Step 2 outcome — decide before creating the branch:
- If your research produces a confirmed code fix: create `bugfix/T385-pi-mcp-format-fix` from the
  current tip of `develop`.
- If the outcome is a documented decision only (no code change, matching either "kept by reasoned
  decision" or "confirmed correct as-is"): create `chore/T385-pi-mcp-format-decision` from the
  current tip of `develop`.

1. Create the appropriate branch per the above.
2. Do the research (Step 1), decide (Step 2), update the doc (Step 3), and make a code change only
   if warranted. Run all tests above; confirm all pass.
3. Commit with a Conventional Commit message matching your branch's type, e.g. (code-fix case):
   ```
   fix(mcp): correct Pi's MCP remote-transport encoding

   T360's plan-030 audit left Pi's format inconclusive (no authoritative
   doc found; sync.mjs reused Cursor's branch by analogy). Re-attempted
   via context7, found <cited source>, confirming Pi's actual shape is
   <shape>. Added a distinct pi branch to emitMcp(), updated pi.json's
   mcp.format, regenerated implementation/.pi/mcp.json. No other
   platform's output changed. Closes the question T360 left open.

   Refs T385
   ```
   or (decision-only case):
   ```
   chore(mcp): close Pi's MCP format question with a documented decision

   T360's plan-030 audit left Pi's format inconclusive. Re-attempted via
   context7 (a new angle T360 did not use) within a 60-minute time-box;
   still no authoritative official "Pi" MCP doc source found. Recorded an
   explicit, reasoned decision in docs/wiki/mcp-servers.md to keep the
   cursor-format assumption rather than leave the question open a third
   time. No code change (pi.json's mcp.format unchanged).

   Refs T385
   ```
4. Push the branch, open a merge request to `develop` referencing T385, wait for CI to go green,
   then STOP — do NOT merge yourself. Report completion to the orchestrator for independent
   re-review and merge.
5. Do NOT push to `develop` or `main` directly under any circumstance.

## Constraints
- Token budget: ≤8k tokens.
- File ownership: `docs/wiki/mcp-servers.md` (Pi row only), and conditionally
  `implementation/scripts/sync.mjs` + `implementation/platforms/pi.json` + regenerated
  `implementation/.pi/mcp.json`, only if a confirmed fix is found.
- No unrelated refactor of any file.
