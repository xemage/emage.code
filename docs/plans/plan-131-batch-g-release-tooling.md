# plan-131 — LOW batch G: release tooling and CI

**Created:** 2026-11-02
**Based on:**
- `docs/artifacts/tracked-debt-register-v5.md` § 5, batch G (14 ids).
- `docs/artifacts/security-review-t715-t716-batch-b-v1.md` § 3, which has the findings and the reviewer's fixes.
- The user's answers of 2026-11-02, verbatim:
  - "G go"
  - SEC-T702-08: "Keep it tracked"
  - TL-T708-07: "Accept as is (Recommended)"
  - SEC-T677-01: "Add a JS parser"

**Scopes:** `T730`, `T731`, `T732`.

## Goal

Close the release-tooling LOW items before the next release. SEC-T716-01 comes first.

## Task Decomposition

1. **T730** (devops-engineer): the release script and the drift check.
   - **SEC-T716-01 (do first):** `scripts/check-main-develop-drift.py:50-51, 146-147` resolves `origin/main` and `origin/develop` by short name, so a tag with that name shadows the branch. Resolve the refs with `git show-ref --verify --hash refs/remotes/<ref>`, as `check-release-tag-tree.py:71-86` does, then read files by object id. Add a test with a shadowing tag.
   - **SEC-T716-02:** in `scripts/publish-release.py:76-80, 326-328`, the category test depends on the Unicode database of the Python that runs it. Add the reserved Default_Ignorable ranges explicitly (U+2065, U+FFF0-FFF8, U+E0000-E0FFF and the others in the Unicode list). Add a test that asserts `unicodedata.unidata_version` for the release image.
   - **SEC-T716-03:** in `publish-release.py:417-446`, bare URLs and GitLab references (`@user`, `#123`, `!12`, `~label`, `%milestone`) in a commit subject render as links. Neutralise `://` and these sigils outside code spans, with tests. If neutralising breaks a legitimate changelog form, document the residual risk instead and give the reason.
   - **SEC-T716-04:** in `publish-release.py:532-539`, `ApiCredential` is a NamedTuple, so `tuple()`, `_asdict()`, `%`-formatting and pickling expose the token. Use a non-iterable type (a frozen dataclass with `field(repr=False)`, or a `__slots__` class). Add a test that none of these forms exposes the token.
   - **SEC-T716-05:** `tests/functional/test_publish_release_t716.py` skips its CommonMark rendering test without saying so when markdown-it-py is missing. Add markdown-it-py to `ci/requirements-ci.in`, regenerate `ci/requirements-ci.txt` with hashes, and make the test fail, not skip, when `CI` is set.
   - **SEC-T676-14:** handle it in the same lock regeneration. Set `--exclude-newer` to at least seven days before the generation day, so it works as a cooldown, and state that in the header comment.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. All gates and the suite pass.
2. **T731** (devops-engineer): the release-docs gate, `scripts/verify-release-docs.py`.
   - **SEC-T715-01** (lines 134, 357-366): pointer forms without the keywords still pass unchecked, for example `v9.0.0.md`, `release-notes`, `doc/releases`, `"$REL_DOC"` or a wiki URL. Widen `POINTER_LIKE_RE` to catch these forms, with a broken fixture for each.
   - **SEC-T715-02** (lines 352-353): a prose pointer on a line that names Cursor is checked only for existence. Check it for the Cursor item, or report it as unparsed. T723 reworded `install.sh:1300`; confirm that the current `install.sh` passes.
   - **SEC-T715-03** (lines 386-414): an anchor inside a raw HTML block still counts. Blank CommonMark HTML blocks as well, with a fixture.
   - **SEC-T715-04** (lines 427-430, and 221): the gate prints an `install.sh` line to the CI log without stripping control or bidi characters. Pass printed lines through an `UNSAFE_RE.sub("?", ...)` like the one in `check-release-tag-tree.py:48`, with a test.
   - *Acceptance:* each item is fixed with a test, and every new check fails on a broken fixture. `verify-release-docs.py --tag v9.0.0` still passes. All gates and the suite pass.
3. **T732** (devops-engineer), **SEC-T677-01**: the user's decision is "Add a JS parser". Make `tests/functional/test_function_size.py` measure JavaScript functions with a real parser instead of line heuristics. This closes the residual shapes listed in the guard's docstring: a `}` inside a multi-line template literal, methods with multi-line parameters, and anonymous callbacks.
   - Use a parser dependency such as `acorn`, pinned to an exact version at least two weeks old.
   - Add a lockfile with integrity hashes in a dedicated directory, for example `ci/js/package.json` and `package-lock.json`. Install with `npm ci --ignore-scripts` in the CI job that runs the suite.
   - When the parser is missing and `CI` is set, the test must fail rather than skip. Locally it may skip, but it must say so.
   - Also record the dependency and its update rule where the repo documents CI dependencies.
   - *Acceptance:*
     - the residual shapes are measured, with fixtures;
     - all real `.mjs` and `.js` files stay within 50 lines;
     - the lockfile carries integrity hashes;
     - CI installs the parser with `--ignore-scripts`;
     - all gates and the suite pass;
     - the CI lint is valid.

T730, T731 and T732 run in parallel. They share no source file, but T730 and T732 may both edit `.gitlab-ci.yml`: T730 owns the Python requirements line, and T732 owns a new npm install step. A Security Engineer reviews all three.

## Not changed in this plan

- **SEC-T702-08** stays tracked (the user: "Keep it tracked").
- **TL-T708-07** is accepted as is (the user: "Accept as is (Recommended)"). The basis is the T704 decision D-T700-1 "Exclude docs/decisions/ (Recommended)".
- **TD-T723-01** is handled in the next release document, by the release-manager, which cites the current `install.sh` lines.

## Constraints

- Subagents never merge, tag or release. The orchestrator merges on `mergeable` with a green pipeline and a pinned sha.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file.
- No change under `implementation/` is expected. If there is one, declare the root drift; a refresh needs the user's approval.

## Outcome (2026-11-04)

- **Tasks.** T730 to T732 are done.
- **User decisions** (AskUserQuestion, verbatim):
  - 2026-11-02, the three gaps the first review named: "Fix now in this batch (Recommended)".
  - 2026-11-04, the reviewer's refused reads: "Allow its reads (Recommended)".
  - 2026-11-04, the re-check's findings: "Fix the three now (Recommended)", meaning SEC-T731-01, SEC-T731-06 and SEC-T730-05.
- **Batch-G ids.**
  - Closed: SEC-T716-01 to -05; SEC-T715-01 to -04; SEC-T677-01 (JavaScript; Bash is still measured line by line, and its two gaps stay in the guard's docstring); SEC-T676-14.
  - Accepted: TL-T708-07.
  - Still tracked: SEC-T702-08 (the user: "Keep it tracked").
  - For the next release document: TD-T723-01.
- **Security review.** `docs/artifacts/security-review-t730-t732-batch-g-v1.md` gives PASS, with no MEDIUM or higher. Of 17 LOW findings, 6 are resolved and 11 are tracked: SEC-T730-03, -04, -06; SEC-T731-03, -04, -05, -07, -08, -09; SEC-T732-01, -02.
- **Visible changes.**
  - `CHANGELOG.md` entries now show `\#42`, `\@user` and URLs in backticks in their source, and `(#42)` no longer links to the issue.
  - Release documents need a blank line or an ATX heading before the Cursor item, and no trailing comment on `## Migration Guide`. Those shapes are deliberate false FAILs.
  - Checked documents may not contain `\v \f \x1c-\x1e \x85 U+2028 U+2029`.
- **Not verified live:** how GitLab renders the escaped references and code spans, the npm step in a tag pipeline, and the lock on the musl image beyond the MR pipeline.
- **Token use against budget:**

  | Task | Used | Budget |
  |---|---|---|
  | T730 | about 176k | 100k, plus 65k for two follow-ups |
  | T731 | about 161k | 80k, plus 85k for three follow-ups |
  | T732 | about 162k | 100k |
  | Security review | about 282k | 70k, plus 45k for two re-checks |
