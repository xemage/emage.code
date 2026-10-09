# Artifact: poc-security-engineer-tool-scoping-v5.md

> Immutable once produced; revisions bump `<N>`. **Amends `poc-security-engineer-tool-scoping-v4.md`** (which amends v3, which
> amends v2), all of which stay unchanged as the historical record. Where they differ, v5 governs; everything v4, v3 and v2 say and
> v5 does not mention is unchanged (server, two tools, argv, environment, root check, caps, redaction including the T611-1 rule
> tests on the raw and the cleaned name, the label conditions of v3 section 4, the SEV-1..SEV-6 bounds, `ref_containment`).
> F-8, E1-b, E1-c and both tool lists are byte-identical. No rule pattern changes, so `RULES_VERSION` stays `2026-10-09.5`.

## Metadata

- **Producer agent**: backend-developer
- **Task**: T612 (plan-116): altered-path flags and the regex-library self-test
- **Created**: 2026-10-09
- **Based on**:
  - `docs/artifacts/poc-security-engineer-tool-scoping-v4.md` (the contract this amends; section 12 lists T611-2 and T611-3);
  - `docs/artifacts/security-review-t611-scanner-residuals-v1.md` (T611-2, T611-3);
  - `docs/artifacts/placeholder-flag-ruling-v3.md` (flag fields and when a flag is void) and `security-review-t608-placeholder-flag-text-v1.md`;
  - `implementation/runtime/security/poc_scan.py`, `poc_audit_server.py`, `git_executor.py`.
- **Decision references**: ADR-008 P4 and D5 (via v2). No new ADR. Immutable Security Constraint 1 governs. No rule is weakened, no
  label condition changes, every new failure path ends in `complete: false` and no hit is hidden.

## 1. Change log against v4

| # | Finding | v4 | v5 |
|---|---|---|---|
| 1 | T611-2 | `safe_name` changes `path_or_redacted`, the key that flags match on; agent text did not cover it (v4 section 12) | A hit whose shown path was altered carries `path_altered: true`; the agent text makes it unflaggable and unresolved (section 2) |
| 2 | T611-3 | The bounded repeats may not compile on a regex library with a low `RE_DUP_MAX`; every scan then ends a bare `git_failed` (v4 section 12) | A self-test compiles the largest rule first and reports `regex_unsupported` (section 3); the library requirement is stated (section 4) |

## 2. T611-2: `path_altered`

**Cause.** `safe_name` removes control, format (bidi, zero width), line and paragraph separator characters and cuts a name at 200
characters, and the scanner decodes git's raw path bytes as UTF-8 with replacement, so a byte that is not valid UTF-8 is shown as
U+FFFD (security review SEC-1: `cfg\xff.yaml` and `cfg\xfe.yaml` both showed `cfg\ufffd.yaml`). The shown `path_or_redacted` is then not
the real git path. A flag is keyed on the path "exactly as the scan shows it",
and the list of paths modified since `flag_commit` is built from real paths, so (a) a later change to such a file never voids its
flag, and (b) two different files can show the same text, so their hits merge into one `hit_count`.

**Marker.** Each `scan_secrets` hit may carry one more key, `path_altered`:

- It is present, and exactly `true`, when the hit has a shown path (`path_or_redacted`) that is not a redacted one and that differs
  from the real path: `safe_name` removed a character or cut the name, **or the raw bytes were not valid UTF-8** (a lossy decode).
  It is absent otherwise: an unaltered path, a redacted path, a hit without a path (`via: "log"` history hits).
- **Lossy decode.** `poc_scan._decode_name(raw)` returns `(text, lossy)`; `lossy` is true exactly when strict UTF-8 decoding of the
  raw path bytes fails. The two path-bearing callers (`grep` and `_name_scan`) pass it to `add_hit` as the internal `name_lossy`
  argument, which is consumed there and never appears in a result. The test is on the raw bytes, not on U+FFFD in the text.
  **A valid name that contains a literal U+FFFD character** decodes cleanly, is shown exactly as it is and is **not** marked: its
  shown path is its real path. If it shares its text with a lossy name, the lossy name is marked and both are counted in the same
  `hit_count`, so a flag on the clean name is void while the lossy file exists (fail closed).
- A name shown as `<redacted-by-rule:ID>` carries `path_index` and no marker. It is already unflaggable (agent text) and is not "the
  real path with characters removed".
- `poc_scan.HIT_KEYS` gains `path_altered` (the full list: `rule_id`, `scope`, `path_or_redacted`, `path_index`, `line`, `commit`,
  `ref`, `via`, `value_shape`, `template_shape`, `path_altered`).
- `add_hit` derives the marker from the name (`shown != name`) and the lossy-decode flag, and never takes it from a caller: a `path_altered` field passed
  in is discarded first. After the allow-list and label checks it validates the key: it must be exactly `True`, the hit must have a
  `path_or_redacted` and no `path_index`; anything else is dropped. A hit is never removed or uncounted by this check.
- The `ref` field of a tree hit (a ref or tag name, cleaned by `safe_name`, decoded with replacement) is not a path, is not part of a
  flag, and does not get a marker.
- The marker changes no rule, no redaction, no label and no count: `counts`, `complete` and `truncated` are the same as in v4.

**Agent text** (`implementation/knowledge/agents/poc-security-engineer.md`, a new sub-bullet "Altered paths" of "Placeholder flags",
plus the "Reporting" bullet; `poc-orchestrator.md`, "Placeholder flags"):

- A hit with `path_altered: true` cannot be flagged and stays unresolved, whatever a register says. The reviewer does not propose a
  flag for it; it reports the hit as unresolved with the note that the path was altered, and the file must be renamed or removed.
- It is still counted, like every hit, in the `hit_count` of the path text it shows. A flag on an unaltered path that shows the same
  text is therefore void while the altered hit exists (fail closed; the existing "number of hits is not exactly `hit_count`" rule).
- **Label.** A hit with `path_altered: true` and `value_shape: "template-ref"` stays `template-ref`: it is listed and counted as
  template-ref and is not unresolved, because the label is not a flag; it still cannot be flagged. (A `bare-dollar-name` or unlabelled
  altered-path hit is unresolved.) The reviewer never infers the marker itself.
- **Progression task.** The `blocked` task for an unresolved altered-path hit awaits the rename or removal of the file, owner the
  remediating agent; it is not titled "awaiting user: placeholder flag", because no user flag can resolve it.
- The orchestrator does not put such a hit to the user as a proposed flag (its "every other hit ... gets a `user-attested` proposal"
  sentence excepts it), and a register entry never records an altered path.

**Residual.** A path that contains one of the removed characters in its real name is unflaggable until renamed. That is the
intended trade: the cost is a rename, the alternative is a flag that cannot be checked.

## 3. T611-3: regex self-test and `regex_unsupported`

**Cause.** The bounded repeats `{7,1024}`, `{1024}` (unquoted rule) and `{10,512}` (JWT) exceed the maximum repeat count
(`RE_DUP_MAX`) of some regex libraries (255 is the POSIX minimum; the T611 review names musl and some BSD libraries as using it).
`git grep -E` then fails to compile the pattern and every scan ended `git_failed` with no reason.

**Self-test (`poc_scan._regex_selftest`).**

- Before any scope except `tracked_names` (the only scope that runs neither `git grep -E` nor `git log -G`), one call compiles the
  rule with the largest repeat count (ties: the longest pattern; today `unquoted-credential-assignment`, 7560 characters):
  `git grep --no-color -q -E -e <pattern> <empty tree> --`. The empty tree is a built-in git object, so nothing is read from the
  repository and only the pattern is compiled. Measured on git 2.43.0 with glibc: about 0.25 s, the compile cost the unquoted rule
  already pays in its own scan calls (unverified on other hosts).
- It goes through `git_executor.run_git` like every other call: the same hardening prefix, environment, byte cap and the scan's
  aggregate `Deadline`. No new subprocess surface, no new module that spawns a process.
- A pass returns nothing and the scan continues unchanged. A clean-path scan costs exactly this one extra call.
- On `git_failed` a **control call** (the same argv with the pattern `a`) runs. If the control passes, the failure was the pattern:
  the scan returns `regex_unsupported` (meaning exactly: the compile call failed while a trivial pattern compiled, usually a low
  `RE_DUP_MAX`; the scan does not prove which regex limit was exceeded). If the control also fails, or any other error occurs (`timeout`, `git_missing`), that error
  code is returned unchanged. The control runs only on the failure path.
- The result is the existing failure shape: `complete: false`, `truncated` only for `timeout`, `hits: []`, `counts: {}`,
  `errors: ["regex_unsupported"]`. It is not a clean result and never claims the absence of secrets. Nothing is dropped, because no
  scanning has started.
- The tool description names the error code. The agent text (the "Reporting" sub-bullet of `poc-security-engineer.md`) adds one
  sentence: such a scan is an incomplete scan, reported as a `technical` blocker, never as clean, with the remedy "run the scan on a
  host whose git uses a regex library with `RE_DUP_MAX` of at least 1024". The frozen F-8 text is untouched.

**Not covered.** The anchored label patterns (`ANCHORED_RULES`) are shorter and carry no larger repeat count than the rule that is
compiled (pinned by a test). A library that compiles the self-test pattern but rejects another construct of another rule is not
detected by the self-test and still fails closed as `git_failed` on that rule's call.

## 4. Regex-library requirement

The scanner needs a regex library, as used by `git grep -E` and `git log -G` on the host, whose `RE_DUP_MAX` is **at least 1024**
(glibc: 32767). Where it is lower (a build against musl or some BSD libraries), every scan except `tracked_names` ends
`regex_unsupported`; the remedy is a git build with a library that supports the counts, not a change to the rules (a smaller bound
would widen the SEV-1 blind spots of v4 section 2). A host that cannot meet it cannot use the content scopes of this server.

## 5. Tests (`tests/functional/test_poc_audit_server.py`, class `T612Tests`; `test_placeholder_flag_text.py`)

Altered path via a stripped control character, via a zero-width character, via a 250-character name and via invalid UTF-8 bytes
(two files `cfg\xff.yaml` and `cfg\xfe.yaml` both marked; a literal U+FFFD that decodes cleanly is not; `_decode_name`; a non-UTF-8
tag shows no marker on `ref`) (marker present, shown text
unchanged from v4); unaltered paths carry no marker; redacted names carry `path_index` and no marker; two files that show the same text
both carry the marker and are both counted; `add_hit` discards a caller-supplied marker and drops an invalid one; the key is in
`HIT_KEYS`; the marker appears in the `tracked_names` and `worktree` scopes; the self-test pattern is the rule with the largest repeat
count and no rule or anchored rule has a larger one; the self-test passes with exactly one extra `git grep` call before the rule
calls; the failure path is simulated by making the executor fail the compile call (the real subprocess is not used for the
failure), giving `regex_unsupported`, `complete: false`, no hits and no clean claim; a failing control gives `git_failed`; a timeout
in the self-test gives `timeout`; the self-test call receives the scan's own `Deadline` object, and an expired deadline gives `timeout` with
no subprocess; a zero-width character in a ref name shows no marker on `ref`; `tracked_names` runs no self-test; the self-test argv carries the hardening prefix; contract v5; the
agent phrases in both agent files and their mirrors; the tool description; no `assert` in the scanner (unchanged test).

## 6. Open residuals (unchanged by T612) and unverified

- **R-1 (aperiodic input)** stays documented only (v4 section 12): fails closed on the deadline.
- The remaining T611 residuals are closed by v4, T611-2 and T611-3 by this document.

Unverified:

1. The `RE_DUP_MAX` values of musl, BSD and macOS libraries are taken from the T611 review and the POSIX minimum; no such host was
   available for the self-test failure path, which is exercised only through a simulated executor failure and, once, by hand with
   a `git grep` repeat count above git's own limit (`a{1,99999}` exits non-zero on git 2.43.0).
2. The 0.25 s self-test cost is for git 2.43.0 on the development host.
3. The empty-tree object is assumed available in every repository the scan accepts (a SHA-256 repository already fails earlier
   because the hardening prefix names the SHA-1 empty tree).
