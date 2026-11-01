# Artifact: security-review-t662-cursor-removal-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell: no installer, generator, test or `git diff` was run; `grep_content` failed on the worktree, so full reads were used; the 1299-line installer was read in full). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-16.
- **Target**: T662 (ADR-010 step S1, Cursor removal), commits `8f6e19f9` (Pi format rename) and `bf6cfdf6` (removal), reviewed; then `8191c3c9` (the review's conditions) on `agent/devops-engineer/T662` (from develop `17fe179`).
- **Based on**: `docs/tasks/task-T662.md`, `docs/decisions/ADR-010-drop-cursor-platform-support.md` (accepted 2026-10-16), `docs/artifacts/cursor-removal-inventory-v1.md`.
- **Orchestrator checks**: the developer reports 1365 tests OK (skipped 23) and all gates after the last commit; the two touched test modules (27 tests) pass with `CI=true` and the real `git archive v8.0.0` upgrade tests ran, not skipped; the root drift baseline equals `--print-drift` (29 paths: the 28 T663 Opencode paths plus `AGENTS.md`).

## Verdict: CONDITIONAL_PASS (conditions met in `8191c3c9`, except the release-time item below)

0 critical, 0 high, 2 medium, 5 low. No Immutable Security Constraint is breached; no required control is removed or weakened. The only control that disappears is the `.cursor` symlink guard, which is no longer needed because nothing writes `.cursor`. The change is strictly safer than v8: the `--update` sweep (`rsync --delete` or `rm -rf`) that deleted user files in `.cursor/` is gone.

## What the review verified

- **Early validation** (`install.sh:93-107`) runs right after argument parsing and before `--target` handling, `resolve_abs_path`, the repo-root refusals, `guard_managed_paths`, `mkdir -p "$TARGET"`, `require_existing_install` and `validate_before_update`, identically in plain, `--update`, `--projections-only` and `--dry-run`; `--platform cursor` exits 1 even without `--target`, with a two-line message and nothing written; `all` is the default and is allow-listed; `list_managed_paths` and the dispatch agree on the six platforms.
- **The notice** is read-only (only `[[ -d ]]`, `[[ -L ]]`, `[[ -f ]]`, `grep -Eq` and `echo` to stderr); there is no `rm`, `mv`, `cp`, `rsync` or `mkdir` that names `.cursor` anywhere in the installer; a symlinked `.cursor` or marker is not followed; the marker content is matched by a fixed regex and never printed or interpolated; false positives are essentially none.
- **Pi rename**: `format: "cursor"` now fails with `Unknown MCP format: cursor` (fail-closed for forks); `.pi/mcp.json`, `implementation/.pi/mcp.json` and the Pi sidecar are identical to the develop checkout.
- **Registry and pack schema** list the six current platforms (`additionalProperties: false` intact); no other live Cursor code remains; removing the root `.cursor/` leaves the other trees unaffected.

## Findings and dispositions

| ID | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T662-01 | SECURITY:MEDIUM (A05, A06) | The D8 residual (a stale `.cursor/mcp.json` is never pruned again; a v7.x install keeps `npx -y @anthropic/mcp-filesystem`, older ones `e2b-mcp` and similar) was disclosed only as a stderr pointer to `docs/releases/v9.0.0.md`, which does not exist yet | Notice made self-sufficient in `8191c3c9`: it names the `filesystem` entry and the keys `e2b`, `redis`, `figma`, `notion`, and says `--force-prune-keys` exists only in the v8.0.0 installer; the removal message now says "the v8.x releases are the last that support it". **Open until the v9.0.0 release (owner release-manager with technical-writer, T678): `docs/releases/v9.0.0.md` must carry the Cursor Migration Guide item of ADR-010 Appendix A with the M-9 steps, the v5.0.0 to v6.9.0 keys, the statement that `--force-prune-keys` is only available from the `v8.0.0` tag, and the Known Issue "a Cursor install left in a project is frozen and is not pruned"; the release gate must check that the pointer target exists** |
| SEC-T662-02 | SECURITY:MEDIUM (A08) | The only real-v8.0.0 upgrade test skipped silently when the tag was missing; CI uses `GIT_DEPTH 20` and no tag fetch | Fixed in `8191c3c9`: `setUpClass` fails (AssertionError) instead of skipping when `CI` is set; the `unit-tests` job fetches the tag (`git fetch --depth=1 origin tag v8.0.0`); the rsync variant runs only where rsync exists and the cp variant always runs (the CI image has no rsync). Unverified until the first pipeline: the shallow tag fetch on a runner |
| SEC-T662-03 | LOW (A04, A05) | The supported-platform list is written in four places in `install.sh` (usage, early validation `case`, `list_managed_paths`, dispatch); an unknown name in the guard list fails open | Case-insensitive handling of `Cursor`/`CURSOR` added in `8191c3c9`; the duplicated lists stay tracked debt (T672): derive them from one `SUPPORTED_PLATFORMS` array tied by a test to the platform manifests |
| SEC-T662-04 | LOW (A03, A09) | The echoed platform value was sanitised with a locale-dependent class | Fixed in `8191c3c9` (`LC_ALL=C` with `[^ -~]`; test under three locales with ESC, BEL, newline, U+202E and an accented character) |
| SEC-T662-05 | LOW (A09) | Notice detection has known false negatives (installs older than the manifest or sidecar; a plain install prints no notice), and one claim ("Playwright hardening frozen") was stronger than the facts | Claim removed in `8191c3c9`; the plain-install behaviour is documented in the test docstring; the false negatives are accepted |
| SEC-T662-06 | LOW (A05) | The by-name absence test checked the filesystem, not tracked files; the manifest scan only sees trees that carry a manifest | Fixed in `8191c3c9` (`git ls-files`; skip outside a checkout, fail under CI); the filesystem orphan guard is kept |
| SEC-T662-07 | LOW (A05; pre-existing, unchanged) | `mkdir -p "$TARGET"` runs unconditionally, so `--dry-run` creates the target for a valid platform | Tracked debt (T672) |

## For T678 and T679

- **T678 (documentation)** changes: the platform counts (README and `implementation/README.md` "seven platforms"; `docs/wiki/mcp-servers.md:275` "all 7 platforms" to 6; `context-retriever.md:30` "other 6" to 5; `skillify.md:50-53` "seven folders"/"other six" to six/five; `test_root_install_parity.py:3` "eight platform trees" to seven); both `AGENTS.md` files (the Knowledge Base line, the `extended` row, the sentences about Cursor in the MCP section; K-15 and K-16 keep Opencode, Gemini CLI and Pi); the README platform and `--platform` tables plus a short migration paragraph; `PREREQUISITES.md` ("Cursor 0.42+"), `SECURITY.md:25`, `CONTRIBUTING.md` (the `cursor.json` template advice and the `pi.json`-reuses-`cursor` lesson), the eight wiki pages, `docs/releases/_template.md:23`, the two `.gitlab` templates, and the clause "recorded before Cursor was removed" where live docs cite immutable artifacts. The release-manager owns the v9.0.0 release document: the `--platform cursor` exit-1 Breaking entry, the `all` meaning change, the Cursor migration item (SEC-T662-01), the pack-author note and the fork note about `mcp.format: "cursor"`.
- **T679 (root refresh)**: `install.sh --projections-only --platform all`, empty the drift list and add the "Emptied" line; touch the source mtimes first in a fresh worktree.

## Limits

L-1 no shell (no installer, generator, test, gate or `git diff` run by the reviewer); L-2 `grep_content` failed on the worktree; L-3 the edited count-sensitive tests, `test_manifests.py`, `test_install_script.py`, `test_install_type_conflicts.py` and `test_install_projections_only.py` were not read in full, and the deletion of the 182 files was not enumerated; L-4 whether the runner fetches the `v8.0.0` tag under `GIT_DEPTH 20` is unverified; L-5 the other trees' sweep behaviour is judged unchanged by reading, not by a diff; L-6 no held-out, `.env*`, credential or local settings file was opened.
