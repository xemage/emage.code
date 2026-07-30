# Task T294 — Extend test coverage for the `claude-code` platform

**ID:** T294
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T293
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T294

## Why this task exists
The functional test suite hardcodes platform lists in several places
(`_TARGET_PLATFORMS` in `test_platform_projections.py`, the required-platform
tuple in `test_manifests.py`). Without extending them, CI would keep passing
even if `claude-code`'s projection silently broke — the new platform would be
invisible to the generic drift/shape tests. This task also adds
platform-specific assertions for the two new sync-engine features (`tools`
as a string, `.mcp.json` shape) and for the installer's `claude-code` wiring,
mirroring the existing `opencode`/`github`-specific tests already in the
suite.

## STOP-RULES (read before touching anything)
- Confirm T293 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T294 (missing dependency)`.
- **R2** This task touches **EXACTLY FOUR FILES**:
  `tests/functional/test_manifests.py`,
  `tests/functional/test_platform_projections.py`,
  `tests/functional/test_install_agents_mapping.py`,
  `tests/functional/test_install_script.py`.
- Do NOT modify `implementation/scripts/sync.mjs`, any `implementation/platforms/*.json`,
  or any generated `implementation/.claude/**` file to make a test pass. If a
  test fails, the bug is upstream (T285–T291) — STOP and report which task ID
  needs rework.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `test: T294 extend platform test coverage for claude-code`

## Edit 1 — `tests/functional/test_manifests.py` required-platform tuple

**FIND this exact block (occurs exactly once):**
```python
    def test_at_least_four_platforms(self):
        manifests = list_platform_manifests()
        names = [p.stem for p in manifests]
        for required in ("github", "gemini", "opencode", "cursor"):
            self.assertIn(required, names, f"missing platform manifest: {required}")
```

**REPLACE WITH exactly this block:**
```python
    def test_at_least_four_platforms(self):
        manifests = list_platform_manifests()
        names = [p.stem for p in manifests]
        for required in ("github", "gemini", "opencode", "cursor", "claude-code"):
            self.assertIn(required, names, f"missing platform manifest: {required}")
```

## Edit 2 — `tests/functional/test_platform_projections.py` `_TARGET_PLATFORMS`

**FIND this exact line (occurs exactly once):**
```python
_TARGET_PLATFORMS = ("github", "gemini", "opencode")
```

**REPLACE WITH exactly this line:**
```python
_TARGET_PLATFORMS = ("github", "gemini", "opencode", "claude-code")
```

## Edit 3 — `tests/functional/test_platform_projections.py` add `tools: string` test

**FIND this exact block (occurs exactly once — note the blank line before
`def test_github_agent_aliases_match_filename_slugs`):**
```python
        for orchestrator in ("orchestrator", "poc-orchestrator"):
            fm, _ = parse_file(opencode_agents / f"{orchestrator}.md")
            self.assertTrue(
                fm.get("user-invocable") is True,
                f"{orchestrator}.md: user-invocable must be true in Opencode projection",
            )

    def test_github_agent_aliases_match_filename_slugs(self):
```

**REPLACE WITH exactly this block:**
```python
        for orchestrator in ("orchestrator", "poc-orchestrator"):
            fm, _ = parse_file(opencode_agents / f"{orchestrator}.md")
            self.assertTrue(
                fm.get("user-invocable") is True,
                f"{orchestrator}.md: user-invocable must be true in Opencode projection",
            )

    def test_claude_code_agents_use_tools_string(self):
        claude_agents = _generated_root("claude-code") / "agents"
        source_agents_dir = knowledge_root() / "agents"

        for path in sorted(claude_agents.glob("*.md")):
            source_fm, _ = parse_file(source_agents_dir / f"{path.stem}.md")
            projected_fm, _ = parse_file(path)
            source_tools = source_fm.get("tools", [])
            projected_tools = projected_fm.get("tools")
            with self.subTest(agent=path.stem):
                self.assertIsInstance(projected_tools, str, f"{path.name}: tools should be a string")
                self.assertEqual(
                    [t.strip() for t in projected_tools.split(",")],
                    source_tools,
                    f"{path.name}: tools string must list source tools in order",
                )

    def test_github_agent_aliases_match_filename_slugs(self):
```

## Edit 4 — `tests/functional/test_platform_projections.py` add `.mcp.json` shape check

**FIND this exact block (occurs exactly once):**
```python
        vscode_mcp = json.loads(
            (implementation_root() / ".vscode" / "mcp.json").read_text(encoding="utf-8")
        )
        self.assertIn("servers", vscode_mcp)
        self.assertIn("gitlab", vscode_mcp["servers"])
        self.assertIn("context7", vscode_mcp["servers"])


if __name__ == "__main__":
    unittest.main()
```

**REPLACE WITH exactly this block:**
```python
        vscode_mcp = json.loads(
            (implementation_root() / ".vscode" / "mcp.json").read_text(encoding="utf-8")
        )
        self.assertIn("servers", vscode_mcp)
        self.assertIn("gitlab", vscode_mcp["servers"])
        self.assertIn("context7", vscode_mcp["servers"])

        claude_code_mcp = json.loads(
            (implementation_root() / ".mcp.json").read_text(encoding="utf-8")
        )
        self.assertIn("mcpServers", claude_code_mcp)
        self.assertIn("gitlab", claude_code_mcp["mcpServers"])
        self.assertIn("context7", claude_code_mcp["mcpServers"])
        self.assertEqual(claude_code_mcp["mcpServers"]["context7"].get("type"), "http")


if __name__ == "__main__":
    unittest.main()
```

## Edit 5 — `tests/functional/test_install_agents_mapping.py` add claude-code test + extend all-platform test

**FIND this exact block (occurs exactly once):**
```python
    def test_all_platform_install_includes_projection_map(self) -> None:
        with tempfile.TemporaryDirectory(prefix="emage-install-all-") as tmp:
            content = self._run_install(Path(tmp), "all")

        self.assertIn("`.github/skills/`", content)
        self.assertIn("`.cursor/skills/`", content)
        self.assertIn("`.gemini/skills/`", content)
        self.assertIn("`.opencode/skills/`", content)
        self.assertIn("`.pi/skills/`", content)
        self.assertIn("`.vscode/mcp.json`", content)
        self.assertIn("`.gemini/settings.json`", content)
        self.assertIn("`.opencode/opencode.json`", content)


if __name__ == "__main__":
    unittest.main()
```

**REPLACE WITH exactly this block:**
```python
    def test_claude_code_install_rewrites_agents_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="emage-install-claude-") as tmp:
            content = self._run_install(Path(tmp), "claude-code")

        self.assertIn("`.claude/skills/`", content)
        self.assertIn("`.claude/rules/coding-standards.md`", content)
        self.assertIn("`.claude/rules/security-guidelines.md`", content)
        self.assertIn("`.mcp.json`", content)

    def test_all_platform_install_includes_projection_map(self) -> None:
        with tempfile.TemporaryDirectory(prefix="emage-install-all-") as tmp:
            content = self._run_install(Path(tmp), "all")

        self.assertIn("`.github/skills/`", content)
        self.assertIn("`.cursor/skills/`", content)
        self.assertIn("`.gemini/skills/`", content)
        self.assertIn("`.opencode/skills/`", content)
        self.assertIn("`.pi/skills/`", content)
        self.assertIn("`.claude/skills/`", content)
        self.assertIn("`.vscode/mcp.json`", content)
        self.assertIn("`.gemini/settings.json`", content)
        self.assertIn("`.opencode/opencode.json`", content)


if __name__ == "__main__":
    unittest.main()
```

## Edit 6 — `tests/functional/test_install_script.py` add root-file placement test

**FIND this exact block (occurs exactly once):**
```python
            self.assertIn("Append-only log. Entries move here", completed)
            self.assertIn("Per-task briefs live alongside", active)
            self.assertNotIn("> Keep this note.", active)


if __name__ == "__main__":
    unittest.main()
```

**REPLACE WITH exactly this block:**
```python
            self.assertIn("Append-only log. Entries move here", completed)
            self.assertIn("Per-task briefs live alongside", active)
            self.assertNotIn("> Keep this note.", active)

    def test_claude_code_install_places_root_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="claude-code")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((target / "CLAUDE.md").is_file())
            self.assertTrue((target / ".mcp.json").is_file())
            self.assertTrue((target / ".claude" / "agents").is_dir())


if __name__ == "__main__":
    unittest.main()
```

## Expected outputs
- The 4 files listed in STOP-RULES modified with the 6 edits above (2 edits
  land in `test_platform_projections.py`).

## Acceptance criteria
1. Syntax check:
   ```bash
   python3 -m py_compile tests/functional/test_manifests.py tests/functional/test_platform_projections.py tests/functional/test_install_agents_mapping.py tests/functional/test_install_script.py
   ```
   Expected: no output, exit code `0`.
2. Run the four touched test modules directly:
   ```bash
   python3 -m unittest tests.functional.test_manifests tests.functional.test_platform_projections tests.functional.test_install_agents_mapping tests.functional.test_install_script -v
   ```
   Expected: all tests `OK`, exit code `0`. If any test fails, identify
   whether the failure is a bug in this task's edits (fix it) or a defect in
   an upstream generated artifact (T285–T291) — in the latter case, STOP and
   report the exact upstream task ID rather than patching the test to hide
   the failure.
3. Verify command — new test names are present:
   ```bash
   grep -Fc "def test_claude_code_agents_use_tools_string" tests/functional/test_platform_projections.py
   grep -Fc "def test_claude_code_install_rewrites_agents_paths" tests/functional/test_install_agents_mapping.py
   grep -Fc "def test_claude_code_install_places_root_files" tests/functional/test_install_script.py
   ```
   Expected output: `1` for each.
4. `git status --porcelain` lists exactly four modified files (the ones in
   STOP-RULES).

## Revert rule
If any verify command fails:
```bash
git checkout -- tests/functional/test_manifests.py tests/functional/test_platform_projections.py tests/functional/test_install_agents_mapping.py tests/functional/test_install_script.py
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.
If a test fails because an upstream artifact is wrong, name the exact task ID
to re-open (T285–T291) rather than editing the test to match broken behavior.

## Execution notes
<filled during execution>
</content>
