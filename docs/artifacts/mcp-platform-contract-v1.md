# MCP Platform Contract — v1

**Status:** Proposed (author-only; not yet independently reviewed).
**Based on:** `implementation/knowledge/mcp/servers.yaml` (canonical server registry, read in
full); `implementation/platforms/claude-code.json`, `cline.json`, `cursor.json`, `gemini.json`,
`github.json`, `opencode.json`, `pi.json` (all 7 read directly, not summarized from a prior
source); `implementation/scripts/sync.mjs` (`emitMcp()` and the `manifest.mcp` handling block in
`syncPlatform()`, read in full); `scripts/merge-mcp-json.py` (module docstring and
`prune_names_recursive`, read in full); `AGENTS.md` §"MCP Servers" (cross-checked, not treated as
primary source); `docs/wiki/mcp-servers.md` (T384/plan-033, cross-checked for platform-list and
path agreement); `docs/plans/plan-037-phase2-phase5-sequencing.md` (source of the kickoff finding
adjudicated in §5); `docs/tasks/task-T420.md` (this task's own brief and the orchestrator's
pre-dispatch finding, independently re-verified below, not taken on faith).
**Owner:** solution-architect
**Consumers:** T421 (re-scoping — needs this contract to adjudicate defect vs. intended
behavior), T422 (conformance test — needs this contract to define "correct" per platform).

## 1. Method

Every claim below was derived by direct inspection of the four source files listed in "Based on,"
cross-referenced against the live, on-disk generated output for all 7 platforms (`.mcp.json`,
`.cline/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`,
`.pi/mcp.json`, `.vscode/mcp.json`) and their `<file>.provenance.json` sidecars where present. For
each platform, `emitMcp()`'s code path for that platform's declared `format` was traced by hand
against `servers.yaml`'s 15 server entries and diffed, key-for-key, against the corresponding
on-disk output file. Every one of the 7 platforms' on-disk MCP file matched its manifest's
declared `tags`/`format`/`outputFile` exactly; no content discrepancy was found in this manual
trace for any of the 7 files (see §4 for the one non-content anomaly found: a missing provenance
sidecar).

**A material limitation on evidence for acceptance criterion 2, disclosed up front rather than
glossed over:** this task session was not provisioned with a shell/Bash execution tool — only
file-read/write and web-fetch tools were available. `node scripts/sync.mjs --check` could
therefore **not** be executed live in this session, despite the task brief's explicit instruction
to run it. §5 states plainly what evidence stands in its place (an exhaustive manual byte-level
diff of `emitMcp()`'s per-format output against every on-disk file) and what remains unconfirmed
as a result. This is flagged as a blocker to the orchestrator in the completion report; it does
not block delivery of this document, since the manual diff is complete and traceable, but it is
not the same evidentiary class as a command transcript and should not be represented as one.

## 2. Server registry summary (`servers.yaml`)

15 servers total: 7 tagged `core` (`gitlab`, `playwright`, `fetch`, `memory`,
`sequential-thinking`, `brave`, `context7`), 8 tagged `extended` (`hf-mcp-server`, `filesystem`,
`github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`). Two servers use
`transport: remote` (`context7`, `hf-mcp-server`); the other 13 use `transport: stdio`.

**Note on `servers.yaml`'s own header comment (lines 3–7):** it lists only 4 of the 7 real
projection targets (`.vscode/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`,
`.cursor/mcp.json`) — it omits `.mcp.json` (claude-code), `.cline/mcp.json`, and `.pi/mcp.json`.
This is a stale/incomplete comment, not a functional defect (the manifests and `emitMcp()` are the
actual source of truth and are complete); noted here so T421 doesn't need to re-discover it.

## 3. Per-platform contract table

All 7 output paths below are relative to the repo root and were confirmed against
`implementation/platforms/*.json`'s `mcp.outputFile` resolved against `mcp.outputDir`
(`path.resolve(outRoot, manifest.mcp.outputFile)` in `sync.mjs`), not assumed from convention.

| Platform | Manifest file | Output path (repo-root-relative) | `mcp.format` | Tags included | Servers in scope |
|---|---|---|---|---|---|
| `claude-code` | `claude-code.json` | `.mcp.json` (via `outputDir: .claude`, `outputFile: ../.mcp.json`) | `claude-code` | `core` + `extended` | all 15 |
| `cline` | `cline.json` | `.cline/mcp.json` | `cline` | `core` + `extended` | all 15 |
| `cursor` | `cursor.json` | `.cursor/mcp.json` | `cursor` | `core` + `extended` | all 15 |
| `gemini` | `gemini.json` | `.gemini/settings.json` | `gemini` | `core` + `extended` | all 15 |
| `github` | `github.json` | `.vscode/mcp.json` (via `outputDir: .github`, `outputFile: ../.vscode/mcp.json`) | `vscode` | `core` **only** | 7 core servers |
| `opencode` | `opencode.json` | `.opencode/opencode.json` | `opencode` | `core` + `extended` | all 15 |
| `pi` | `pi.json` | `.pi/mcp.json` | `cursor` (pi's manifest literally declares `"format": "cursor"` — it reuses the Cursor wire shape verbatim, not a distinct `pi` format; confirmed by `pi.json` line 30 and by the fact `.pi/mcp.json` and `.cursor/mcp.json` are byte-identical in `mcpServers` shape) | `core` + `extended` | all 15 |

### 3.1 Wire-shape detail per format (from `emitMcp()`, `sync.mjs` lines ~293–378)

| `format` | Wrapper key | Stdio server shape | Remote server shape |
|---|---|---|---|
| `claude-code` | `mcpServers` | `{ command, args, env? }` | `{ type: "http", url }` |
| `cline` | `mcpServers` | `{ command, args, env? }` | `{ type: "streamableHttp", url }` |
| `cursor` | `mcpServers` | `{ command, args, env? }` | `{ url }` (no `type` field) |
| `gemini` | `mcpServers` (plus a top-level `hooks.AfterTool` block, unrelated to MCP) | `{ command, args, env? }` | `{ httpUrl }` (note: different key name, not just shape) |
| `vscode` (github) | `servers` | `{ command, args, env? }` | `{ type: "http", url }` |
| `opencode` | top-level `mcp` (plus `$schema` and an `instructions` array from `manifest.mcp.extraFields`) | `{ type: "local", command: [cmd, ...args], environment? }` | `{ type: "remote", url }` |

`env`/`environment` values are emitted as platform-native placeholder templates
(`${env:VAR}` for claude-code/cline/cursor/gemini/vscode, `{env:VAR}` for opencode) via
`mapEnv()` — never interpolated to a real secret value at generation time, consistent with
`security-guidelines.md`.

### 3.2 Explicit per-platform server enumeration

**`core` + `extended` platforms** (`claude-code`, `cline`, `cursor`, `gemini`, `opencode`, `pi`) —
all 15 servers appear: `gitlab`, `playwright`, `fetch`, `memory`, `sequential-thinking`, `brave`,
`context7`, `hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`,
`toolradar`. Confirmed by direct read of `.mcp.json`, `.cline/mcp.json`, `.cursor/mcp.json`,
`.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json` — each lists exactly these 15
top-level server keys, no more, no fewer.

**`core`-only platform** (`github`) — exactly 7 servers appear: `gitlab`, `playwright`, `fetch`,
`memory`, `sequential-thinking`, `brave`, `context7`. Confirmed by direct read of
`.vscode/mcp.json`'s `servers` object: it contains precisely these 7 keys plus one additional,
non-generator key (`cwso`) addressed in §4. None of the 8 `extended`-tagged servers
(`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`)
appear.

## 4. Known non-generator content (single-file merge targets)

`.vscode/mcp.json` and `.mcp.json` are the two single-file MCP targets in this repo (as opposed to
the 5 directory-tree platforms whose MCP file lives inside an otherwise-generated platform
directory). Per `scripts/merge-mcp-json.py`'s module docstring, these two files are not simply
overwritten on `scripts/install.sh --update`; they are merged: keys present in the generated
source always win on conflict, keys present only in the existing dest file are preserved as
hand-added content, and a `<file>.provenance.json` sidecar (recording the generator-owned key set
at each generation) lets a later `--update` distinguish a genuinely-retired generator key (safe to
prune) from a hand-added key (never pruned).

- **`cwso` in `.vscode/mcp.json` is exactly this precedent.** It is not present in
  `servers.yaml` at all, and its shape (`url`, `headers.Authorization` with a `${input:...}`
  prompt-string placeholder, and a top-level `inputs` array entry) is not something `emitMcp()`'s
  `vscode` branch produces. It is dest-only, hand-added content, preserved by design. **T421/T422
  should not flag `cwso` as a generator conformance gap** — it is intentional, documented
  (`merge-mcp-json.py` docstring + `prune_names_recursive`) non-generator content, consistent with
  the orchestrator's pre-dispatch finding.
- `.mcp.json` (claude-code) currently has no dest-only content beyond the 15 generator-owned
  keys — its `.mcp.json.provenance.json` sidecar's `generatorOwnedKeys` (15 entries, core +
  extended) matches its live content exactly, with nothing extra.

**A provenance-sidecar anomaly found independently, not part of the plan-037 claim, worth flagging
for T421/T422:** `sync.mjs`'s `syncPlatform()` writes a `<outputFile>.provenance.json` sidecar
unconditionally for every platform with an `mcp` block (the code is not conditioned on
single-file-vs-tree or on format). Direct `Read` confirms this sidecar exists and is populated
(15 `generatorOwnedKeys`) for 6 of the 7 platforms — `.mcp.json.provenance.json`,
`.cline/mcp.json.provenance.json`, `.cursor/mcp.json.provenance.json`,
`.gemini/settings.json.provenance.json`, `.opencode/opencode.json.provenance.json`,
`.pi/mcp.json.provenance.json` all exist in this worktree. **`.vscode/mcp.json.provenance.json`
does not exist** in this worktree (confirmed by two separate `Read` attempts, both returning "File
does not exist"). Two candidate explanations, neither of which this session could fully resolve
without shell access:
  1. `.vscode/*` is excluded from version control by this repo's own root `.gitignore`
     (`.vscode/*` ignored, with only `extensions.json` and `settings.example.json` explicitly
     allowlisted back in — `.gitignore` lines 52–55). If `.vscode/mcp.json` and its sidecar are
     genuinely untracked, then what this worktree shows for `.github`'s projection target is local
     filesystem state from whatever last populated this specific worktree (e.g., a prior partial
     `sync.mjs` run, or manual seeding), not necessarily identical to what `git worktree add`
     alone would produce from a clean `develop` checkout — worktrees do not inherit another
     checkout's ignored files.
  2. Alternatively, the sidecar could have been deleted or never written by whatever process most
     recently populated `.vscode/mcp.json` in this worktree, independent of git-tracking status.
- **This does not change §5's adjudication of the plan-037 `brave`/`context7`/`cwso` claim** (that
  claim was about tag misclassification and about `cwso`, both independently confirmed false/
  non-issue below on their own terms). It is a separate, narrower finding about sidecar-file
  parity that T421/T422 should verify with a live `node scripts/sync.mjs --check` (which this
  session could not run) and, if confirmed, either explain (e.g., "`.vscode/` is intentionally
  gitignored and its provenance sidecar is regenerated only by a local `--update`, so a missing
  sidecar in a fresh worktree is expected, not a defect") or file as a real gap for T421 to fix.

## 5. Adjudication of the plan-037 `brave`/`context7`/`cwso` finding

**plan-037's original claim:** `.vscode/mcp.json` over-includes `brave` and `context7` because
they are tagged `extended` in `servers.yaml`, which should exclude them from the `github`
platform.

**Independent re-verification performed in this session, from primary sources:**

1. `implementation/knowledge/mcp/servers.yaml` line 50–56 (`brave`) and line 58–61 (`context7`)
   both read directly: both are tagged `[core]`, not `extended`. **plan-037's premise is false at
   the source-of-truth level** — there is no `extended` tag on either server for this to have
   over-included on.
2. `implementation/platforms/github.json` line 30 reads `"tags": ["core"]` for its `mcp` block —
   the `github` platform's own manifest already restricts it to `core`-tagged servers only, which
   is exactly what §3.2 confirms the live `.vscode/mcp.json` contains (7 core servers, no
   `extended` servers).
3. `AGENTS.md` §"MCP Servers"' "Core servers (always available)" table (cross-checked, not relied
   on alone) independently lists both `brave` and `context7` by name under "core," consistent with
   `servers.yaml`.
4. `cwso`'s presence in `.vscode/mcp.json` is accounted for in §4 above as intentional,
   documented, dest-only preserved content per `merge-mcp-json.py`'s own docstring and
   `prune_names_recursive` — not a generator defect, not related to the tag question at all.

**Conclusion: the orchestrator's pre-dispatch correction is confirmed correct, on this session's
own independent re-derivation from `servers.yaml`, `github.json`, and `AGENTS.md`, not merely
restated from the task brief.** `brave` and `context7` are `core`-tagged and are supposed to
appear in every platform's projection, `.vscode/mcp.json` included; `cwso` is intentional
hand-added content, not a generator gap. **plan-037's original claim is false and should not be
carried forward into T421/T422 as a defect to fix.**

This session's own independent check did surface one thing the orchestrator's pre-dispatch note
did not mention: the missing `.vscode/mcp.json.provenance.json` sidecar (§4). That finding is
unrelated to the `brave`/`context7`/`cwso` question specifically — it does not reopen or qualify
the adjudication above — but it is new information this session found that the brief's
pre-dispatch note did not surface, and is flagged for T421/T422 rather than silently reconciled.

**On the "zero drift across 557 files" claim:** this session could not reproduce that number —
`node scripts/sync.mjs --check` was not run (see §1's disclosed tooling limitation). The manual,
file-by-file content diff in §3 found zero *content* discrepancies across all 7 platforms'
generated MCP files against `emitMcp()`'s expected output for each declared format, which is
consistent with (though not proof of) a zero-drift result on those 7 files specifically. It cannot
speak to the other ~550 non-MCP files `sync.mjs` also projects (agents, commands, instructions,
skills), which were out of this task's scope and were not checked.

## 6. Open items for T421/T422

- Confirm live, via `node scripts/sync.mjs --check` (from `implementation/`), that this document's
  §3 table and §3.2 enumeration match actual generator output on a clean `develop` checkout — this
  session's evidence is a manual static trace, not a command transcript.
- Resolve the `.vscode/mcp.json.provenance.json` anomaly (§4): confirm whether `.vscode/*`'s
  gitignore status makes a missing sidecar expected-and-benign in any fresh worktree/clone, or
  whether it indicates a real gap in `sync.mjs`'s sidecar-writing path for the `vscode` format
  specifically.
- Treat `cwso` (§4) and the `brave`/`context7` core-tag classification (§5) as closed,
  non-issues — do not re-flag either without new evidence beyond what's cited here.

## 7. Orchestrator independent verification (added post-authoring, 2026-09-08)

This section was added by the orchestrator after this document's initial authoring, to close the
two items in §6 that this session's tooling (no Bash grant) could not itself resolve. Both are now
resolved with real command output rather than left open for T421.

**§6 item 1 — live `sync.mjs --check` run.** Executed from a clean `agent/solution-architect/T420`
worktree checked out from `origin/develop` (same commit this document was authored against):

```
$ node scripts/sync.mjs --check      # run from implementation/
[claude-code] checked 86 files -> .claude
[cline] checked 40 files -> .cline
[cursor] checked 86 files -> .cursor
[gemini] checked 86 files -> .gemini
[github] checked 87 files -> .github
[opencode] checked 86 files -> .opencode
[pi] checked 86 files -> .pi

OK - no drift across 557 files.
```

This confirms, by real command transcript rather than manual trace, the §1/§5 "zero drift" claim
this document could previously only support by hand-diffing. §3/§3.2's per-platform contract table
is consistent with this result.

**§6 item 2 — `.vscode/mcp.json.provenance.json` anomaly, root-caused.** This is real, but benign
in content and narrow in scope — not a `sync.mjs` code defect, and not related to the
`brave`/`context7`/`cwso` question in §5 at all:

- The file exists on disk in the long-lived primary checkout (`/home/emage/Code/emage/emage.code`,
  dated 2026-08-10, 170 bytes) and its content matches what `sync.mjs` currently generates (implied
  by the zero-drift result above, which re-generates and diffs it as part of the `github` platform's
  87 checked files).
- It is **not git-tracked**: `git ls-files` lists `.vscode/mcp.json` but not
  `.vscode/mcp.json.provenance.json`, while the analogous sidecar for all 6 other platforms
  (`.mcp.json.provenance.json`, `.cline/mcp.json.provenance.json`, etc.) **is** tracked.
- `git check-ignore -v` confirms why: `.gitignore` line 53 (`.vscode/*`) matches
  `.vscode/mcp.json.provenance.json` and there is no negation entry for it (only `extensions.json`
  and `settings.example.json` are un-ignored, lines 54–55). `.vscode/mcp.json` itself was at some
  point force-added past this same rule (`git add -f`, evidenced by it being tracked despite
  matching the same `.vscode/*` pattern — `check-ignore` does not flag already-tracked paths) —
  but its provenance sidecar was never given the same treatment.
- **Practical consequence:** a fresh `git clone` or `git worktree add` (as this task's own worktree
  was) gets `.vscode/mcp.json` but not its sidecar, until a real (non-`--check`) `sync.mjs` run
  regenerates it locally. `merge-mcp-json.py`'s own docstring already treats a missing old-sidecar
  as "bootstrap" (non-fatal), so this does not break `--update`'s merge logic — but it does mean
  `github` is the one platform whose provenance history doesn't survive a fresh checkout, an
  inconsistency with the other 6 platforms with no evident reason for the asymmetry.
- **Disposition for T421:** this is a real, narrow, low-risk fix — add a `.gitignore` negation
  (`!.vscode/mcp.json.provenance.json`, alongside the existing two negations) and `git add -f` the
  file so it's tracked like its 6 counterparts. This is arguably closer to plan-035's original
  (pre-plan-037) T421 framing — "close the `.claude`/`.github` gaps... no projected MCP config
  present" — than the `brave`/`context7` tag question ever was, since it is an actual, if minor,
  completeness gap specific to the `github` platform target. It is unrelated to, and does not
  reopen, §5's `brave`/`context7`/`cwso` adjudication.

Both items in §6 are now closed. No further open items remain in this document as of this section.
