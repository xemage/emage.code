# Artifact: release-v11-audit-v1.md

> Immutable once produced; revisions bump `<N>`.

# Release-level audit, `v10.0.0..develop`, for v11.0.0

- **Task:** T813 (plan-161 § Task Decomposition item 1). **Author:** tech-lead (read-only on source). **Date:** 2026-11-13.
- **Range:** `v10.0.0..9acf84dc` (develop): 55 commits, 27 of them not merges, 634 files (13218+, 50078-). Most of the files are the removed `.pi/` and `.gemini/` trees (364 paths) and the generated mirrors.
- **Based on:** `docs/tasks/task-T813.md`; `docs/plans/plan-161-release-v11.md` (§ State at writing, § Why MAJOR, § Task Decomposition, § User actions); `docs/artifacts/tracked-debt-register-v16.md` § 5 (batch Q), § 6.1 to § 6.3, § 7, and through it v11 to v15 § 6.2 (items only); `docs/releases/v10.0.0.md`; `docs/releases/_template.md`; ADR-013, ADR-014 (D5/D4, D9/D8, Appendix A); plans 146, 148, 151, 153, 155 to 160 § Outcome; `git log`/`git diff --stat` of the range; targeted reads of `scripts/install.sh`, `.gitlab-ci.yml`, `implementation/scripts/sync.mjs`, `implementation/knowledge/mcp/servers.yaml`, `implementation/runtime/memory/`, `implementation/PREREQUISITES.md`, `implementation/knowledge/agents/release-manager.md`, `docs/artifacts/brave-audit-acceptance-v4.md`, `docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md`.
- **The user's words** (2026-11-13, question dialog, option labels verbatim): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)"; probe tag "Yes, probe first (Recommended)".
- **Line numbers** are on `9acf84dc`, read here unless marked. T815 bumps version markers on the release branch, so **T816 re-reads every cited line on the release branch** before writing it into the document.

## 1. Breaking and behaviour changes

| # | Change | Commit / MR | Citation | Reaches |
|---|---|---|---|---|
| B-1 | **Pi removed** (ADR-013). `--platform pi` (any letter case) exits 1 before any write, in plain install, `--update`, `--projections-only` and `--dry-run`, with "error: platform 'pi' was removed in v11.0.0 (see docs/releases/v11.0.0.md). Existing .pi/ files in your project are not touched. Nothing was written." `--platform all` no longer installs `.pi/`. On `--update`/`--projections-only`, a `.pi/` directory (not a symlink) with a generator marker (`.generated-manifest.json` naming `"platform": "pi"`, or `mcp.json.provenance.json`) gets a stderr notice; `.pi/` is never written, pruned or deleted. | `bed31f34` (!659), root refresh `f43e2dee` (!660) | `scripts/install.sh:20` (`SUPPORTED_PLATFORMS`), `:191-194`, notice `:1308-1327`, called `:1358` from `validate_before_update` (`:1353`) | targets, automation |
| B-2 | **Gemini CLI removed** (ADR-014). Same shape: `--platform gemini` (any case) exits 1 with the matching message; notice on a marked `.gemini/` (`settings.json.provenance.json` or the manifest); never reads `.gemini/settings.json` or `.gemini/.env`; never deletes. | `4d820f54` (!662), root refresh `58a96662` (!663) | `scripts/install.sh:195-198`, notice `:1330-1351`, called `:1359` | targets, automation |
| B-3 | **Authoring/fork refusals that come with B-1/B-2**: manifest enums lose `pi`, `gemini`, `tools: drop`, `mcpToolNames: pi`; the pack schema's `supportedPlatforms` loses `gemini` and `pi`; a leftover `skipFormats` key stops `sync.mjs`; `merge-mcp-json.py --drop-env-form` and the Gemini `excludeTools`/`hooks` handling are gone; the registry's platform list has four entries. | `bed31f34`, `4d820f54` | `implementation/platforms/_manifest.schema.json` (enums), `implementation/registry/package.schema.json`, `implementation/scripts/sync.mjs:208`, `scripts/merge-mcp-json.py` (removed `add_argument("--drop-env-form")`), `implementation/scripts/generate-registry.py` | fork authors |
| B-4 | **context-retriever `--platform-root` is per platform** (QA-T760-03): the generated entry carries `.claude`, `.cline` or `.opencode` instead of `.claude` everywhere. A Cline or Opencode install without `.claude/` now works (`retrieve` failed before), and **SEC-T791-01**: next to `.claude/`, Cline and Opencode sessions now resolve as `cline`/`opencode`, so shared-scope entries naming only `claude-code` are no longer returned to them, and entries naming their platform now are. Reaches a target's `.cline/mcp.json` and `.opencode/opencode.json` at `--update`. | `d69ecad0` (!670), root refresh `0febdb4b` (!671) | `implementation/knowledge/mcp/servers.yaml:184-196`; `implementation/scripts/sync.mjs:224-250`; `implementation/runtime/memory/context_retriever.py:243` | targets using context-retriever |
| B-5 | **Unknown `{{...}}` placeholders in a server's `args` stop `sync.mjs`** (only a whole `{{platformDir}}` is known; an `outputDir` that is not one plain dot-folder name stops the run). | `d69ecad0` | `implementation/scripts/sync.mjs:231-250`, `:1284-1290` | fork authors |
| B-6 | **Memory build and server** (batch Z, batch O): the install notice prints the `requirements.txt` install line (QA-T760-01) and the build line activates `.venv-mcp` first (QA-T792-1); `build.py` refuses a `--project-id` that is not the derived lower-case `<org>/<repo>` (exit 2; QA-T760-02) and names on stderr, by path only, every own-repo project-scope entry whose `project_id` is not `--project-id` (SEC-T791-02); a remote with a `.`/`..` org or repo yields no project id, so the server does not start (default) or every `retrieve` fails (`--index-dir`) (SEC-T791-03); refusal messages redact a remote's userinfo (SEC-T796-01). | `d69ecad0` (!670), `2addaef4` (!673) | `scripts/install.sh:1734-1741`; `implementation/runtime/memory/build.py:45-52`, `:125`, `:239`, `:282`; `context_retriever.py:97`, `:102`, `:149` | targets using the memory index |
| B-7 | **Shipped rule text: ADR-015 and ADR-016.** `validation-gates` § Verdict Rules (C1, D1, D2, W1 to W3) and the release-manager Conditions slots (C2) change what a target's own release gate demands of a user-accepted MEDIUM whose fix is "none possible in the harness" (four validity conditions, the Security Engineer's confirmation before the user is asked) and of a passed deadline. | `f20de1ec` (!676), `018777cb` (!678); root refreshes `ce49d32f` (!677), `8e68b3fe` (!679) | `implementation/knowledge/skills/validation-gates/SKILL.md:70`, `:120`; `implementation/knowledge/agents/release-manager.md:183` | targets' release flow; this repo's release author |
| B-8 | **CI default image** `node:24-alpine@sha256:116b800c…` (Node 24.22.3, Alpine 3.24.4); `node --version` printed in `verify-knowledge-drift`. | `4b7d5c5d` (!667) | `.gitlab-ci.yml:43`, `:134`, record `:13-21` | maintainers |
| B-9 | **CA-chain control** (SEC-T756-02): two jobs, one per pinned image; `unit-tests` installs `openssl~=3.5`; no rule matches a tag. | `4ab4a5b6` (!658) | `.gitlab-ci.yml:151-159` (comment), `:160`, `:181`, `:103-104`; `scripts/check-ca-chains.sh`; `tests/fixtures/ca-chains/` | maintainers |
| B-10 | **Release-gate runner tag**: `tags: ["release-gate"]` on `release-docs-gate`, `main-develop-drift-gate` and `release`, pinned by `runner_tag_problems` in `tests/functional/test_ci_hash_pins.py`. A pipeline without a runner carrying that tag leaves the three tag jobs pending. | `4786feb7` (!681) | `.gitlab-ci.yml:255`, `:282`, `:306` | maintainers, forks that tag |
| B-11 | `unit-tests` fetches the `v10.0.0` tag for `test_install_removed_platform_v11`. | `bed31f34` | `.gitlab-ci.yml:112-116` | maintainers |
| B-12 | Brave record v4 replaces v3 as the accepted set the gate names; the script's help text points at v4. Pins and expiry unchanged. | `44e7c967` (!680) | `scripts/audit-mcp-pins.py` (one help line); `docs/artifacts/brave-audit-acceptance-v4.md` | release author |
| B-13 | Pi/Gemini wording removed from shipped knowledge text (`commands/consolidate-memory.md`, `discover-skills.md`, `skillify.md`, `skills/memory-management`, `skills/skillify`, `agents/context-retriever.md`, `implementation/SECURITY.md`), `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `Makefile` usage, `.gitlab/` templates, `docs/wiki/`, `docs/releases/_template.md` platform table (`:20-26`). Text only. | `bed31f34`, `4d820f54` | as named | targets (text), contributors |

**Version.** B-1 and B-2 remove a supported `--platform` value and a generated tree, which ADR-013 D9 and ADR-014 D8 decided as MAJOR with no deprecation release (precedent v9.0.0, Cursor). B-3 and B-5 refuse inputs that were accepted before; B-4 changes what an existing install's sessions see. Nothing argues for a version other than **MAJOR**, and nothing found here goes beyond what plan-161 § Why MAJOR already says, except B-5 and B-7, which add to the MAJOR case and do not change it. **No change found blocks the release.**

## 2. Migration items for the release document

| # | Item | Source | Exact user-facing action |
|---|---|---|---|
| MI-1 | **Pi is no longer supported** | ADR-013 Appendix A; SEC-T773-02 (item 31) | Breaking-changes entry and Migration Guide item as ADR-013 Appendix A drafts it: `--platform pi` exits 1; `--update`/`--projections-only` no longer touch `.pi/`; to clean up, delete the paths under `files` in `.pi/.generated-manifest.json` except `mcp.json`, then the manifest and empty folders; in `.pi/mcp.json` remove the servers under `generatorOwnedKeys` of `.pi/mcp.json.provenance.json` and keep your own, then delete the sidecar; do not delete `.pi/` as a whole unless nothing else keeps files there; if kept it is **frozen** (MCP pins, Playwright hardening, GitLab grants in `.pi/agents/*.md` get no updates); automation running `--platform pi` or reading `.pi/` after `--platform all` must change; rollback is the v10.x installer, which replaces `.pi/` wholesale. Add that a `.pi/` without a marker gets no notice (SEC-T773-02). The install table already has no Pi row (`_template.md:20-26`); the sentence under the table is still to be written. |
| MI-2 | **Gemini CLI is no longer supported** | ADR-014 Appendix A; SEC-T780-05 (item 31) | As ADR-014 Appendix A: `--platform gemini` exits 1; `.gemini/` no longer touched; **do not delete `.gemini/settings.json` or `.gemini/`**; delete the manifest's `files` except `settings.json`; in `settings.json` remove the servers under `generatorOwnedKeys` of the sidecar and the harness hook under `hooks.AfterTool`, keep every other key; then delete sidecar and manifest; if kept, frozen, and Gemini CLI agents can call every tool of every configured server except the six denied Playwright tools; automation changes; rollback is the v10.x installer, which sweeps `.gemini/` and deletes the user's own files there. |
| MI-3 | **Your own Gemini entries outside `.gemini/`** | A-22 (plan-161 § User actions; ADR-014 Q4 as recorded in plan-146) | Generic form for any adopter: remove Gemini entries you added yourself to your own client settings (for this repository's user: `.vscode/settings.json`, `.claude/settings.json`); the installer never edits them. Whether the user has done A-22 is **(unverified)**. |
| MI-4 | **Cline/Opencode platform identity next to `.claude/`** | SEC-T791-01, item 39; B-4 | After `--update`: Cline and Opencode sessions resolve as `cline`/`opencode`; shared-scope entries naming only `claude-code` are no longer returned to them, entries naming their platform now are. Shared entries meant for every client list each platform or use `["*"]`. A self-install's root changes only after its refresh. Also: a Cline or Opencode install without `.claude/` now gets working `retrieve` (K-35 closed). |
| MI-5 | **Memory build** | item 36 (v14, v15); B-6 | Report as fixed: K-35 (QA-T760-03) closed, keeping the id; M-2's two caveats no longer apply (QA-T760-01, -02); batch O lines (a) to (d) of v15 item 36. **Action** for (b)/(c): a `--project-id` not in the derived lower-case form is refused (exit 2), so scripts passing another case must change; a remote with `.`/`..` as org or repo gives no project id (whether any real host allows such a path is **(unverified)**). Cite the current `install.sh:1735` (requirements line) and `:1739-1741` (build lines). |
| MI-6 | **Node minimum for the `npx` MCP entries** | SEC-T784-01, item 38 | Use Node ≥ 22.23.5, ≥ 24.22.3 or ≥ 26.13.1 for the `npx` entries; "Node.js 18+" is out of date. **`implementation/PREREQUISITES.md:4` still says "Node.js 18+" and `:227` still says `≥ 18`** (read here): the edit is not done (section 3, item 38). |
| MI-7 | **Fork authors of knowledge** | B-3, B-5; ADR-013/014 Appendix A breaking entries | A manifest with `mcp.format`/`mcpToolNames` `pi`, `mcp.format` `gemini` or `tools: drop` fails; a pack listing `pi` or `gemini` is rejected; remove any `skipFormats` key; stop passing `--drop-env-form`; an `args` entry with `{{...}}` other than a whole `{{platformDir}}` stops `sync.mjs` (B-5 is not in any § 6.2 item or Appendix A; section 7). |
| MI-8 | **Release authors and maintainers of this repository** (not for a target) | B-7, B-9, B-10; items 35, 40 | A tag pipeline needs a runner carrying `release-gate`; a digest change of the tag jobs' image needs the runner's `allowed_images` changed with it (`docs/wiki/mcp-pin-bump-checklist.md` § 3, plan-159); both CA-chain jobs must pass on the release commit; a user-accepted MEDIUM with no harness fix needs the ADR-016 conditions in its Conditions line. |

## 3. Register v16 § 6.2, items 1 to 42

Status: **done** (nothing left for v11.0.0), **due at release** (an action in a plan-161 task), **n/a** (no change in the range triggers it), **open** (an action not yet routed or waiting on the user). Source is the register version that last changed the item.

| # | Item (short) | Status | Who, task | Source |
|---|---|---|---|---|
| 1 | T725 migration item | n/a (done at v10.0.0) | — | v12 |
| 2 | MEDIUMs under acceptance: SEC-T660-01, SEC-T665-01, SEC-T702-09 | due at release: the acceptances are recorded (plan-158, plan-160); left are the Conditions lines (section 5), v4's gate command at the release, TD-T808-02's dates | release-manager T816; devops-engineer T814 (gate command); security-engineer T820 checks | v16 |
| 3 | Verdict fields `Issued at commit`, `Independent check` (`_template.md:85-86`) | due at release | release-manager T821 | v12 |
| 4 | TD-T723-01: cite current `install.sh` lines (`:187`, `:1300`, `:1301`, `:1305`, Pi `:1308-1327`, Gemini `:1330-1351`) | due at release (re-read on the release branch) | release-manager T816; tech-lead T819 | v12, v14 |
| 5 | Brave after 2027-01-30 or above 2.1.4 | due at release (as item 42) | devops-engineer T814; orchestrator T822 date check | v11 |
| 6 | D-T710-2 `CHANGELOG.md` below `[Unreleased]` | n/a (observed at v10.0.0; `scripts/publish-release.py` has no diff in the range) | — | v12 |
| 7 | Gate rules of batches G, S, T for the author | due at release (rules hold: `verify-release-docs.py` has no diff) | release-manager T816 | v12 |
| 8 | Not verified live: npm step not in a tag pipeline; musl lock beyond MR pipeline | open (watch; musl lock stays **(unverified)**) | orchestrator T822 (watch) | v12 |
| 9 | Conditions block (`release-manager.md:183`) | due at release | release-manager T816, T821 | v11, v16 (citation note) |
| 10 | Template pointer sentence (`_template.md:88`; SEC-T735-09) | due at release: remove from `v11.0.0.md` before the independent check | release-manager T816/T821 | v11, v12 |
| 11 | Independent checker (`release-manager.md:46`, unchanged) | due at release: `@tech-lead` | tech-lead, within T821 | v11 |
| 12 | Closed list after the check; hotfix eligibility | due at release | release-manager T821 | v11 |
| 13 | Targets receive neither `verify-release-docs.py` nor `_template.md` | done (settled by install at v10, T753); `install.sh` mentions the gate script only in the comment `:1300` (grep here, not an install) | QA re-shows in T818's install | v12 |
| 14 | Watch `release-docs-gate` at the tag | due at release. **Lines moved by plan-159** (after v16): job `.gitlab-ci.yml:252-277`, `tags` `:255`, `timeout` `:263`, removal `:271`, `release` `GIT_STRATEGY: clone` `:311` | orchestrator T822; T817 probe | v13 (lines now as here) |
| 15 | Tag jobs without `allow_failure` | due at release (the three `allow_failure: true` at `:55`, `:210`, `:250` are in jobs before `:252`; that none is a tag job is my reading of the line order, confirm in review) | tech-lead T819 | v11 |
| 16 | A local gate run needs the parser | due at release | release-manager T816; qa-engineer T818 | v11 |
| 17 | Regenerating `ci/requirements-ci.txt` needs the release lock | n/a (`ci/` has no diff) | — | v11 |
| 18 | A new CI job needs a `NOT_TAG_CONDITIONS` `if` | done for the two CA-chain jobs (comment `:159`; suite green per plan-146) | tech-lead T819 confirms | v11 |
| 19 | Digest bump vs. `apk`/Python minor test edit; header recipe `.gitlab-ci.yml:26-30` | n/a unless T814 leads to a bump | devops-engineer, only if a bump task is created | v13 |
| 20 | Checked files valid UTF-8; strict `check-version-consistency.py` | due at release | release-manager T815; qa-engineer T818 | v11 |
| 21 | Allowlisted gate commands; job-shell comment now `.gitlab-ci.yml:272` (moved) | due at release (watch) | orchestrator T822 | v13 |
| 22 | No HTML other than comments in the document | due at release | release-manager T816 | v11 |
| 23 | Release script edit needs `RELEASE_COMMAND`; `script` line now `.gitlab-ci.yml:318` (moved, unchanged text) | n/a (no change to the line) | — | v13 |
| 24 | A release candidate is a full release; a probe tag proves the gates only | n/a (no RC; the probe T817 follows this item's limits) | orchestrator T817 | v11 |
| 25 | Gate limits (131072 chars, nesting 20) | due at release | release-manager T816 | v11 |
| 26 | `run-allowlisted.py` is code with no pin | n/a (no diff) | — | v11 |
| 27 | Placeholders (`_template.md:3`; `CONTRIBUTING.md:224-226`) | due at release | release-manager T816 | v12 |
| 28 | First-tag watch list `CONTRIBUTING.md:280-293`; `main` must not move between tag and tree check | due at release; add the runner checks of plan-159 (`gitlab-runner-16028`, `allowed_images`) | orchestrator T822 | v12 |
| 29 | No `docker` in briefs | due at release (every brief) | orchestrator, all tasks | v12 |
| 30 | No second verdict heading in a real heading or displayed HTML | due at release | release-manager T816/T821 | v11 |
| 31 | ADR-013/014 Appendix A items and frozen-state warnings; reviewed by hand (TL-T780-09); `install.sh` pointer resolves | due at release (pointers `install.sh:192`, `:196`, `:1327`, `:1351` name `docs/releases/v11.0.0.md`) | release-manager T816; tech-lead T819; qa-engineer T818 | v12 |
| 32 | SEC-T657-01/SEC-T658-01 and K-15 closed by removal, with the reopening condition (K-20, A-7, SEC-T658-02) | due at release | release-manager T816; security-engineer T820 | v12 |
| 33 | SEC-T762-04 questions answered (ADR-015, ADR-016) | due at release: state them as ruled, not as open | release-manager T816 | v16 |
| 34 | A-21 before the tag (or by 2027-02-19) | open: the user | the user; orchestrator asks before T822 | v12, v16 § 7 |
| 35 | Both CA-chain jobs (`:160`, `:181`) pass on the release commit, in its branch or MR pipeline | due at release | qa-engineer T818 reads; orchestrator T822 | v13 |
| 36 | K-35 closed, M-2 caveats, batch O lines (a)-(d); cite `install.sh:1739-1741` | due at release | release-manager T816 | v15 |
| 37 | SEC-T786-01: `unit-tests` log for `nodejs` 24.22.3 | due at release | devops-engineer T814; record in T816; re-grade in T820 if still absent | v13 |
| 38 | SEC-T784-01: Node minimums in the document and in `PREREQUISITES.md` | **open: `PREREQUISITES.md:4` and `:227` still name 18; no plan-161 task edits `implementation/PREREQUISITES.md`** | orchestrator routes (suggestion: a small edit before or within T815, reviewed in T819/T820); T816 writes the minimums | v13 |
| 39 | SEC-T791-01 migration note | due at release (MI-4) | release-manager T816 | v14 |
| 40 | ADR-015/016 Conditions duties for SEC-T660-01, SEC-T665-01 | due at release (section 5) | release-manager T816; security-engineer T820; tech-lead T821 check | v16 |
| 41 | T806 note items 1 to 7 | due at release: items 1 to 3 (review, question, words) done by plan-160; 4 (T806 is not the confirming review; T812 is), 5 and 6 (in item 40) and 7 (no ADR-016 conditions for SEC-T702-09) go into T816 | release-manager T816 | v16 |
| 42 | Brave record v4, expiry 2027-01-30; npm newest Brave at preparation | due at release | devops-engineer T814; orchestrator T822 (date) | v16 |

**Counts:** done 2 (13, 18); due at release 30; n/a 7 (1, 6, 17, 19, 23, 24, 26); open 3 (8, 34, 38). Total 42.

## 4. Batch Q (9 ids): route in this release

| Id | Route |
|---|---|
| TD-T723-01 | T816 cites current `install.sh` lines (item 4), re-read on the release branch; T819 checks the citations. |
| SEC-T735-08 | The questions of plan-158/Brave v4 and plan-160 named the release, showed the plan and a deadline ahead (quoted in section 5). T816 records them; T820 confirms. Whether that closes the id is for register v17, not ruled here. |
| SEC-T735-09 | T816 drops the pointer sentence (`_template.md:88`) from `v11.0.0.md` before the independent check (item 10); the template keeps it. |
| SEC-T773-02 | MI-1 with the frozen-state warning and "no notice without a marker" (item 31); T818 shows the notice and that nothing under `.pi/` changes. |
| SEC-T780-05 | MI-2 with the frozen-state warning (item 31); T818 as above for `.gemini/`. |
| TL-T780-09 | T819 reviews MI-1 and MI-2 by hand: the gate checks migration items only on `install.sh` lines with "Cursor". No check is added in this release (plan-161 adds none). |
| SEC-T784-01 | Item 38: `PREREQUISITES.md` edit **not yet routed** (open) and the minimums in T816 (MI-6). |
| SEC-T791-01 | MI-4 in T816 (item 39). |
| TD-T808-02 | T814 reads npm's newest Brave; T822 confirms the tag date is not after 2027-01-30 and no Brave release above 2.1.4 exists; otherwise back to the user. |

## 5. Conditions-line facts for the three accepted MEDIUMs

Facts only; the validity of the acceptances is not ruled here (the orchestrator recorded them). Slots as `implementation/knowledge/agents/release-manager.md:183`; shape as `docs/releases/v10.0.0.md:297-299`.

**SEC-T660-01 and SEC-T665-01** (one line each, or one shared line as v10.0.0 did):
- `risk_accepted_by=@user`, words verbatim: **"Accept for v11.0.0 (Recommended)"**, **2026-11-13**, question dialog (plan-160 § Outcome). The question as shown is in plan-160 § Outcome, "Question" (verbatim; it cites T812 with its date and states the old deadline). The acceptance of 2026-11-12 ("Accept for v11.0.0") is superseded by this one (plan-160 § Outcome).
- `grade=SECURITY:MEDIUM`; `release=v11.0.0`.
- `mitigation=` the plan as shown: owner the user (isolation) and devops-engineer (documentation); fix: none possible in the harness. **Outside closer:** the user, by an isolated OS user, container or VM. **Plain statement** that no harness fix exists, confirmed by **`docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md`, dated 2026-11-13**, a new review for v11.0.0 (T812 header). **Order:** T812 came before the question, which was put on **2026-11-13** (plan-160 § Outcome: "The question was put to the user after T812's review, citing that review"). T806 is not the confirming review (item 41).
- `deadline=` the review on **2027-01-28** (token renewal), which is the plan's deadline (ADR-015) and must still be ahead when v11.0.0 ships; if the release slips to it, the user accepts again (T812 line 67; plan-160 § Outcome). A new acceptance at the next release that ships them.
- **SEC-T660-01 only:** the earlier plan's deadline "the sprint after v8.0.0" has passed, at the latest **2026-11-01** (T812 lines 70 and 132). The release that acceptance was given for: the acceptance with that plan is recorded at `docs/releases/v8.0.0.md:261` ("Accept the risk, plan after the release (Recommended)", 2026-10-15), so **v8.0.0** is my reading; T812 does not name the release, and whether v9.0.0 carried the same deadline is **(unverified)**. T816 states this separately from the v10.0.0 plan's 2027-01-28 review (T812 line 132).
- **SEC-T665-01 only:** no earlier deadline, so the passed-deadline duty does not apply (T812 line 98).

**SEC-T702-09:**
- `risk_accepted_by=@user`, the three answers verbatim with dates (`brave-audit-acceptance-v4.md` § Metadata, Decision 1 to 3): "If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0" (2026-11-12, AskUserQuestion); "Keep the acceptance (Recommended)" (2026-11-12, after the T799 scouting); "1. Keep the acceptance" (2026-11-13, plan-158). The question texts are quoted there.
- `grade=SECURITY:MEDIUM`; `release=v11.0.0`.
- `mitigation=` plan as shown: owner devops-engineer; fix: bump to the first Brave release above 2.1.4. The fix is a bump, so the ADR-015 Rule 1 and ADR-016 conditions do not apply (v4 § Metadata; item 41 point 7). Stdio forced, as v10.0.0's K-28 said.
- `deadline=` 2027-01-30 or the first Brave release above 2.1.4, whichever comes first; the gate command and seven `--accept` entries of v4 carry that expiry (item 42).

**Elsewhere in the document:** the "Accepted for v11.0.0 only" Known Issues section (as v10.0.0 § "Accepted for v10.0.0 only") must no longer say the rules are silent on a passed deadline (item 33); TD-T697-07 (2027-01-29) is not shipped and not accepted (plan-161 § State at writing).

## 6. What the release document must not assume

1. That target projects receive `scripts/verify-release-docs.py`, `docs/releases/_template.md`, `.gitlab-ci.yml`, `scripts/check-ca-chains.sh` or `docs/` (item 13 settles the first two by install; the others are **(unverified)** here, grep only).
2. That the installer deletes or cleans `.pi/` or `.gemini/`: it never does, and a tree without a marker gets no notice.
3. That the Node minimums are enforced: nothing in the range checks the user's Node version for `npx` entries **(unverified)**; and that `unit-tests` runs Node 24.22.3 (SEC-T786-01, until T814 reads the log).
4. Live client behaviour: the per-agent denials on Opencode, the tool narrowing on Copilot/VS Code, and the Cline/Opencode platform identity (SEC-T791-01) are from documentation, source reading and test installs, not live clients (K-20, A-7) **(unverified live)**.
5. The release-gate runner: that the three jobs run on runner #59129270 through `gitlab-runner-16028` and that `allowed_images` match. Only a tag pipeline proves it; the probe T817 proves the two gates, not `release`. SEC-T811-01 and -02 rest on the user's report (nobody read GitLab).
6. A-21 and A-22 as done (both **(unverified)**).
7. That the dates hold: the tag before 2027-01-28, and no Brave release above 2.1.4 before the tag (T814/T822).
8. That a real host allows `.`/`..` as org or repo (SEC-T791-03) **(unverified)**.
9. That `main` is an ancestor of `develop` (it is not: plan-161 § State at writing).

## 7. Changes since v10.0.0 not covered by any § 6.2 item

- **U-1 (B-5):** the `sync.mjs` refusal of unknown `{{...}}` placeholders in `args`. Fork-author facing; suggested in MI-7.
- **U-2 (B-7):** the ADR-015/ADR-016 rule text reaches targets' `validation-gates` skill and release-manager agent. Items 33, 40 and 41 cover this repository's document, not what targets receive. Suggested as a "behaviour change to brief your team on" line (like v10.0.0 M-8).
- **U-3 (B-10):** the `release-gate` runner tag. For maintainers and forks that tag: without such a runner the tag jobs stay pending. SEC-T741-17 is batch S, not a § 6.2 item. Suggested for MI-8 and Known Issues "Release pipeline, for maintainers".
- **U-4 (B-9, B-11):** `unit-tests` now needs `openssl~=3.5` and the `v10.0.0` tag fetch. Maintainers only; item 35 covers only the CA-chain jobs. Internal changelog line.
- **U-5 (B-3, partly):** the registry's platform list and `merge-mcp-json.py` changes are in Appendix A; the `generate-registry.py` platform list and `Makefile` usage are not, but they follow from the removals. Changelog only.
- **Citation drift:** register v16 says `.gitlab-ci.yml` did not change in its range; plan-159 (after v16) inserted the `tags` lines, so items 14, 21 and 23 cite new lines (section 3). Items 19 (`:26-30`) and 35 (`:160`, `:181`) are before the inserts and stand.

## 8. Method and limits

- Read: the inputs above, by section; diffs by `git diff -U0` on the named source files; line numbers by `grep -n`/`sed -n` on `9acf84dc`. Not read: the mirrors, `tests/golden/`, the registers' other sections, the full T812/T806/T811 reviews (only the cited lines), `docs/wiki/` diffs. No test, install or pipeline was run beyond the two gates in the report.
- The MR number of each commit comes from the merge commits' bodies in the range.
- Review mode: read-only; no source modified; only this artifact created.
