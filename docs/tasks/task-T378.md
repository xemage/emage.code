# Task T378 — Add regression test coverage for the 5 newly merge-safe platforms

**ID:** T378
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T377
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-02)

This brief is self-contained. You do not need to read plan-033 or T377's brief to execute this
task, though you do need T377's fix already committed on the branch you check out (see Git workflow
below).

## Objective
T377 extended `scripts/install.sh --update`'s JSON-key-preserving merge (previously only
`.vscode/mcp.json`/`.mcp.json`, per plan-031/T369) to `.cursor/mcp.json`, `.gemini/settings.json`,
`.opencode/opencode.json`, `.pi/mcp.json`, `.cline/mcp.json`. Prove this behavior with automated
tests, mirroring the exact pattern plan-031/T369 already established in
`tests/functional/test_install_script.py` for the two github/claude-code files, extended to all five
newly-covered platforms — plus one new class of test T369 didn't need (because github's/
claude-code's MCP file always lived outside the replaced tree): proving the exclude-from-`rsync
--delete` is scoped to exactly the one file, not the whole platform tree.

## Inputs (exact paths, verified against the current file)
The file you will edit: `/home/emage/Code/emage/emage.code/tests/functional/test_install_script.py`
(329 lines as of this brief — re-count yourself; it may have grown if run out of order).

The existing pattern to replicate (quoted verbatim, the four github/claude-code tests you are
mirroring — read-only reference, do not modify these):
- `test_fresh_install_plain_copies_mcp_json` (lines 169-200) — fresh install byte-identical to
  source.
- `test_update_preserves_unknown_mcp_server_key_github` (lines 202-244) — unknown server key +
  top-level `inputs` key both survive `--update`.
- `test_update_refreshes_generator_known_mcp_keys_github` (lines 246-272) — `context7` refreshed to
  match generated source after `--update`.
- `test_update_preserves_unknown_mcp_server_key_claude_code` (lines 274-316) — same as the github
  test, for `.mcp.json`.
- `test_update_refreshes_generator_known_mcp_keys_claude_code` (lines 318-344) — same refresh
  assertion, for `.mcp.json`.

The `_run_install` helper (lines 21-38, read-only reference, do not modify) already supports
`platform` and `update` parameters for any of the seven platform names (it just forwards to
`scripts/install.sh --platform <platform> [--update]`); you do not need a new helper.

The five platforms' MCP output shapes, confirmed by direct read of
`implementation/.<platform>/<file>` during T377's planning (needed to write correct assertions —
each has a different top-level key or sibling non-MCP keys):
| Platform | File | Top-level MCP key | Sibling non-MCP keys (must survive untouched) |
|---|---|---|---|
| `cursor` | `.cursor/mcp.json` | `mcpServers` | none |
| `gemini` | `.gemini/settings.json` | `mcpServers` | `hooks` |
| `opencode` | `.opencode/opencode.json` | `mcp` | `$schema`, `instructions` |
| `pi` | `.pi/mcp.json` | `mcpServers` | none |
| `cline` | `.cline/mcp.json` | `mcpServers` | none |

Every platform's MCP output contains a `context7` entry (it is a `core`-tagged server in
`implementation/knowledge/mcp/servers.yaml`, emitted to every platform) — use it as the
generator-known-key refresh target, exactly as the existing github/claude-code tests do.

## Allow-list (files you may touch)
- `tests/functional/test_install_script.py` only. Add new test methods; do not modify any of the
  ten existing test methods already in the file.

## Deny-list (do not touch — no exceptions)
- Do NOT edit `scripts/install.sh` — T377 already fixed it; this task only adds test coverage.
- Do NOT edit `scripts/merge-mcp-json.py`.
- Do NOT edit any of the ten existing test methods in this file (`test_install_merges_into_...`
  through `test_update_refreshes_generator_known_mcp_keys_claude_code`).
- Do NOT edit any other test file.
- Do NOT add a new test module — extend the existing file.
- Do NOT create any new branch — use the branch T377 already created (see Git workflow below).

## Exact tests to add
Add five new test methods to `TestInstallScript`, placed after the existing
`test_update_refreshes_generator_known_mcp_keys_claude_code` method (end of the class, before the
`if __name__ == "__main__":` block). One method per platform is the minimum required shape; each
method must cover, for its platform: (a) fresh install is a plain byte-identical copy, (b) `--update`
preserves an unknown hand-added key, (c) `--update` refreshes `context7` to match generated source,
(d) `--update` still deletes a stale non-MCP file elsewhere in the same platform tree. You may
combine (a)-(d) into one method per platform (recommended, mirrors the density of the existing
github/claude-code tests) or split further — the assertions listed are the required minimum content,
not a required method count.

Reference implementation (adapt the per-platform table above for `gemini`/`opencode`'s differences —
shown here for `cursor` as the template; write the other four analogously):

```python
    # -- .cursor/mcp.json / .gemini/settings.json / .opencode/opencode.json /
    #    .pi/mcp.json / .cline/mcp.json merge-on-update (T377) --

    def test_cursor_mcp_json_merge_on_update(self):
        implementation_mcp = repo_root() / "implementation" / ".cursor" / "mcp.json"
        source_data = json.loads(implementation_mcp.read_text(encoding="utf-8"))
        source_context7 = source_data["mcpServers"]["context7"]

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            # (a) fresh install: byte-identical plain copy
            proc = self._run_install(target, platform="cursor")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            mcp_path = target / ".cursor" / "mcp.json"
            self.assertEqual(
                mcp_path.read_text(encoding="utf-8"),
                implementation_mcp.read_text(encoding="utf-8"),
                "fresh (non --update) install must plain-copy .cursor/mcp.json byte-for-byte",
            )

            # inject an unknown server key + corrupt a generator-known key
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["mcpServers"]["my-custom-server"] = {"url": "https://example.invalid/mcp"}
            data["mcpServers"]["context7"] = {"url": "https://stale.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            # (d) a stale non-MCP file elsewhere in the same tree
            stale = target / ".cursor" / "stale-agent-that-should-be-deleted.md"
            stale.write_text("remove me", encoding="utf-8")

            proc2 = self._run_install(target, platform="cursor", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            # (b) unknown key survives
            self.assertEqual(
                updated["mcpServers"].get("my-custom-server"),
                {"url": "https://example.invalid/mcp"},
                "unknown pre-existing server key must survive --update merge",
            )
            # (c) generator-known key refreshed
            self.assertEqual(
                updated["mcpServers"]["context7"],
                source_context7,
                "generator-known server key must be refreshed to match the generated source on --update",
            )
            # (d) stale non-MCP file in the same tree still correctly deleted —
            # proves the exclude is scoped to exactly mcp.json, not the whole tree
            self.assertFalse(
                stale.exists(),
                "--update must still stale-clean the rest of .cursor/ via rsync --delete; "
                "only mcp.json is exempted",
            )
```

For `gemini`, additionally assert the `hooks` key (present in
`implementation/.gemini/settings.json`) is unchanged after `--update`:
```python
            self.assertEqual(
                updated.get("hooks"),
                source_data.get("hooks"),
                "gemini's non-MCP 'hooks' key must be unaffected by the mcpServers merge",
            )
```
For `opencode`, use top-level key `mcp` (not `mcpServers`) throughout, and additionally assert
`$schema` and `instructions` are unchanged after `--update`:
```python
            self.assertEqual(updated.get("$schema"), source_data.get("$schema"))
            self.assertEqual(updated.get("instructions"), source_data.get("instructions"))
```

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Targeted run of just this file:
   ```
   python3 -m unittest tests.functional.test_install_script -v
   ```
   PASS = all methods report `ok` (10 pre-existing + your new ones), `OK` at the end, exit 0. This
   actually shells out to `scripts/install.sh` end-to-end into temp dirs, so it depends on T377's
   fix already being present on the branch.

2. Full functional suite:
   ```
   python3 tests/run.py --suite functional -v
   ```
   PASS = exits 0, no `FAILED`/`ERROR` lines.

3. Full suite (same gate T381 will run):
   ```
   python3 tests/run.py
   ```
   PASS = exits 0. Capture your own before/after counts — do not assume a stale count from an
   earlier brief; your new tests should increase the total count and must not reduce it.

## Acceptance criteria (all must be true)
- [ ] `git diff` shows changes in exactly one file: `tests/functional/test_install_script.py`.
- [ ] For each of the 5 platforms (`cursor`, `gemini`, `opencode`, `pi`, `cline`): a test asserts an
      unknown pre-existing key survives `--update`.
- [ ] For each of the 5 platforms: a test asserts the generator-known `context7` key is refreshed to
      match `implementation/.<platform>/<file>`'s current content after `--update` (verified against
      a deliberately-corrupted dest value, not a no-op check).
- [ ] For each of the 5 platforms: a test asserts a stale non-MCP file elsewhere in that platform's
      tree is still deleted by `--update` — proving the exclude is scoped to exactly the one file.
- [ ] For each of the 5 platforms: a test asserts a fresh (non-`--update`) install is still a plain
      byte-identical copy of the MCP file.
- [ ] `gemini`'s `hooks` key and `opencode`'s `$schema`/`instructions` keys are explicitly asserted
      unchanged after `--update` (not merely "not tested" — an explicit assertion).
- [ ] `python3 -m unittest tests.functional.test_install_script -v` passes.
- [ ] `python3 tests/run.py` exits 0, total test count increased from your own recorded baseline.
- [ ] None of the 10 pre-existing test methods in this file were modified.

## Blocker protocol
STOP and report a blocker (do not improvise a workaround) if:
- The branch T377 created (`bugfix/T377-install-mcp-merge-all-platforms`) does not exist, or does
  not contain T377's fix (e.g. `install_cursor()` in `scripts/install.sh` still calls
  `install_tree_into "$IMPLEMENTATION/.cursor" "$TARGET/.cursor"` with only two arguments) →
  `type: dependency`, `severity: critical` — T378 cannot proceed without T377's completed fix.
- Any of the five platforms' current generated MCP output doesn't match the shape documented in the
  table above (different top-level key, missing/extra sibling keys, no `context7` entry) → `type:
  dependency`, `severity: major` — re-verify against the actual current
  `implementation/.<platform>/<file>` content before writing that platform's test.
- Any test fails for a reason unrelated to your added tests (i.e. a pre-existing test regresses) →
  `type: technical`, `severity: major`, include exact command output; do not modify the pre-existing
  test to make it pass.
- T377's merge behavior itself appears broken when you write these tests against it (e.g. the
  unknown-key-survival assertion genuinely fails against T377's real committed code) → `type:
  technical`, `severity: major` — report the actual observed behavior; do not weaken your assertion
  to hide a real regression in T377's implementation. This is exactly the scenario T378 exists to
  catch.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Check out the EXISTING branch `bugfix/T377-install-mcp-merge-all-platforms` (created by T377 —
   do NOT create a new branch, do NOT branch from `develop` again).
2. Confirm T377's commit is present (`git log --oneline -3` should show T377's fix commit).
3. Make the change; run all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   test(install): assert MCP merge-on-update for cursor/gemini/opencode/pi/cline

   Mirrors the plan-031/T369 pattern already covering .vscode/mcp.json and
   .mcp.json, extended to the five platforms T377 just made merge-safe.
   Each new test proves: fresh install is a plain copy, an unknown
   hand-added server key survives --update, a generator-known key
   (context7) is refreshed, and a stale non-MCP file elsewhere in the same
   tree is still correctly deleted (proving the T377 exclude is scoped to
   exactly the one MCP file).

   Refs T378
   ```
5. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit (stacked on top of T377's commit, same branch) and report completion (commit SHA,
   full test output) back to the orchestrator. T379 and T380 will stack further commits on this same
   branch; T381 will push it and open the MR.

## Constraints
- Token budget: ≤25k tokens.
- File ownership: `tests/functional/test_install_script.py` only.
- No unrelated refactor of this file.
