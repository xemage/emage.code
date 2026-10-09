"""`poc-security-audit` MCP server (T603) -- tool logic for `scan_secrets` and
`ref_containment`.

Implements `docs/artifacts/poc-security-engineer-tool-scoping-v2.md` §3.2 and §3.3. This
module spawns no process itself: every command goes through
`git_executor.run_git()`, as a fixed argv list built from constants plus validated data.

What the tools return, and what they never return:

* No matched text, no stderr, no argv. `git grep -z -n` output is parsed as
  `path NUL line NUL text LF`. The text field is never copied into a result. One narrow
  exception to "dropped unread" (contract v3, `poc-security-engineer-tool-scoping-v3.md`): only
  for the two credential-assignment rules in `worktree`/`index` scope (`_parse_records` with
  `keep_text=True`) the text is compared in memory against fixed template shapes (`_label_for`),
  reduced to a shape name and discarded. Every other rule and scope still drops it unread.
* The caller supplies no pattern. The rule table below is the only source of patterns; it
  is also applied to paths, ref names and tag names before they are returned.
* Errors are codes: not_a_toplevel, bad_scope, bad_rev, timeout, git_missing, git_failed.

Documented limits (v2 §3.2 / R-3, R-4, R-5): a clean result means "no match for this rule
set at the scanned refs", not "no secret"; dangling objects and reflog-only commits are
invisible; `pushed` is `true` or `"unknown"`, never `false`.

Further limits recorded by the T603 code review (security-review-poc-security-audit-code-v1,
tracked in T604):

* L-3 (superseded by the user decision of 2026-10-09, T606 Q2 Option A, placeholder-flag-ruling-v3
  E-S2): the `$`, `<`, `{` and (quoted rule only) space leading-character skips are gone, so a
  value that starts with one of those is an ordinary hit. A hit carries `value_shape`
  `template-ref` (with `template_shape`) only when every match of its rule on the line is, as a
  whole, one of three exact shapes, and `bare-dollar-name` for a bare `$NAME`; see `_label_for`.
  Still not reported: quoted or unquoted values shorter than eight characters (a URL password
  shorter than three), values with a quote (and, unquoted, `(`), unquoted values that start with a
  space, tab, CR, quote, `(` or `=`, unquoted names that end in a configuration word (ttl, timeout,
  url, ... see NON_SECRET_NAME_ENDINGS), a URL password that starts with `/`, `@` or a space or
  contains `/`, `@` or a space, a URL whose scheme is 32 or more characters long or in upper case,
  and secrets in unlisted formats.
* L-4: `scan_secrets(scope="history")` uses `git log -G`, which does not diff merge commits.
  A secret that exists only as a merge-resolution change is found only if it is also visible
  in a scanned tip tree.
* L-5: a `rev_range` that names more than `max_refs` (200) commits is reported `truncated`
  although the `git log` pass covers the whole range. This is deliberately over-conservative.
* L-6: a `.git` *file* in `root_dir` may point to a gitdir outside `allowed_root`; only the
  working directory is checked against `allowed_root` (recorded as R-6 in v2).
* Untracked secret FILES (scope `worktree`) are reported by NAME only, with the rule id
  `untracked-secret-file-name`; their content is covered by the content rules, so a file whose
  name is not on the allowlist is still scanned by content. Ignored files are included.
* `unquoted-credential-assignment` is a tuned heuristic: it needs a credential keyword in the
  name, a value of 8 or more characters without whitespace, `(` or quotes and not starting with
  `=`, and a name that does not end in a non-secret word (ttl, timeout, url, ...). A
  value shorter than 8 characters is never reported, and a code identifier such as
  `password = args.password` is (a known false positive).
"""
from __future__ import annotations

import fnmatch
import os
import re
import stat
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from implementation.runtime.security.git_executor import (
    ERR_GIT_FAILED,
    LOG_FLAGS,
    Deadline,
    GitResult,
    git_argv,
    run_git,
)

RULES_VERSION = "2026-10-09.4"


def _ci(word: str) -> str:
    """Case-insensitive ERE for a word (works in git ERE and in Python `re`)."""
    return "".join(f"[{c.upper()}{c.lower()}]" if c.isalpha() else c for c in word)


_NAME_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789_-"


def _name_class(chars: set[str]) -> str:
    """Bracket expression for lower-case name characters, letters in both cases."""
    parts = [c.upper() + c if c.isalpha() else c for c in sorted(chars) if c != "-"]
    return "[" + "".join(parts) + ("-" if "-" in chars else "") + "]"


def _not_ending(words: tuple[str, ...]) -> str:
    """ERE (no lookaround) for name-character strings, empty included, that end in NONE of
    `words` (case-insensitive). Built by peeling the last character off every word."""
    last = {w[-1] for w in words}
    alts = ["[A-Za-z0-9_-]*" + _name_class(set(_NAME_CHARS) - last)]
    for c in sorted(last):
        rest = tuple(w[:-1] for w in words if w[-1] == c)
        if all(rest):  # a one-letter word would forbid every string ending in c
            alts.append(_not_ending(rest) + _name_class({c}))
    return "(" + "|".join(alts) + ")?"


_CREDENTIAL_WORDS = "(" + "|".join([
    _ci("password"), _ci("passwd"), _ci("pwd"), _ci("secret"),
    _ci("api") + "[-_]?" + _ci("key"), _ci("access") + "[-_]?" + _ci("key"),
    _ci("private") + "[-_]?" + _ci("key"), _ci("token")]) + ")"
# Name endings that are configuration about a secret, not a secret (user decision 2026-10-09).
NON_SECRET_NAME_ENDINGS = ("ttl", "timeout", "url", "uri", "endpoint", "path", "file", "dir",
                           "name", "expiry", "expires", "expiration", "length", "size", "type",
                           "header", "env", "var")
_UNQUOTED_VALUE = (
    "[^ \t\r\"'(=][^ \t\r\"'(]{7,}([ \t\r]|$)"  # 8+ chars, no space/quote/( ; ends at space/EOL
)

# (rule_id, pattern). POSIX-ERE and Python-re compatible subset only.
RULES: tuple[tuple[str, str], ...] = (
    ("private-key-header", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("aws-access-key-id", r"(AKIA|ASIA)[0-9A-Z]{16}"),
    ("github-token", r"gh[pousr]_[A-Za-z0-9]{36,}"),
    ("gitlab-token", r"glpat-[A-Za-z0-9_-]{20,}"),
    ("slack-token", r"xox[abprs]-[A-Za-z0-9-]{10,}"),
    ("stripe-live-key", r"sk_live_[A-Za-z0-9]{16,}"),
    ("google-api-key", r"AIza[0-9A-Za-z_-]{35}"),
    ("bearer-token", r"[Bb]earer [A-Za-z0-9._~+/=-]{20,}"),
    ("pgp-private-key-block", r"-----BEGIN PGP PRIVATE KEY BLOCK-----"),
    ("github-fine-grained-pat", r"github_pat_[A-Za-z0-9_]{22,}"),
    ("npm-token", r"npm_[A-Za-z0-9]{36,}"),
    ("sendgrid-api-key", r"SG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}"),
    ("jwt", r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]*"),
    ("sk-api-key", r"(^|[^A-Za-z0-9_])sk-(ant-|proj-)?[A-Za-z0-9_-]{20,}"),
    # URL with embedded credentials; a password starting with / @ or a space is a delimiter case.
    # The scheme is bounded ({0,31}): an unbounded run made git grep quadratic (minutes) on one
    # very long line of scheme characters, which L-1's `-o` fix now lets reach the scanner.
    ("url-embedded-credentials", r"[a-z][a-z0-9+.-]{0,31}://[^/:@ ]+:[^/@ ][^/@ ]{2,}@"),
    (
        "credential-assignment",
        _CREDENTIAL_WORDS
        # [A-Za-z0-9_-]* then an optional closing quote then : or = (JSON/YAML/.env/code)
        + "[A-Za-z0-9_-]*[\"']?[ \t]*[:=][ \t]*[\"'][^\"'][^\"']{7,}[\"']",
    ),
    (
        "unquoted-credential-assignment",
        _CREDENTIAL_WORDS + _not_ending(NON_SECRET_NAME_ENDINGS)
        + "[\"']?[ \t]*[:=][ \t]*" + _UNQUOTED_VALUE,
    ),
)
_COMPILED = tuple((rid, re.compile(pat)) for rid, pat in RULES)

# --- value-shape labels (T609, placeholder-flag-ruling-v3 E-S2, security review V3-2) -----------
# Only these two rules can carry a label; URL hits never do (V3-2). Only these scopes can.
LABEL_RULES = ("credential-assignment", "unquoted-credential-assignment")
LABEL_SCOPES = ("worktree", "index")
TEMPLATE_REF = "template-ref"
BARE_DOLLAR = "bare-dollar-name"
# Exact shapes, matched with fullmatch against the whole value (no prefix or substring match):
# `${NAME}` (NAME upper case), `<word-word>` (lower-case words, at least one separator, no digits),
# `{{ name }}` (one space each side, no digits). `$NAME` bare is not a template reference.
TEMPLATE_SHAPES: tuple[tuple[str, "re.Pattern[str]"], ...] = (
    ("braced", re.compile(r"\$\{[A-Z][A-Z0-9_]{2,}\}")),
    ("angle", re.compile(r"<[a-z]+([ _-][a-z]+)+>")),
    ("jinja", re.compile(r"\{\{ [a-z][a-z_.]{1,30} \}\}")),
)
_BARE_DOLLAR_RE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]{2,}")
# What `git grep -o` returns for these rules: name, optional quote, separator, value. The name
# characters contain neither `:` nor `=`, so the first one is the separator.
_QUOTED_MATCH_RE = re.compile(r"[^:=]*[:=][ \t]*[\"']([^\"']*)[\"']")
_UNQUOTED_MATCH_RE = re.compile(r"[^:=]*[:=][ \t]*([^ \t\r]+)[ \t\r]*")
# T609-1: the `-o` text ends at the closing quote or the first whitespace, so it cannot show what
# follows the value on the line. A label therefore also needs a second, ANCHORED `git grep` of the
# same rule whose tail is `[ \t\r]*$` (only spaces, tabs or CR may follow the value; a trailing `,`
# or `;` or any other text leaves the hit unlabelled).
_LINE_END = "[ \t\r]*$"
_UNQUOTED_TAIL = "([ \t\r]|$)"
# Every key a `scan_secrets` hit may carry (the contract v3 output list). Pinned by a test.
HIT_KEYS = frozenset({"rule_id", "scope", "path_or_redacted", "path_index", "line", "commit", "ref",
                      "via", "value_shape", "template_shape"})


def _anchored(rule_id: str, pattern: str) -> str:
    """The rule pattern with its tail replaced by `[ \t\r]*$` (value must end the line)."""
    if rule_id == "unquoted-credential-assignment":
        assert pattern.endswith(_UNQUOTED_TAIL)
        return pattern[:-len(_UNQUOTED_TAIL)] + _LINE_END
    return pattern + _LINE_END


ANCHORED_RULES = {rid: _anchored(rid, pat) for rid, pat in RULES if rid in LABEL_RULES}


def _shape_of(rule_id: str, text: bytes) -> str | None:
    """Reduce one matched text to a shape name (`braced`, `angle`, `jinja`, `bare-dollar-name`)
    or None. The text is compared here, in memory, and not kept or returned."""
    rx = _QUOTED_MATCH_RE if rule_id == "credential-assignment" else _UNQUOTED_MATCH_RE
    m = rx.fullmatch(_decode(text))
    if m is None:
        return None
    value = m.group(1)
    for shape, shape_rx in TEMPLATE_SHAPES:
        if shape_rx.fullmatch(value):
            return shape
    return BARE_DOLLAR if _BARE_DOLLAR_RE.fullmatch(value) else None


def _label_for(shapes: list[str | None]) -> dict:
    """Label fields for one (rule, path, line) from the shape of EVERY match of the rule on that
    line. Any non-shape match, or two different shapes, gives no label (the whole line is judged)."""
    kinds = set(shapes)
    if not shapes or None in kinds or len(kinds) != 1:
        return {}
    (kind,) = kinds
    if kind == BARE_DOLLAR:
        return {"value_shape": BARE_DOLLAR}
    return {"value_shape": TEMPLATE_REF, "template_shape": kind}

# security-guidelines.md "Secret and credential files" allowlist (names only).
# Matched case-insensitively against the lower-cased basename (patterns are lower case).
TRACKED_NAME_PATTERNS = (".env", ".env.*", "credentials.json", "*.pem", "*.key",
                         "id_rsa", "secrets.yaml", "id_ed25519", "*.p12", "*.pfx",
                         ".npmrc", ".pgpass")
TRACKED_NAME_RULE = "tracked-secret-file-name"
UNTRACKED_NAME_RULE = "untracked-secret-file-name"

SCOPES = ("worktree", "index", "stashes", "history", "tracked_names")
_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
_SHA_RANGE_RE = re.compile(r"^[0-9a-f]{7,40}\.\.[0-9a-f]{7,40}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_OID_RE = re.compile(r"^[0-9a-f]{40}$")
_TREE_PREFIX_RE = re.compile(rb"^([0-9a-f]{40}):")
_BATCH = 50

ERR_NOT_TOPLEVEL = "not_a_toplevel"
ERR_BAD_SCOPE = "bad_scope"
ERR_BAD_REV = "bad_rev"
ERR_INTERNAL = "internal_error"


@dataclass(frozen=True)
class PocAuditConfig:
    allowed_root: Path
    deadline_seconds: float = 60.0
    max_refs: int = 200
    max_stashes: int = 50
    max_hits: int = 500
    max_bytes: int = 4_000_000


def redact_name(name: str) -> tuple[str, str | None]:
    """-> (name, None) or ("<redacted-by-rule:ID>", rule_id) if a rule matches the name."""
    for rule_id, rx in _COMPILED:
        if rx.search(name):
            return f"<redacted-by-rule:{rule_id}>", rule_id
    return name, None


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")


def parse_grep_z(data: bytes) -> tuple[list[tuple[bytes, int]], bool]:
    """Parse `git grep -z -n` output -> ([(path_bytes, line_no)], leftover).

    `leftover` is True when bytes remain that are not a well-formed record. For output
    that was NOT truncated that means the format was not understood (for example ANSI
    colour escapes), and the caller must fail closed instead of reporting zero hits.
    The matched text is skipped, never copied (`_parse_records` copies it only with
    `keep_text=True`, for the label rules in `worktree`/`index` scope).
    """
    records, leftover = _parse_records(data)
    return [(path, line) for path, line, _ in records], leftover


def _parse_records(data: bytes, keep_text: bool = False) -> tuple[list[tuple[bytes, int, bytes]], bool]:
    """As `parse_grep_z`, but each record carries a third item: the matched-text bytes when
    `keep_text` is true (only the label rules in `worktree`/`index` scope), otherwise `b""` (the
    text is dropped unread). Only `_shape_of` reads that field; it never reaches a result."""
    records: list[tuple[bytes, int, bytes]] = []
    pos, n = 0, len(data)
    while pos < n:
        p1 = data.find(b"\0", pos)
        p2 = data.find(b"\0", p1 + 1) if p1 >= 0 else -1
        eol = data.find(b"\n", p2 + 1) if p2 >= 0 else -1
        if eol < 0 or not data[p1 + 1:p2].isdigit():
            return records, True
        records.append((data[pos:p1], int(data[p1 + 1:p2]), data[p2 + 1:eol] if keep_text else b""))
        pos = eol + 1
    return records, False


def resolve_root(root_dir: object, cfg: PocAuditConfig, deadline: Deadline) -> tuple[str | None, str | None]:
    """F-2: inside allowed_root AND equal to `git rev-parse --show-toplevel`."""
    if not isinstance(root_dir, str) or not root_dir or "\0" in root_dir:
        return None, ERR_NOT_TOPLEVEL
    try:
        path = Path(root_dir).resolve()
        path.relative_to(cfg.allowed_root.resolve())
    except (ValueError, OSError, RuntimeError):
        return None, ERR_NOT_TOPLEVEL
    if not path.is_dir():
        return None, ERR_NOT_TOPLEVEL
    res = run_git(git_argv(str(path), "rev-parse", "--show-toplevel"), deadline, 4096)
    if res.error == ERR_GIT_FAILED:
        # L-2: only a directory with no `.git` entry is a genuine "not a repository". With one,
        # a failing rev-parse is an old git, a SHA-256 repo, an ownership refusal ...: report it.
        return None, (ERR_GIT_FAILED if os.path.lexists(path / ".git") else ERR_NOT_TOPLEVEL)
    if res.error:
        return None, res.error
    out = _decode(res.stdout)
    out = out[:-1] if out.endswith("\n") else out
    try:
        same = Path(out).resolve() == path
    except (OSError, RuntimeError):
        same = False
    return (str(path), None) if same else (None, ERR_NOT_TOPLEVEL)


class _Scan:
    """State of one `scan_secrets` call: hits, errors, truncation, aggregate deadline."""

    def __init__(self, root: str, cfg: PocAuditConfig, deadline: Deadline, scope: str) -> None:
        self.root, self.cfg, self.deadline, self.scope = root, cfg, deadline, scope
        self.hits: list[dict] = []
        self.errors: list[str] = []
        self.truncated = False
        self._redacted: dict[str, int] = {}

    # -- plumbing ---------------------------------------------------------------
    def run(self, *args: str, ok: tuple[int, ...] = (0,)) -> GitResult | None:
        res = run_git(git_argv(self.root, *args), self.deadline, self.cfg.max_bytes, ok)
        if res.error:
            self._error(res.error, res.truncated)
            return None
        self.truncated = self.truncated or res.truncated
        return res

    def _error(self, code: str, truncated: bool) -> None:
        if code not in self.errors:
            self.errors.append(code)
        self.truncated = self.truncated or truncated

    def display(self, name: str) -> tuple[str, int | None]:
        shown, rule = redact_name(name)
        if rule is None:
            return shown, None
        return shown, self._redacted.setdefault(name, len(self._redacted) + 1)

    def add_hit(self, rule_id: str, **fields) -> bool:
        if len(self.hits) >= self.cfg.max_hits:
            self.truncated = True
            return False
        hit = {"rule_id": rule_id, "scope": self.scope}
        name = fields.pop("name", None)
        if name is not None:
            hit["path_or_redacted"], idx = self.display(name)
            if idx is not None:
                hit["path_index"] = idx
        hit.update({k: v for k, v in fields.items() if v is not None})
        for key in set(hit) - HIT_KEYS:  # contract v3 allow-list, enforced: an unknown key is dropped
            del hit[key]
        self.hits.append(hit)
        return True

    def result(self) -> dict:
        counts = dict(Counter(h["rule_id"] for h in self.hits))
        return {
            "complete": not self.errors and not self.truncated,
            "truncated": self.truncated,
            "rules_version": RULES_VERSION,
            "hits": self.hits,
            "counts": counts,
            "errors": self.errors,
        }

    # -- git grep ---------------------------------------------------------------
    def grep(self, flags: tuple[str, ...], trees: tuple[str, ...] = (),
             refs: dict[str, str | None] | None = None) -> None:
        """One `git grep` per rule (so each hit carries its rule_id); text never returned."""
        for rule_id, pattern in RULES:
            keep = rule_id in LABEL_RULES and self.scope in LABEL_SCOPES and not trees
            # -a (treat as text) so a `-diff`/binary attribute cannot hide a match.
            # -o (L-1) prints only the matched part, so a huge single line cannot fill the byte cap.
            args = ("grep", "--no-color", *flags, "-a", "-o", "-n", "-z", "-E", "-e", pattern,
                    *trees, "--")
            res = self.run(*args, ok=(0, 1))
            if res is None:
                return
            records, leftover = _parse_records(res.stdout, keep_text=keep)
            if leftover and not res.truncated:
                self._error(ERR_GIT_FAILED, False)  # unparseable output: fail closed
                return
            # A cut-off output may hide further matches on a line, so it gets no labels.
            labelled = keep and not res.truncated
            # -o prints one record per match, not per line: one hit per (path, line), and the
            # shape of EVERY match on the line is collected before the label is decided.
            shapes: dict[tuple[bytes, int], list[str | None]] = {}
            for raw, line, text in records:
                found = shapes.setdefault((raw, line), [])
                if labelled:
                    found.append(_shape_of(rule_id, text))
            ends_line = self._value_ends_line(flags, rule_id, shapes) if labelled else set()
            for (raw, line), found in shapes.items():
                m = _TREE_PREFIX_RE.match(raw) if trees else None
                commit = m.group(1).decode() if m else None
                name = _decode(raw[m.end():] if m else raw)
                ref = (refs or {}).get(commit) if commit else None
                label = {}
                if (raw, line) in ends_line and redact_name(name)[1] is None:
                    label = _label_for(found)
                if not self.add_hit(rule_id, name=name, line=line, commit=commit, ref=ref, **label):
                    return

    def _value_ends_line(self, flags: tuple[str, ...], rule_id: str,
                         shapes: dict[tuple[bytes, int], list[str | None]]) -> set[tuple[bytes, int]]:
        """(path, line) pairs where a match of the rule ENDS the line (T609-1). One extra anchored
        `git grep` through the same executor and deadline, only when some line is a label
        candidate. Fail closed and quiet: an error, a timeout, truncation or unparseable output
        returns the empty set (no label), records no scan error and never removes a hit."""
        if not any(_label_for(found) for found in shapes.values()):
            return set()
        args = ("grep", "--no-color", *flags, "-a", "-o", "-n", "-z", "-E", "-e", ANCHORED_RULES[rule_id], "--")
        res = run_git(git_argv(self.root, *args), self.deadline, self.cfg.max_bytes, (0, 1))
        if res.error or res.truncated:
            return set()
        records, leftover = _parse_records(res.stdout)
        return set() if leftover else {(raw, line) for raw, line, _ in records}

    def grep_trees(self, shas: list[str], refs: dict[str, str | None] | None = None) -> None:
        for i in range(0, len(shas), _BATCH):
            self.grep((), tuple(shas[i:i + _BATCH]), refs)

    # -- scopes -----------------------------------------------------------------
    def scan_stashes(self) -> None:
        probe = self.run("for-each-ref", "--count=1", "--format=%(objectname)", "refs/stash")
        if probe is None or not probe.stdout.strip():
            return
        cap = self.cfg.max_stashes
        res = self.run("rev-list", "-g", f"--max-count={cap + 1}", "refs/stash")
        if res is None:
            return
        shas = self._oids(res.stdout)
        if len(shas) > cap:
            self.truncated = True
        self.grep_trees(shas[:cap])

    def tips(self, rev_range: str | None) -> tuple[list[str], dict[str, str | None]]:
        cap = self.cfg.max_refs
        refs: dict[str, str | None] = {}
        if rev_range:
            res = self.run("rev-list", f"--max-count={cap + 1}", "--end-of-options", rev_range, "--")
            shas = self._oids(res.stdout) if res else []
        else:
            res = self.run("for-each-ref", f"--count={cap + 1}", "--format=%(objectname) %(refname)",
                           "refs/heads", "refs/remotes", "refs/tags")
            shas = []
            lines = _decode(res.stdout).splitlines() if res else []
            self.truncated = self.truncated or len(lines) > cap  # cap counts refs
            for line in lines[:cap]:
                oid, _, ref = line.partition(" ")
                if _OID_RE.match(oid) and oid not in refs:
                    shas.append(oid)
                    refs[oid] = self.display(ref)[0]
        if len(shas) > cap:
            self.truncated = True
        return shas[:cap], refs

    def scan_history(self, rev_range: str | None) -> None:
        shas, refs = self.tips(rev_range)
        if not shas:
            return
        self.grep_trees(shas, refs)
        for rule_id, pattern in RULES:  # git log -G takes one pattern: one call per rule
            tail = ("--end-of-options", rev_range) if rev_range else tuple(shas)
            res = self.run("log", f"-G{pattern}", *LOG_FLAGS, "--format=%H", *tail, "--")
            if res is None:
                return
            for sha in self._oids(res.stdout):
                if not self.add_hit(rule_id, commit=sha, via="log"):
                    return

    def scan_tracked_names(self) -> None:
        self._name_scan(("ls-files", "-z"), TRACKED_NAME_RULE)

    def scan_untracked_names(self) -> None:
        """Names only, no content: untracked files, ignored ones included (no
        `--exclude-standard`), against the same allowlist as `scan_tracked_names`."""
        self._name_scan(("ls-files", "-z", "--others"), UNTRACKED_NAME_RULE)

    def _name_scan(self, args: tuple[str, ...], rule_id: str) -> None:
        res = self.run(*args)
        if res is None:
            return
        parts = res.stdout.split(b"\0")
        if res.truncated:
            parts = parts[:-1]  # last name may be cut
        for raw in parts:
            name = _decode(raw)
            base = name.rsplit("/", 1)[-1]
            lowered = base.lower()
            if any(fnmatch.fnmatchcase(lowered, pat) for pat in TRACKED_NAME_PATTERNS):
                if not self.add_hit(rule_id, name=name):
                    return

    @staticmethod
    def _oids(data: bytes) -> list[str]:
        return [t for t in _decode(data).split() if _OID_RE.match(t)]


def _failure(code: str, **extra) -> dict:
    out = {"complete": False, "truncated": code == "timeout", "rules_version": RULES_VERSION,
           "hits": [], "counts": {}, "errors": [code]}
    out.update(extra)
    return out


def scan_secrets(root_dir: str, scope: str, rev_range: str | None, cfg: PocAuditConfig) -> dict:
    """The `scan_secrets` tool body. Never raises; an unexpected exception becomes the
    coded `internal_error` (its message and traceback are discarded)."""
    try:
        return _scan_secrets(root_dir, scope, rev_range, cfg)
    except Exception:  # noqa: BLE001 -- deliberate catch-all, nothing is echoed
        return _failure(ERR_INTERNAL)


def _scan_secrets(root_dir: str, scope: str, rev_range: str | None, cfg: PocAuditConfig) -> dict:
    deadline = Deadline(cfg.deadline_seconds)
    failure = _validate_scope(scope, rev_range)
    if failure is None:
        root, failure = resolve_root(root_dir, cfg, deadline)
    if failure is not None:
        return _failure(failure)
    scan = _Scan(root, cfg, deadline, scope)
    if scope == "worktree":
        scan.grep(("--untracked", "--no-exclude-standard"))
        scan.scan_untracked_names()
    elif scope == "index":
        scan.grep(("--cached",))
    elif scope == "stashes":
        scan.scan_stashes()
    elif scope == "history":
        scan.scan_history(rev_range)
    else:
        scan.scan_tracked_names()
    return scan.result()


def _validate_scope(scope: object, rev_range: object) -> str | None:
    if scope not in SCOPES:
        return ERR_BAD_SCOPE
    if rev_range is None:
        return None
    if scope != "history":
        return ERR_BAD_SCOPE
    if not isinstance(rev_range, str):
        return ERR_BAD_REV
    # git forbids ".." inside a ref name, so a ref-form value containing it is an
    # arbitrary range and is rejected; only <sha>..<sha> may carry "..".
    ref_ok = _REF_RE.match(rev_range) and ".." not in rev_range
    return None if ref_ok or _SHA_RANGE_RE.match(rev_range) else ERR_BAD_REV


def _fetch_head_time(root: str, deadline: Deadline) -> str | None:
    res = run_git(git_argv(root, "rev-parse", "--absolute-git-dir"), deadline, 4096)
    if res.error:
        return None
    out = _decode(res.stdout).rstrip("\n")
    try:
        info = os.lstat(Path(out) / "FETCH_HEAD")  # lstat: a symlinked FETCH_HEAD is not followed
        if not stat.S_ISREG(info.st_mode):
            return None
        return datetime.fromtimestamp(info.st_mtime, tz=timezone.utc).isoformat()
    except (OSError, ValueError, OverflowError):
        return None


def ref_containment(root_dir: str, commit: str, cfg: PocAuditConfig) -> dict:
    """The `ref_containment` tool body. `pushed` is True or "unknown", never False.
    Never raises; an unexpected exception becomes the coded `internal_error`."""
    try:
        return _ref_containment(root_dir, commit, cfg)
    except Exception:  # noqa: BLE001 -- deliberate catch-all, nothing is echoed
        return _containment_base(None, [ERR_INTERNAL])


def _containment_base(commit: str | None, errors: list[str]) -> dict:
    return {"commit": commit, "remote_refs": [], "tags": [], "local_branches": [],
            "pushed": "unknown", "last_fetch_time": None, "as_of_last_fetch": True,
            "complete": False, "truncated": False, "errors": errors}


def _ref_containment(root_dir: str, commit: str, cfg: PocAuditConfig) -> dict:
    deadline = Deadline(cfg.deadline_seconds)
    out = _containment_base(None, [])
    if not isinstance(commit, str) or not _COMMIT_RE.match(commit):
        out["errors"].append(ERR_BAD_REV)
        return out
    out["commit"] = commit
    root, failure = resolve_root(root_dir, cfg, deadline)
    if failure is not None:
        out["errors"].append(failure)
        return out
    res = run_git(
        git_argv(root, "for-each-ref", "--contains", commit, f"--count={cfg.max_refs + 1}",
                 "--format=%(refname)", "refs/remotes", "refs/tags", "refs/heads"),
        deadline, cfg.max_bytes)
    if res.error:
        out["errors"].append(res.error)
        out["truncated"] = res.truncated
        return out
    _classify_refs(out, _decode(res.stdout).splitlines(), cfg.max_refs)
    out["pushed"] = True if out["remote_refs"] else "unknown"
    out["last_fetch_time"] = _fetch_head_time(root, deadline)
    out["complete"] = not out["truncated"]
    return out


def _classify_refs(out: dict, refs: list[str], cap: int) -> None:
    if len(refs) > cap:
        out["truncated"] = True
        refs = refs[:cap]
    redacted: dict[str, int] = {}
    for ref in refs:
        shown, rule = redact_name(ref)
        if rule is not None:
            shown = f"{shown}#{redacted.setdefault(ref, len(redacted) + 1)}"
        if ref.startswith("refs/remotes/"):
            out["remote_refs"].append(shown)
        elif ref.startswith("refs/tags/"):
            out["tags"].append(shown)
        elif ref.startswith("refs/heads/"):
            out["local_branches"].append(shown)
