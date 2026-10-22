# Artifact: security-review-t680-pi-placeholders-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no Pi, generator, merger or test run; the `grep_content` tool could not reach the worktree or scratchpad). Recorded by the orchestrator from the reviewer's two reports (first review, delta re-review).
- **Gate**: security. **Date**: 2026-10-22.
- **Target**: T680, branch `agent/devops-engineer/T680` (from develop `84312bb0`): Pi MCP placeholders verified on Pi 0.99.0, 1.0.0, 1.3.0 and 1.4.0 (scratch installs, fake servers, `env -i`, no real credential), the generator's `optional: true` for `env` values and `skipFormats`, `${env:X}` replaced by `${X}` for every server on Pi, `scripts/merge-mcp-json.py --drop-env-form` for `.pi/mcp.json`. Reviewed tips: `4bc35edb` (first review), fix commit `bf35726b` (delta). The last round (`440e45ed`: SEC-T680-05, -07, -08, -09 and the residual of -04, merged with develop `33f6375b`) was verified by the developer's tests and the orchestrator's suite run, not re-read by the reviewer.
- **Based on**: `docs/tasks/task-T680.md`, `docs/artifacts/security-review-t665-token-handling-v1.md` (SEC-T665-09), `security-review-t682-installer-residuals-v1.md`.
- **Orchestrator checks**: the full suite on the final merged tree is recorded in the task outcome. The developer's mutation log (`scratchpad/mutations-t680.txt`): 69 distinct mutations (23 + 24 + 22) and 4 re-runs, all killed in the final state.

## First review: CONDITIONAL_PASS (0 critical, 0 high, 1 medium, 5 low)

Omitting an optional variable on Pi adds no exposure (a stdio server already inherits Pi's environment); the new Pi form fails closed (an unset variable stops that server with a named error instead of sending a literal `${env:X}` as the credential); the generator validates before writing; no injection through the new rendering.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T680-01 | MEDIUM | a literal token typed into the now-omitted Pi token keys was kept by the merge (a T665 invariant, "the merge does not keep a literal credential in a generated entry", no longer held on Pi; the migration text was false for Pi) | fixed: a WARNING for a kept key in a generator-owned env/headers/environment block whose name looks like a credential and whose value is a literal (name only, never the value, the key is not deleted), a Pi test, corrected migration text; CLOSED |
| SEC-T680-02 | LOW | `optional` on a header would silently drop the header on Pi | fixed (`optional` refused on `headers`); CLOSED |
| SEC-T680-03 | LOW | `hindsight` and `cwso` (templated `url`, which Pi 1.x rejects) generated for Pi although they cannot work | fixed (`skipFormats: [pi]`, validated; the Pi sidecar drops the two names so `--update` prunes them, with a prune note; user entries under other names are untouched); `pi mcp list` exit 1 with a rejected url observed on 1.4.0; CLOSED |
| SEC-T680-04 | LOW | verification claims broader than the evidence (a release range, "no network", project-level `.pi/mcp.json` not tested, ambient secrets in the recorded environment) | fixed (four named releases; "no network beyond the package installation (Pi's own start-up calls were not checked)"; the Status cells say project-level `.pi/mcp.json` not tested; the developer confirmed `env -i` with fake values and deleted the recorded files; the Pi no-per-server-environment-scoping limit added to "What this does not protect"); CLOSED |
| SEC-T680-05 | LOW | the drop is lossy and the printed names are not escaped | fixed in the last round (every name through one `format_names()` helper that calls T682's `printable()`; the bootstrap-kept note and the `--force-prune-keys` offenders message routed through it; six sinks tested; restore hint); CLOSED, not re-read |
| SEC-T680-06 | LOW | test and mutation gaps | fixed; CLOSED |

## Delta re-review: PASS (0 critical, 0 high, 0 medium; 4 LOW open at the time, all addressed in the last round)

| Id | Grade | Finding | Disposition (last round, not re-read by the reviewer) |
|---|---|---|---|
| SEC-T680-07 | LOW | the literal-credential classifier treated `${VAR:-glpat-...}`, `pa$word` and similar as placeholders; a literal path in `*_FILE` triggered "revoke the token" | fixed: a value is a placeholder only if it fully matches one `${NAME}`, `$NAME` or `{env:NAME}` reference (optional one-word prefix; `!command` exempt); credential names extended; keys ending in FILE or PATH get a non-alarming "literal path" note. Known limit documented in the code: a real secret shaped exactly like `$NAME` cannot be told from a reference |
| SEC-T680-08 | LOW | quadratic regex on a hostile value | fixed: only the first 4096 characters are classified, a longer value counts as a literal; time-limit tests with multi-megabyte values |
| SEC-T680-09 | LOW | pruning a same-named hand-fixed `hindsight`/`cwso` entry loses it with no backup | fixed: migration text ("copy the entry to another name before updating"), a note "differs from the generated entry; its old content is not kept" (names only; the heuristic is "not a single reference"), tests |
| SEC-T680-05 (rest) | LOW | two print sites bypassed the helper and the helper escaped nothing | fixed as above |

Informational: Pi has no per-server environment scoping (documented); the trust prompt for a project-level `.pi/mcp.json` is unverified and a hostile project file is Pi's concern; a stale exported `GITLAB_PERSONAL_ACCESS_TOKEN` still wins over `_FILE` (documented).

## Open and unverified

Every Pi behaviour claim except what the developer observed on the four scratch installs (the in-session MCP path, other Pi releases, Pi's own start-up network calls, project-level `.pi/mcp.json`, a real run of `pi-mcp-adapter`, whether `pi mcp list` exits 1 for other rejections); the reviewer saw no experiment transcripts; the behaviour of Pi's environment merge order.
