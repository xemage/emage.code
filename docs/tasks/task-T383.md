# Task T383 — Add literal-secret guard for generated MCP outputs (P2)

**ID:** T383
**Owner:** security-engineer
**Status:** pending
**Priority:** P2
**Depends on:** T381
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-07)

This brief is self-contained. You do not need to read plan-033 to execute this task, though T381
must already be merged to `develop` before you start (this task's branch is cut from post-T381
`develop`; the actual functional dependency is loose — see Blocker protocol if T381 isn't merged
yet).

## Objective
No automated CI/test guard exists today that would catch a *future* accidental literal-secret
commit to a generated MCP/settings output file. This matters because it already happened once:
`implementation/knowledge/mcp/servers.yaml`'s `toolradar` entry carries an explicit code comment
recording that v1 of this repo leaked a live `TOOLRADAR_API_KEY` value (`tr_live_…`) directly into
`.vscode/mcp.json`, `.opencode/opencode.json`, and `.gemini/settings.json` before it was fixed to use
an env-var placeholder. Add a minimal, deterministic, regex-based guard — as a new automated test —
that fails if any credential value in a generated MCP output file is anything other than the
generator's own placeholder syntax.

## Inputs (exact paths, verified against the current file — re-verify before implementing; see
Blocker protocol)

**1. `/home/emage/Code/emage/emage.code/implementation/knowledge/mcp/servers.yaml`** — the source of
truth for which env vars are `secret: true` (currently three: `GITLAB_PERSONAL_ACCESS_TOKEN` in
`gitlab`'s `env` block, `BRAVE_API_KEY` in `brave`'s `env` block, `TOOLRADAR_API_KEY` in
`toolradar`'s `env` block — quoted verbatim from the current file):
```yaml
  gitlab:
    ...
    env:
      GITLAB_PERSONAL_ACCESS_TOKEN: { fromEnv: GITLAB_PERSONAL_ACCESS_TOKEN, secret: true }
      GITLAB_API_URL: { fromEnv: GITLAB_API_URL }
  ...
  brave:
    ...
    env:
      BRAVE_API_KEY: { fromEnv: BRAVE_API_KEY, secret: true }
  ...
  toolradar:
    ...
    env:
      # SECURITY: never inline a real key here. Set TOOLRADAR_API_KEY in your shell
      # or your platform's secret store. v1 leaked a live key — do not repeat.
      TOOLRADAR_API_KEY: { fromEnv: TOOLRADAR_API_KEY, secret: true }
```
Re-verify this is still the current list of `secret: true` entries yourself
(`grep -n "secret: true" implementation/knowledge/mcp/servers.yaml`) before hardcoding it — do not
assume this brief's snapshot is current if it disagrees.

**2. Confirmed placeholder syntax per platform (from this plan's own investigation, Finding #4 —
already independently audited, cited here as established fact, not re-derived from scratch):** every
`env`/`environment` value across all 7 platforms' current generated output uses `${env:VAR}` for
`vscode`/`cursor`/`gemini`/`pi`/`cline`/`claude-code`, or `{env:VAR}` for `opencode`. No literal
secret exists in any currently-generated file — this guard is defense-in-depth against a *future*
regression, not a fix for a current problem.

**3. Files to scan** — every generated MCP/settings output file, both `implementation/`'s canonical
copies and this repo's root self-install mirror:
```
implementation/.vscode/mcp.json    implementation/.cursor/mcp.json
implementation/.gemini/settings.json    implementation/.opencode/opencode.json
implementation/.pi/mcp.json    implementation/.cline/mcp.json    implementation/.mcp.json
.vscode/mcp.json    .cursor/mcp.json    .gemini/settings.json
.opencode/opencode.json    .pi/mcp.json    .cline/mcp.json    .mcp.json
```
Confirm this exact list of 14 files all exist before writing the test (`ls` each path) — if any is
missing, that's a discrepancy to report, not silently skip.

**4. Existing test-suite conventions to follow** — `tests/functional/test_platform_projections.py`
already does exact-shape assertions against `sync.mjs`'s output and has a `_remote_server_urls()`
helper sourcing expected values from `servers.yaml` (added by T363); read it for the repo's
established pattern of "parse `servers.yaml`, then assert against generated output," but do not
modify that file — this task adds a new, separately-named test module (see Allow-list).

## Allow-list (files you may create/touch)
- A NEW file: `tests/functional/test_mcp_secret_guard.py`. This is a new test module, not an
  extension of an existing one — the plan explicitly scopes this as "a minimal regex-based guard
  (test or CI job)," and no existing test file's purpose already covers credential-value scanning.

## Deny-list (do not touch — no exceptions)
- Do NOT edit `implementation/knowledge/mcp/servers.yaml`, `implementation/scripts/sync.mjs`,
  `scripts/install.sh`, `scripts/merge-mcp-json.py`, or any generated MCP output file.
- Do NOT edit `tests/functional/test_platform_projections.py` or any other existing test file.
- Do NOT wire this new test into `.gitlab-ci.yml` directly — `tests/run.py` auto-discovers test
  modules under `tests/functional/` (confirm this yourself: check how `tests/run.py` selects test
  modules — if it does NOT auto-discover and requires explicit registration, STOP and report a
  blocker rather than guessing at CI wiring, since editing `.gitlab-ci.yml` is outside this task's
  described scope of "a test or CI job" without further orchestrator confirmation of which).
- Do NOT create any new branch beyond the one specified in Git workflow below.

## Exact guard implementation (reference — you may implement differently as long as the three
required test behaviors below all hold)

```python
"""Guard against literal (non-placeholder) secret values in generated MCP output.

Defense-in-depth for the class of leak recorded in
implementation/knowledge/mcp/servers.yaml's toolradar entry (v1 leaked a live
TOOLRADAR_API_KEY value directly into three generated files before the fix to
env-var placeholder syntax). This test asserts every credential-bearing `env`
block value in every generated MCP/settings output file is the generator's
own placeholder syntax, never a literal string.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

# ${env:VAR} (vscode/cursor/gemini/pi/cline/claude-code) or {env:VAR} (opencode).
ALLOWED_ENV_VALUE_RE = re.compile(r"^\$?\{env:[A-Z][A-Z0-9_]*\}$")

GENERATED_MCP_FILES = [
    "implementation/.vscode/mcp.json",
    "implementation/.cursor/mcp.json",
    "implementation/.gemini/settings.json",
    "implementation/.opencode/opencode.json",
    "implementation/.pi/mcp.json",
    "implementation/.cline/mcp.json",
    "implementation/.mcp.json",
    ".vscode/mcp.json",
    ".cursor/mcp.json",
    ".gemini/settings.json",
    ".opencode/opencode.json",
    ".pi/mcp.json",
    ".cline/mcp.json",
    ".mcp.json",
]


def find_literal_env_values(data) -> list[tuple[str, str]]:
    """Recursively find (key, value) pairs inside any 'env' dict whose value
    is not the generator's placeholder syntax. Returns a list of violations."""
    violations: list[tuple[str, str]] = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "env" and isinstance(value, dict):
                    for env_key, env_value in value.items():
                        if isinstance(env_value, str) and not ALLOWED_ENV_VALUE_RE.match(env_value):
                            violations.append((env_key, env_value))
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return violations


class TestMcpSecretGuard(unittest.TestCase):
    def test_no_literal_secrets_in_generated_mcp_output(self):
        for rel_path in GENERATED_MCP_FILES:
            path = repo_root() / rel_path
            if not path.is_file():
                self.fail(f"expected generated MCP file missing: {rel_path}")
            with self.subTest(file=rel_path):
                data = json.loads(path.read_text(encoding="utf-8"))
                violations = find_literal_env_values(data)
                self.assertEqual(
                    violations, [],
                    msg=f"{rel_path} has literal (non-placeholder) env value(s): {violations}",
                )

    def test_guard_detects_injected_literal_secret(self):
        fixture = {
            "mcpServers": {
                "toolradar": {
                    "command": "npx",
                    "args": ["-y", "toolradar-mcp"],
                    "env": {"TOOLRADAR_API_KEY": "tr_live_FAKEVALUEFORTESTONLYNOTREAL"},
                }
            }
        }
        violations = find_literal_env_values(fixture)
        self.assertEqual(
            violations, [("TOOLRADAR_API_KEY", "tr_live_FAKEVALUEFORTESTONLYNOTREAL")],
            msg="guard must detect a deliberately-injected literal secret-shaped value",
        )

    def test_guard_allows_placeholder_syntax(self):
        fixture = {
            "mcpServers": {
                "gitlab": {"env": {"GITLAB_PERSONAL_ACCESS_TOKEN": "${env:GITLAB_PERSONAL_ACCESS_TOKEN}"}},
                "brave": {"env": {"BRAVE_API_KEY": "${env:BRAVE_API_KEY}"}},
            },
            "mcp": {
                "toolradar": {"env": {"TOOLRADAR_API_KEY": "{env:TOOLRADAR_API_KEY}"}},
            },
        }
        violations = find_literal_env_values(fixture)
        self.assertEqual(violations, [], msg="legitimate placeholder syntax must not false-positive")


if __name__ == "__main__":
    unittest.main()
```
Note: this fixture-based design deliberately does NOT depend on `${input:...}` syntax (used by the
hand-added `cwso` block in root `.vscode/mcp.json`, under `headers`, not `env`) — that block is
outside this guard's scope (it's not a `servers.yaml`-generated entry, and it's not inside an `env`
dict), so it correctly never triggers a false positive without needing special-case handling.

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Targeted run of the new module:
   ```
   python3 -m unittest tests.functional.test_mcp_secret_guard -v
   ```
   PASS = `Ran 3 tests`, `OK`, exit 0.

2. Confirm test discovery actually picks up the new file (before assuming `tests/run.py` will find
   it automatically):
   ```
   grep -n "discover\|glob\|test_\*.py\|functional" tests/run.py | head -20
   ```
   Use this output to confirm the discovery mechanism, then:
   ```
   python3 tests/run.py --suite functional -v 2>&1 | grep -i "mcp_secret_guard"
   ```
   PASS = at least one line mentioning `test_mcp_secret_guard` appears, confirming the new module was
   picked up without any registration edit. If nothing appears, STOP — see Blocker protocol (do not
   guess at wiring it in yourself).

3. Full suite:
   ```
   python3 tests/run.py
   ```
   PASS = exits 0, count increased by exactly 3 from your own recorded baseline.

## Acceptance criteria (all must be true)
- [ ] `git status` shows exactly one new file: `tests/functional/test_mcp_secret_guard.py`. No
      existing file modified.
- [ ] `test_no_literal_secrets_in_generated_mcp_output` passes against the current (clean) generated
      output — confirms no false positive on real data.
- [ ] `test_guard_detects_injected_literal_secret` fails-to-pass-through a deliberately-injected
      literal-secret-shaped fixture (i.e. the guard function correctly flags it) — confirms the guard
      actually detects a violation, not just always passing.
- [ ] `test_guard_allows_placeholder_syntax` passes on legitimate `${env:VAR}`/`{env:VAR}` syntax for
      all three currently-`secret: true` env vars — confirms no false positive on the exact syntax
      the generator produces.
- [ ] The new test module is picked up by `tests/run.py` without any additional wiring (test 2), or a
      blocker was raised if it isn't.
- [ ] `python3 tests/run.py` exits 0 with count increased by 3 from your own recorded baseline.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- Any of the 14 files in "Files to scan" doesn't exist at the stated path → `type: dependency`,
  `severity: minor` — report which file(s) are missing; do not silently drop them from the list.
- `servers.yaml`'s `secret: true` entries have changed from the three listed above → `type:
  dependency`, `severity: minor` — update your understanding from the actual current file; the guard
  itself does not hardcode which vars are secret (it checks ALL `env` dict values, not just the
  three flagged ones), so this shouldn't require an implementation change, but note the discrepancy.
- `tests/run.py`'s discovery mechanism does NOT automatically pick up the new module (test 2 finds
  nothing) → `type: technical`, `severity: minor` — report the exact discovery mechanism found in
  `tests/run.py` and ask the orchestrator whether editing `.gitlab-ci.yml` or `tests/run.py` itself
  is in scope, rather than guessing.
- `test_no_literal_secrets_in_generated_mcp_output` genuinely fails against real current data (i.e.
  a real literal secret is found) → `type: technical`, `severity: critical` — do NOT paste the
  actual discovered value anywhere (not in your report, not in a commit, not in chat) per this
  repo's security guidelines; report only the file name and env-var key name, and escalate
  immediately as a security incident rather than a normal test failure.
- Any verification command fails for an unrelated reason → `type: technical`, `severity: major`,
  include exact output.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Confirm T381 has merged to `develop` (`git log origin/develop --oneline | grep -i "T377\|T378\|
   T379\|T380"` returns at least one commit); if not yet merged, this task has no strict functional
   blocker on it (the guard doesn't depend on T377-T380's content) — you may still proceed, but
   branch from the current `develop` tip either way.
2. Create branch `test/T383-mcp-secret-guard` from the current tip of `develop`.
3. Create the new test file; run all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   test(mcp): add literal-secret guard for generated MCP/settings output

   Defense-in-depth against the class of leak recorded in servers.yaml's
   toolradar entry (v1 leaked a live TOOLRADAR_API_KEY value directly into
   three generated files). New test recursively scans every 'env' dict in
   all 14 generated MCP/settings output files (implementation/ canonical
   copies + repo-root self-install mirror) and fails if any value isn't
   the generator's own ${env:VAR}/{env:VAR} placeholder syntax. Includes a
   self-test proving the guard actually detects an injected literal value,
   not just always passing.

   Refs T383
   ```
5. Push the branch, open a merge request to `develop` referencing T383, wait for CI to go green,
   then STOP — do NOT merge yourself. Report completion to the orchestrator for independent
   re-review and merge.
6. Do NOT push to `develop` or `main` directly under any circumstance.

## Constraints
- Token budget: ≤10k tokens.
- File ownership: `tests/functional/test_mcp_secret_guard.py` only (new file).
- No edits to `.gitlab-ci.yml` without explicit orchestrator confirmation per the Blocker protocol.
