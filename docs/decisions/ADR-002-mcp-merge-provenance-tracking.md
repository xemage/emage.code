# ADR-002 — Track MCP-merge key provenance via per-file sidecar diff, with a one-time forced-prune bootstrap bridge

> Filename: `ADR-002-mcp-merge-provenance-tracking.md`

- **Status**: Accepted
- **Date**: 2026-08-10
- **Decider(s)**: solution-architect
- **Tasks**: T389 (this decision), T390 (implementation), T391 (tests), T392 (docs), T393 (gate)
- **Evidence**: docs/plans/plan-034-mcp-provenance-tracking.md; scripts/merge-mcp-json.py;
  implementation/scripts/sync.mjs `emitMcp()`/`syncPlatform()`; scripts/install.sh

## Context

> **Correction (2026-08-10, pre-merge):** During T390's implementation attempt, this ADR's original
> Decision §4 pruning algorithm was found to be structurally broken: it checked key containment at the
> top level of the parsed MCP JSON file, but every one of the 7 platforms actually nests server names
> one level inside a per-format wrapper key (`servers` for `vscode`; `mcpServers` for
> `cursor`/`pi`/`gemini`/`claude-code`/`cline`; `mcp` for `opencode` — see `emitMcp()`), never at the top
> level. Because of this, the original algorithm's `key in merged` check was always `False` for every
> real server name, so pruning — both the sidecar diff and `--force-prune-keys` — could never locate or
> remove any real server key, on any platform, under any circumstances. This ADR had not yet reached
> `develop` or been reviewed at the T393 validation gate when the flaw was found, so this is a **pre-merge
> correction of an undiscovered defect in the original Decision text — not a supersession of an accepted,
> merged decision**, and no new ADR number is issued. Decision §4 below is corrected to walk
> `merged`/`source_data` recursively — a generic recursive prune requiring no new CLI flag and no
> platform-specific wrapper-key knowledge in `merge-mcp-json.py` — chosen over an alternative explicit
> `--mcp-key <name>` wrapper-key parameter so the tool remains fully platform-agnostic, matching its
> existing design philosophy. Decision §1–§3 and §5–§7 are unaffected and unchanged by this correction;
> the pruning-refresh step in §4.4 (writing `--new-sidecar`'s content to `--old-sidecar`'s path) is also
> unaffected, since it operates on the sidecar files' own flat JSON content, never on the MCP file's
> nested structure.

`scripts/install.sh --update` regenerates all 7 platforms' MCP/settings files from
`implementation/knowledge/mcp/servers.yaml` and merges the freshly generated file into each target
project's existing file via `scripts/merge-mcp-json.py`. That merge (`merge_json()`) is memoryless: for
any top-level JSON key present only in `dest` (the target's existing file) and absent from `source`
(this generation's output), the rule is "preserved as-is, unconditionally, no exceptions" — there is no
third input anywhere in the call graph that could tell the merge "the generator used to own this key
and has now retired it, so it is safe to remove" versus "a human hand-added this key and it must be
kept forever." Both cases look identical to the merge today: a dest-only key.

This is not a hypothetical gap. This repository's own `implementation/.vscode/mcp.json` already carries
two real hand-added elements that the generator never wrote and never will: a `cwso` key under
`servers` (sibling to every generator-owned entry, never present in `servers.yaml`) and a top-level
`inputs` array (a key the `vscode` branch of `emitMcp()` never emits at all). Any provenance mechanism
that cannot distinguish these two permanently-preserved keys from a genuinely-retired generator key is
unacceptable regardless of how it performs elsewhere.

Separately, T386 already removed four servers (`e2b`, `redis`, `figma`, `notion`) from
`servers.yaml`, which means every already-installed project (including this repository's own root, on
the very first `--update` after this ADR's mechanism ships) currently has those four keys sitting in
its MCP files as dest-only orphans with **no possible history to diff against** — a pure sidecar-diff
mechanism has nothing to diff on its first run and cannot, by itself, close this pre-existing bootstrap
gap. A separate, explicit mechanism is required to retire this specific known set once, without
inventing a general "prune anything unknown" rule.

A reusable-looking pattern already exists — `sync.mjs`'s `syncPlatform()` writes a
`.generated-manifest.json` sidecar per `outRoot` — but it is unsuitable as this design's provenance
source for two independently-confirmed reasons: (1) an ordering bug — for the 5 tree-based platforms,
`sync_tree_into()`'s `rsync -a --delete` runs before `merge_or_copy_mcp_json()`, and
`.generated-manifest.json` is not in the current `exclude_rel` list, so by the time any merge step
could read the "old" manifest it has already been overwritten with the new one; and (2) a
path-vs-key mismatch — its `files` array lists relative file paths written under `outRoot`, not the
top-level JSON *keys* inside the MCP file, so it cannot answer "which server names did the generator
emit last time" without re-parsing the MCP file's own content. It also does not exist at all for the
two standalone-file platforms (`.vscode/mcp.json`, `.mcp.json`), since both live outside any
`outRoot`.

No new evidence surfaced during this task's re-verification (source files quoted in the task brief were
read directly against the live repository and matched verbatim) that would change the
already-established recommendation from plan-034: adopt option (a) — a dedicated, per-MCP-file sidecar
diffed old-vs-new — as the permanent mechanism, plus option (c) — an explicit, opt-in
`--force-prune-keys` flag — as a narrowly-scoped, one-time bootstrap bridge for the pre-existing
`e2b`/`redis`/`figma`/`notion` gap. Option (b), an in-file marker/comment convention, remains rejected:
standard JSON has no comment syntax, and a sentinel data field (e.g. `"_meta": {...}`) would pollute the
platform-native schema every downstream tool (VS Code, Cursor, Gemini CLI, Opencode, Cline) parses
directly — a documented, real concern per `docs/wiki/mcp-servers.md`'s per-platform runtime-verification
checklist (T384) — while still requiring the identical diff logic as (a), just relocated, with no
architectural simplification.

## Decision

We adopt the sidecar-diff mechanism (permanent) plus the `--force-prune-keys` bridge (one-time
bootstrap) exactly as follows. This is the final, exact form — not a range of options.

### 1. Sidecar file naming and location (all 7 platforms)

A sidecar file named `<mcpfilename>.provenance.json` is always colocated in the exact same directory
as the MCP file it describes — never in a different directory, never a single shared file across
platforms:

| MCP file | Sidecar file |
|---|---|
| `implementation/.cursor/mcp.json` | `implementation/.cursor/mcp.json.provenance.json` |
| `implementation/.gemini/settings.json` | `implementation/.gemini/settings.json.provenance.json` |
| `implementation/.opencode/opencode.json` | `implementation/.opencode/opencode.json.provenance.json` |
| `implementation/.pi/mcp.json` | `implementation/.pi/mcp.json.provenance.json` |
| `implementation/.cline/mcp.json` | `implementation/.cline/mcp.json.provenance.json` |
| `implementation/.vscode/mcp.json` | `implementation/.vscode/mcp.json.provenance.json` |
| `implementation/.mcp.json` | `implementation/.mcp.json.provenance.json` |

This convention is deliberately independent of `.generated-manifest.json` (per Context, above) and
gives every one of the 7 platforms — including the 2 standalone files that have no existing tree-level
manifest at all — a provenance record with no additional indirection.

### 2. Sidecar schema (schemaVersion 1)

```json
{
  "schemaVersion": 1,
  "generatorOwnedKeys": ["gitlab", "playwright", "context7", "..."]
}
```

`generatorOwnedKeys` is exactly `Object.keys(filtered)` from `emitMcp()` — the format-independent,
pre-branch server-name set computed once before any platform-format branch — sorted, for
deterministic, diff-friendly output (mirrors `.generated-manifest.json`'s own `files.sort()`
convention). No other fields are defined in schemaVersion 1.

### 3. `merge-mcp-json.py` CLI surface (additive, backward-compatible; no existing flag's behavior
   changes)

- `--old-sidecar <path>` (optional): the dest-side sidecar, read **before** merging. If the path does
  not exist on disk, this is the bootstrap case — treated as "no provenance history."
- `--new-sidecar <path>` (optional): the source-side sidecar (the freshly generated one under
  `implementation/`), read for the pruning diff and also used, after a successful merge, to overwrite
  `--old-sidecar`'s path with the current generation's key set — seeding history for the *next*
  `--update`. `--old-sidecar` and `--new-sidecar` must be supplied together (both or neither); supplying
  exactly one is an error (non-zero exit, no partial write).
- `--force-prune-keys <comma-separated-names>` (optional, independent of the two sidecar flags — works
  with or without them present): prunes exactly the named dest-only keys from the merge result, if and
  only if each named key is present in `dest` and absent from `source`. If a named key is not
  genuinely dest-only (missing from `dest` entirely, or still present in `source`), this is an error
  (non-zero exit, no partial write) — never a silent no-op, and never "prune it from `source` too."

### 4. Pruning algorithm (applied after the existing `merge_json(dest, source)` produces `merged`; this
   is the literal, unambiguous rule)

Every server name managed by this decision (`generatorOwnedKeys` entries, and `--force-prune-keys`
names) is a key one level **inside** a per-format wrapper key (`servers` for `vscode`, `mcpServers` for
`cursor`/`pi`/`gemini`/`claude-code`/`cline`, `mcp` for `opencode` — see `emitMcp()`), never a top-level
key of the parsed MCP file itself. The pruning algorithm therefore is a **recursive, parallel walk of
`merged` and `source_data`**, checking every dict level either structure contains — not only the top
level — deliberately mirroring how `merge_json()` itself already recurses into matching nested dicts at
any depth (this is exactly what already lets `cwso`, nested under `servers`, survive correctly today).
No platform-specific wrapper-key name is hard-coded anywhere in `merge-mcp-json.py`; the walk finds
whatever depth a key actually lives at, generically, with the same code path for all 7 platforms.

Define `prune_names_recursive(merged_node, source_node, names)`, first called with `merged_node =
merged`, `source_node = source_data`:

  a. If `merged_node` is not a `dict`, return immediately — nothing to prune or recurse into at this
     path.
  b. Let `source_dict` be `source_node` if it is a `dict`, else `{}` (an absent or non-dict counterpart
     at this path means every key `merged_node` holds at this level is, by definition, absent from
     `source` at this same path).
  c. For each `name` in `names`: if `name` is a key of `merged_node` **and** `name` is not a key of
     `source_dict`, delete `merged_node[name]`. (The second condition re-confirms genuine
     dest-only-ness, at this exact nesting level, after the ordinary merge — a key `source` still emits
     at this same path is never touched, regardless of what the diff or `--force-prune-keys` says.)
  d. For each remaining `(key, value)` pair in `merged_node`: if `value` is a `dict`, recurse —
     `prune_names_recursive(value, source_dict.get(key), names)` — descending in lockstep by the same
     key path in both structures, at every depth, not only one level.

Using this helper:

1. If `--old-sidecar`/`--new-sidecar` were both given, and `--old-sidecar`'s file exists and parses:
   compute `retired = old_sidecar.generatorOwnedKeys − new_sidecar.generatorOwnedKeys` (set
   difference). Call `prune_names_recursive(merged, source_data, retired)`.
2. If `--old-sidecar` was given but its file does not exist (bootstrap case): step 1 is skipped
   entirely. Zero keys are pruned by the diff mechanism, unconditionally.
3. If `--force-prune-keys` was given: first run `prune_names_recursive` in **check-only** mode over the
   named keys — for each named key, confirm it matches at least one path anywhere in `merged` where
   step (c) above would actually delete it (i.e. present in `merged` at that path, absent from
   `source_data` at that same path). If any named key matches zero such occurrences anywhere in the tree
   (absent from `merged` entirely, or present in `source_data` at every path where it also appears in
   `merged`), exit non-zero with an error identifying the exact key(s) that failed the check, **before
   writing anything** to `--dest`. Only if every named key passes this check does the real
   `prune_names_recursive(merged, source_data, force_prune_names)` deletion pass run.
4. After all pruning: write `merged` to `--dest` (unchanged from today's behavior). If `--new-sidecar`
   was given and this is not a `--dry-run`, also write `--new-sidecar`'s exact content to
   `--old-sidecar`'s path, refreshing the dest-side sidecar for the next `--update` to diff against.
   **This step is unaffected by the nesting-level fix**: it operates purely on the sidecar files' own
   flat `{schemaVersion, generatorOwnedKeys}` JSON content, never on the MCP file's internal structure,
   so its behavior and wording are unchanged by this correction.

Steps 1–3 are independent and additive: `--force-prune-keys` may be combined with the sidecar flags in
a single invocation, or used entirely on its own without either sidecar flag present.

**Cross-depth collision risk (accepted, documented):** because `prune_names_recursive` matches a name
against *any* dict level's keys, not only the wrapper level, a name that happened to collide with an
unrelated key elsewhere in the same file (at any depth) would be considered for pruning there too, using
the identical dest-only check. Given the real shape of all 7 platforms' generated files — the
per-format server map (`servers`/`mcpServers`/`mcp`) is the only meaningfully deep, dynamically-keyed
nested dict any of them contains — this is a low, documentable risk, in the same spirit as the "coarse
per-key-name provenance" tradeoff already accepted in the Context section above, not a new class of risk
this correction introduces.

### 5. `install.sh` wiring (confirmed shape; T390 implements)

- **5 tree-based platforms** (`cursor`, `gemini`, `opencode`, `pi`, `cline`): `sync_tree_into()`'s
  exclude mechanism must be extended to exclude the sidecar file in addition to the MCP file itself, so
  both survive the `rsync -a --delete` tree replace. `sync_tree_into()`'s current `exclude_rel`
  parameter is a single string passed to one `--exclude=`; this must become either a second parameter
  (`exclude_rel_2`) or an array-typed parameter accepting multiple relative paths — T390 must pick one
  and apply it consistently across all 5 call sites. `merge_or_copy_mcp_json()` gains the two new
  `--old-sidecar`/`--new-sidecar` arguments, passed for all 5 of these platforms. On fresh
  (non-`--update`) installs, the sidecar is plain-copied alongside the MCP file, mirroring the existing
  MCP-file fresh-install behavior.
- **2 standalone platforms** (`github`'s `.vscode/mcp.json`, `claude-code`'s `.mcp.json`): identical
  `--old-sidecar`/`--new-sidecar` wiring through `merge_or_copy_mcp_json()`, but **no** exclude-list
  change is needed — neither `install_github()` nor `install_claude_code()` ever calls
  `install_tree_into`/`sync_tree_into` on the directory these two MCP files (or their sidecars) live in,
  so nothing ever whole-tree-replaces them regardless of this design.

### 6. `--force-prune-keys` bootstrap bridge and its scope

`--force-prune-keys` is invoked exactly once, explicitly, by `docs/tasks/task-T382.md`'s Step 2
(already amended per that brief), passing the literal string `e2b,redis,figma,notion` — the same four
names T386 removed from `servers.yaml`. This is a one-time, human-supplied, reviewed list; it is not a
standing default anywhere else in the codebase, and no other call site in `install.sh` passes this flag.

### 7. Ruling: is `--force-prune-keys` a permanent CLI capability?

**Ruling: `--force-prune-keys` remains a permanent capability of `merge-mcp-json.py`, but is
documented as an undocumented-as-routine, manually-invoked escape hatch for future one-off registry
cleanups — not a standing default and not part of the normal `--update` code path.** Reasoning: the
sidecar-diff mechanism (§1–4) only prunes keys it has positive historical evidence for, which
structurally means it can never retroactively close a bootstrap gap that predates the sidecar's
existence — every future registry-wide server removal that ships without at least one prior
`--update` cycle recording it in a sidecar will hit the exact same gap `e2b`/`redis`/`figma`/`notion`
hit here. Removing the flag after this bootstrap use would force a future maintainer to reinvent it
under time pressure the next time this situation recurs, for no compensating safety benefit — the flag
is already maximally conservative (named keys only, hard error on any key that is not genuinely
dest-only, no wildcard/pattern support). It is retained, un-called by default, as a reviewed manual
tool, not deprecated or scheduled for removal.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| (a) sidecar diff (chosen, permanent mechanism) | Self-maintaining once seeded; safe on bootstrap (no old sidecar → no pruning); needs no manual intervention on steady-state `--update` runs; scoped per-file, matching the merge's own per-file granularity | Cannot by itself close the pre-existing `e2b`/`redis`/`figma`/`notion` gap, since no sidecar history exists before this fix ships | Chosen as the permanent mechanism; the bootstrap gap is covered by (c) instead, not by weakening (a) |
| (b) in-file marker/comment | Would colocate provenance data with the content it describes, no separate file to keep in sync | Standard JSON has no comment syntax; a sentinel data field (e.g. `"_meta": {...}`) pollutes the platform-native schema every downstream tool (VS Code, Cursor, Gemini CLI, Opencode, Cline) parses directly, risking validation warnings (documented concern, `docs/wiki/mcp-servers.md`, T384); still needs the identical diff logic as (a), just relocated, with no architectural simplification | Rejected |
| (c) explicit `--force-prune-keys` only, no sidecar | Needs no history; a human-reviewed, explicit, one-time list is auditable and cannot silently over-prune; the only option of the three that can close the pre-existing bootstrap gap | No automatic mechanism for future retirements — every future registry removal would need a fresh manual invocation, which does not scale as a *sole, standing* mechanism | Chosen ONLY as a one-time bootstrap bridge alongside (a), not as a standalone permanent mechanism |

## Consequences

- **Positive**: Distinguishes generator-retired keys from hand-added keys with an explicit, auditable,
  file-local record; requires no schema pollution of platform-native MCP files; the bootstrap gap for
  `e2b`/`redis`/`figma`/`notion` is closed by an explicit, reviewed, one-time flag rather than an
  inferred heuristic; every non-negotiable property (see below) is satisfied by construction, not by
  convention.
- **Negative**: Adds a second file per platform's MCP output (7 new sidecar files across
  `implementation/`), and a second exclude-list entry point per tree-based platform that T390 must wire
  correctly across all 5 call sites; `sync_tree_into()`'s single-string `exclude_rel` parameter must be
  extended, which is a signature change touching all 7 `install_<platform>()` functions indirectly.
- **Risks introduced**: If T390's exclude-list extension is wired incorrectly for even one of the 5
  tree-based platforms, that platform's sidecar would be silently deleted by `rsync --delete` on every
  `--update`, permanently resetting that platform to the bootstrap (no-pruning) case without any visible
  error — T391 must include a test that asserts sidecar survival across an `--update` cycle for each of
  the 5 tree-based platforms individually, not just one representative platform.
- **Follow-ups**: T390 (implement `merge-mcp-json.py` flags + `install.sh` wiring), T391 (tests), T392
  (docs), T393 (validation gate).

## Security constraints

Restating non-negotiable property #5: no literal secret value is ever written by any new code path
introduced by this decision. The sidecar schema (`generatorOwnedKeys`) carries only server *names*
(strings matching `servers.yaml` entry keys, e.g. `"gitlab"`, `"playwright"`) — never connection
strings, tokens, URLs with embedded credentials, or resolved environment variable values. The pruning
algorithm (§4) only ever deletes or preserves whole JSON keys by name, at whatever nesting depth they
occur (see §4's recursive walk); it never reads, copies, or interpolates the *values* under those keys,
at any depth. Placeholder syntax (`${env:VAR}` / `{env:VAR}`) already present in
`merge-mcp-json.py`'s existing module docstring guarantee is untouched by every code path this decision
adds — the sidecar diff and `--force-prune-keys` both operate purely on the set of key *names*, never on
value contents, at any depth in the tree.

## Validation

T391's tests must prove this decision correct via the four proof classes plan-034 names, each mapped to
a specific, checkable non-negotiable property from this ADR:

All fixtures below must nest server-name keys one level under the platform's real wrapper key
(`servers`/`mcpServers`/`mcp`, per §4), never at the top level of the fixture file, so tests exercise the
same nesting depth the real generated files use — this is the exact literal change required by the
nesting-level fix; none of the four proof classes change in spirit.

1. **Bootstrap-safe default** (property #1): run a merge with `--old-sidecar` pointing at a path that
   does not exist and `--new-sidecar` pointing at a valid sidecar, against a `dest`/`source` fixture
   whose server names are nested under the platform's wrapper key; assert zero dest-only keys are
   pruned at any nesting depth, and the merge result is byte-for-byte identical to running without
   either sidecar flag at all.
2. **Retired-key pruning** (the diff mechanism itself): seed an `--old-sidecar` containing a key not
   present in `--new-sidecar` and not present in `source`, with a `dest` fixture in which that key is
   nested one level under the platform's wrapper key (not at the file's top level); assert that key is
   removed from its actual nested path in the merge result, all sibling keys and the wrapper object
   itself are otherwise untouched, and that `--old-sidecar`'s path is refreshed with `--new-sidecar`'s
   content after a successful (non-dry-run) merge.
3. **Hand-added-key survival** (property #3, the real `cwso`/`inputs` precedent): construct a `dest`
   fixture containing both `cwso` (a sibling key nested under `servers`, alongside the generator-owned
   entries) and a top-level `inputs` array, matching this repository's own `.vscode/mcp.json` exactly;
   run a merge with `--force-prune-keys` set to an unrelated list (e.g. `e2b,redis,figma,notion`,
   themselves nested under `servers` in the fixture, matching their real historical location) and,
   separately, with a populated sidecar diff; assert neither `cwso` nor `inputs` is ever removed in
   either case, and that both persist byte-for-byte across an `--update` cycle including the
   `rsync --delete` step (property #4 double-checked via this same fixture: a key `source` still emits
   at its nested path must never be prunable regardless of sidecar content — add a variant where the
   diff or `--force-prune-keys` name a key that `source` still emits at that same nested path, and
   assert the merge exits non-zero / leaves that key untouched rather than deleting it).
4. **`--force-prune-keys` scoping** (property #3 and the explicit-error requirement): run
   `--force-prune-keys` naming a key that is not dest-only at its real nested path (either absent from
   `dest` entirely, or still present in `source` at that same nested path); assert non-zero exit, no
   write to `--dest`, and an error message identifying the exact offending key name(s).

Additionally, T391 must include a sidecar-survival test per tree-based platform (5 separate assertions,
not one representative case — see "Risks introduced" above), confirming `<mcpfile>.provenance.json`
is present and unchanged immediately after a `sync_tree_into()`/`rsync --delete` pass, before
`merge_or_copy_mcp_json()` runs.
