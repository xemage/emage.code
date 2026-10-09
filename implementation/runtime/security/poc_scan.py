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
* Errors are codes: not_a_toplevel, bad_scope, bad_rev, timeout, git_missing, git_failed,
  regex_unsupported (T612: the host regex library cannot compile the largest rule, see below).

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
  space, tab, CR, quote, `(` or `=`, unquoted names that end in a configuration word after `_` or
  `-` (ttl, timeout, url, ... see NON_SECRET_NAME_ENDINGS and SEV-4 below), a URL password that
  starts with `/`, `@` or a space or contains `/`, `@` or a space, a URL whose scheme is in upper
  case, and secrets in unlisted formats. (T609-13: a scheme of 32 or more characters is NOT a blind
  spot: the pattern is not anchored on the left, so a longer scheme still matches its last 32
  characters; only an upper-case scheme is missed.)
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

Further limits recorded by the T604 code review (security-review-poc-security-audit-code-v2,
SEV-1..SEV-6) and the T609 code review (security-review-t609-template-label-v1, T609-10..T609-13),
handled in T611 (contract `poc-security-engineer-tool-scoping-v4.md`):

* SEV-1: the work per line is bounded, because git grep was quadratic on one line that repeats a
  credential keyword or `eyJ`. Blind spots this creates: a credential keyword followed by more than
  more than 64 name characters (quoted rule; 65 to 67 for the unquoted rule, depending on the
  ending) before the `:` or `=` (NAME_RUN_MAX; the name-ending exclusion is judged only within that
  run), and a JWT whose first segment has more than 512 characters after its leading `eyJ`. An
  unquoted value is judged to its end up to 1025 characters; a run of 1025 or more non-space,
  non-quote, non-`(` characters is reported without that check (UNQUOTED_VALUE_MAX = 1024), so a
  `(` or quote beyond the bound is over-reported, never missed. Text beyond either bound is also
  unjudged for the label (T609-10): a line with a real credential whose name is longer than the
  name-run bound, followed by a template-shaped assignment that ends the line, is labelled
  `template-ref` for the visible match only. Every timeout still ends in `timeout` / `complete: false`.
* SEV-2: the Python loop over file names checks the shared deadline once per 4096 names; on expiry
  the scan stops with `timeout` and `complete: false`.
* SEV-3: a returned file, ref or tag name has control, format (bidi, zero width) and line/paragraph
  separator characters removed and is cut at 200 characters (`safe_name`); the redaction rules are
  tested on the raw name and on the cleaned name (T611-1: a token split by a zero-width character is
  still redacted) before the cut.
* SEV-4: a configuration-word ending excludes an unquoted name only after `_` or `-`
  (`SECRET_FILE`), so `SECRET_PROFILE` is reported. A camel-case or run-together name (`tokenUrl`,
  `passwordfile`) is therefore no longer excluded and is reported (a false positive).
* SEV-5, known false positives (pinned by tests, not fixed): a type annotation such as
  `password: Optional[str] = None`, `MAX_TOKENS=100000000` (an all-digit value under a name that
  contains "token"; there is no all-digits rule and no `tokens` exclusion, because `API_TOKENS=a,b`
  can be a real secret list) and `args.password`.
* SEV-6: a JWT test fixture (the jwt.io sample, an unsigned `eyJ...` token) is reported by the
  `jwt` rule like any token.
* T609-10: the label is judged on the matched text, not on the whole line. With several matches on
  one line only the last is anchored, so text BETWEEN two shape matches that no rule matches is not
  judged; and a line continuation (a YAML plain scalar that continues on the next line, a trailing
  backslash) is not judged either. A label therefore means "every matched value on this line is
  one template shape and the last ends the line", not "the whole logical value is a template".
* T609-11: `add_hit` also checks the label VALUES against the fixed sets (an invalid label, or a
  `template-ref` without a `template_shape`, is dropped; the hit stays), and `_anchored` raises an explicit error instead of using
  `assert`.
* T609-12: if the anchored check degrades (error, timeout, truncation, unparseable output), the
  hit simply carries no label and the scan stays `complete: true`; a missing label may therefore
  mean the check degraded. The scan assumes a quiescent tree: an edit between the two `git grep`
  passes could in theory shift a line, which at worst gives a wrong or missing label.

Further limits handled in T612 (contract `poc-security-engineer-tool-scoping-v5.md`):

* T611-2: `safe_name` changes the shown name, so a hit whose shown path differs from the real path
  carries `path_altered: true` (`add_hit` computes it from the raw name: `safe_name` changed it, or the
  bytes were not valid UTF-8 and were shown as U+FFFD, see `_decode_name`; a valid name with a literal
  U+FFFD character is not altered; a name shown as
  `<redacted-by-rule:ID>` carries `path_index` instead and no marker). Such a hit cannot be flagged
  (agent text): the shown text does not identify one file, and two different files can show the same
  text.
* T611-3: the bounded repeats `{7,1024}`, `{1024}` and `{10,512}` need a regex library whose
  `RE_DUP_MAX` is at least 1024 (glibc: 32767; some other libraries, for example musl or BSD ones: 255, unverified here). Every
  scan that runs `git grep -E` or `git log -G` first compiles the largest rule once through
  `git_executor` (`_regex_selftest`); if that call fails while a trivial pattern compiles (usually a low
  `RE_DUP_MAX`) the scan ends `regex_unsupported`,
  `complete: false`, no hits and no clean claim, instead of a bare `git_failed`.
"""
from __future__ import annotations

import fnmatch
import os
import re
import stat
from collections import Counter
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from implementation.runtime.security.git_executor import (
    EMPTY_TREE,
    ERR_GIT_FAILED,
    ERR_TIMEOUT,
    LOG_FLAGS,
    Deadline,
    GitResult,
    git_argv,
    run_git,
)

RULES_VERSION = "2026-10-09.5"


def _ci(word: str) -> str:
    """Case-insensitive ERE for a word (works in git ERE and in Python `re`)."""
    return "".join(f"[{c.upper()}{c.lower()}]" if c.isalpha() else c for c in word)


_NAME_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789_-"


def _name_class(chars: set[str]) -> str:
    """Bracket expression for lower-case name characters, letters in both cases."""
    parts = [c.upper() + c if c.isalpha() else c for c in sorted(chars) if c != "-"]
    return "[" + "".join(parts) + ("-" if "-" in chars else "") + "]"


# SEV-1 (T611): the run of name characters between a credential keyword and the `:` or `=` is
# bounded. An unbounded run made git grep quadratic on one line that repeats a keyword (60 s,
# fail closed). Blind spot: a keyword followed by more than 64 name characters (65 to 67 in the
# unquoted rule) before the
# separator is not matched (a longer name is also excluded-ending-checked only within the bound).
NAME_RUN_MAX = 64


def _not_ending(words: tuple[str, ...], max_run: int = NAME_RUN_MAX) -> str:
    """ERE (no lookaround) for name-character strings, empty included, that end in NONE of
    `words` (case-insensitive). Built by peeling the last character off every word. The free run
    in front of the last character is at most `max_run` characters (SEV-1)."""
    last = {w[-1] for w in words}
    alts = ["[A-Za-z0-9_-]{0," + str(max_run) + "}" + _name_class(set(_NAME_CHARS) - last)]
    for c in sorted(last):
        rest = tuple(w[:-1] for w in words if w[-1] == c)
        if all(rest):  # a one-letter word would forbid every string ending in c
            alts.append(_not_ending(rest, max_run) + _name_class({c}))
    return "(" + "|".join(alts) + ")?"


_CREDENTIAL_WORDS = "(" + "|".join([
    _ci("password"), _ci("passwd"), _ci("pwd"), _ci("secret"),
    _ci("api") + "[-_]?" + _ci("key"), _ci("access") + "[-_]?" + _ci("key"),
    _ci("private") + "[-_]?" + _ci("key"), _ci("token")]) + ")"
# Name endings that are configuration about a secret, not a secret (user decision 2026-10-09).
NON_SECRET_NAME_ENDINGS = ("ttl", "timeout", "url", "uri", "endpoint", "path", "file", "dir",
                           "name", "expiry", "expires", "expiration", "length", "size", "type",
                           "header", "env", "var")
# SEV-4 (T611): an ending only counts after a separator, so `SECRET_FILE` is excluded but
# `SECRET_PROFILE` (which merely ends in the letters "file") is reported. Consequence: a
# camel-case or run-together name (`tokenUrl`, `passwordfile`) is no longer excluded.
NON_SECRET_NAME_SUFFIXES = tuple(sep + word for word in NON_SECRET_NAME_ENDINGS for sep in "_-")
# The value: 8 to UNQUOTED_VALUE_MAX + 1 (1025) characters without space/quote/( that end at a space or the end
# of the line, OR a longer run (UNQUOTED_VALUE_MAX + 1 characters without space/quote/( ) reported
# without looking for its end. The bound (SEV-1) stops the quadratic cost of `password=` repeated
# inside one very long token that ends in `(` or a quote; the second branch keeps a long secret
# visible. Residual: a token longer than the bound that contains `(` or a quote after the bound is
# reported (over-reporting, the safe direction).
UNQUOTED_VALUE_MAX = 1024
_UV_FIRST = "[^ \t\r\"'(=]"
_UV_REST = "[^ \t\r\"'(]"
_UNQUOTED_BODY = _UV_FIRST + _UV_REST + "{7," + str(UNQUOTED_VALUE_MAX) + "}"
_UNQUOTED_VALUE = ("(" + _UNQUOTED_BODY + "([ \t\r]|$)|"
                   + _UV_FIRST + _UV_REST + "{" + str(UNQUOTED_VALUE_MAX) + "})")

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
    # SEV-1: the header segment is bounded ({10,512}); an unbounded run made git grep quadratic on a
    # line of repeated `eyJ`. Blind spot: a JWT first segment with more than 512 characters after its leading `eyJ`. The
    # payload segment stays unbounded: it is reached only after `.eyJ` and a match consumes it.
    ("jwt", r"eyJ[A-Za-z0-9_-]{10,512}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]*"),
    ("sk-api-key", r"(^|[^A-Za-z0-9_])sk-(ant-|proj-)?[A-Za-z0-9_-]{20,}"),
    # URL with embedded credentials; a password starting with / @ or a space is a delimiter case.
    # The scheme is bounded ({0,31}): an unbounded run made git grep quadratic (minutes) on one
    # very long line of scheme characters, which L-1's `-o` fix now lets reach the scanner.
    ("url-embedded-credentials", r"[a-z][a-z0-9+.-]{0,31}://[^/:@ ]+:[^/@ ][^/@ ]{2,}@"),
    (
        "credential-assignment",
        _CREDENTIAL_WORDS
        # up to NAME_RUN_MAX name characters, an optional closing quote, then : or = (JSON/YAML/.env/code)
        + "[A-Za-z0-9_-]{0," + str(NAME_RUN_MAX) + "}[\"']?[ \t]*[:=][ \t]*[\"'][^\"'][^\"']{7,}[\"']",
    ),
    (
        "unquoted-credential-assignment",
        _CREDENTIAL_WORDS + _not_ending(NON_SECRET_NAME_SUFFIXES)
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
TEMPLATE_SHAPE_NAMES = frozenset(name for name, _ in TEMPLATE_SHAPES)
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
# Every key a `scan_secrets` hit may carry (the contract v3 output list). Pinned by a test.
# T612 (contract v5) adds `path_altered`.
HIT_KEYS = frozenset({"rule_id", "scope", "path_or_redacted", "path_index", "line", "commit", "ref",
                      "via", "value_shape", "template_shape", "path_altered"})


def _anchored(rule_id: str, pattern: str) -> str:
    """The rule pattern with its value tail replaced by `[ \t\r]*$` (value must end the line).
    T609-11: an explicit check, not an `assert` (which `python -O` removes). A pattern that no
    longer has the expected tail raises at import time, so a drifted rule cannot silently produce
    a wrong anchored pattern (the scan never starts)."""
    if rule_id == "unquoted-credential-assignment":
        if not pattern.endswith(_UNQUOTED_VALUE):
            raise ValueError("unquoted rule does not end with the expected value group")
        # only the bounded first branch can end the line; the longer-run branch is never anchored
        return pattern[:-len(_UNQUOTED_VALUE)] + _UNQUOTED_BODY + _LINE_END
    if not pattern.endswith("[\"']"):
        raise ValueError("quoted rule does not end with its closing quote")
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
ERR_REGEX_UNSUPPORTED = "regex_unsupported"  # T611-3: the host regex library cannot compile a rule


@dataclass(frozen=True)
class PocAuditConfig:
    allowed_root: Path
    deadline_seconds: float = 60.0
    max_refs: int = 200
    max_stashes: int = 50
    max_hits: int = 500
    max_bytes: int = 4_000_000


NAME_MAX_CHARS = 200  # SEV-3: longest name text returned (a longer one ends in "...")
_NAME_CHECK_EVERY = 4096  # SEV-2: the name loop looks at the deadline once per this many names
_STRIPPED_CATEGORIES = ("Cc", "Cf", "Zl", "Zp")  # control, format (bidi, zero width), line/paragraph separators


def _strip_name(name: str) -> str:
    return "".join(ch for ch in name if unicodedata.category(ch) not in _STRIPPED_CATEGORIES)


def _cap_name(name: str) -> str:
    return name[:NAME_MAX_CHARS - 3] + "..." if len(name) > NAME_MAX_CHARS else name


def safe_name(name: str) -> str:
    """SEV-3: a returned name without control, format (bidi, zero width) or line/paragraph
    separator characters and at most NAME_MAX_CHARS characters, so a hostile file name cannot
    become instructions or an escape sequence in the reviewing agent's context. It does not decide
    redaction: `redact_name` tests the rules on the raw AND the cleaned name first."""
    return _cap_name(_strip_name(name))


def redact_name(name: str) -> tuple[str, str | None]:
    """-> (safe_name(name), None) or ("<redacted-by-rule:ID>", rule_id) if a rule matches the name.
    T611-1: each rule is tested on the raw name and on the name with the characters of `safe_name`
    removed (before the length cap), so a token split by a zero-width or control character
    (`AKIA<ZWSP>...`) is still redacted. The cap comes last."""
    cleaned = _strip_name(name)
    for rule_id, rx in _COMPILED:
        if rx.search(name) or (cleaned != name and rx.search(cleaned)):
            return f"<redacted-by-rule:{rule_id}>", rule_id
    return _cap_name(cleaned), None


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")


def _decode_name(raw: bytes) -> tuple[str, bool]:
    """-> (text, lossy). `lossy` is True exactly when `raw` is not valid UTF-8, so `_decode` replaced
    bytes with U+FFFD and two different names can show the same text (T612, SEC-1). It is derived
    from the raw bytes, not from a U+FFFD in the text: a valid name that contains a literal U+FFFD
    character decodes cleanly and is not lossy."""
    try:
        return raw.decode("utf-8"), False
    except UnicodeDecodeError:
        return _decode(raw), True


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
        fields.pop("path_altered", None)  # never taken from a caller: derived from the raw name below
        lossy = fields.pop("name_lossy", False) is True  # set by the module's own decode of the raw bytes
        if name is not None:
            hit["path_or_redacted"], idx = self.display(name)
            if idx is not None:
                hit["path_index"] = idx
            elif hit["path_or_redacted"] != name or lossy:
                # T611-2: safe_name changed the name, or the bytes were not valid UTF-8 (U+FFFD
                # replacement): the shown text is not the real path and may be shared by other files
                hit["path_altered"] = True
        hit.update({k: v for k, v in fields.items() if v is not None})
        for key in set(hit) - HIT_KEYS:  # contract v3 allow-list, enforced: an unknown key is dropped
            del hit[key]
        self._check_label(hit)
        self._check_path_altered(hit)
        self.hits.append(hit)
        return True

    @staticmethod
    def _check_label(hit: dict) -> None:
        """T609-11: the label VALUES are enforced like the keys, against the fixed sets. An unknown
        `value_shape`, an unknown `template_shape`, a `template-ref` without a `template_shape` or a
        `template_shape` on `bare-dollar-name` is dropped: the hit stays, without a label."""
        shape, template = hit.get("value_shape"), hit.get("template_shape")
        if shape is None and template is None:
            return
        valid = ((shape == TEMPLATE_REF and isinstance(template, str) and template in TEMPLATE_SHAPE_NAMES)
                 or (shape == BARE_DOLLAR and template is None))
        if not valid:
            hit.pop("value_shape", None)
            hit.pop("template_shape", None)

    @staticmethod
    def _check_path_altered(hit: dict) -> None:
        """T612: `path_altered` is either absent or exactly `True`, and only on a hit that shows a
        path (`path_or_redacted`) that is not a redacted one (`path_index`). Anything else is
        dropped, so the key never appears in a form the agent text does not describe."""
        if "path_altered" not in hit:
            return
        if hit["path_altered"] is not True or "path_or_redacted" not in hit or "path_index" in hit:
            del hit["path_altered"]

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
                name, lossy = _decode_name(raw[m.end():] if m else raw)
                ref = (refs or {}).get(commit) if commit else None
                label = {}
                if (raw, line) in ends_line and redact_name(name)[1] is None:
                    label = _label_for(found)
                if not self.add_hit(rule_id, name=name, name_lossy=lossy, line=line, commit=commit, ref=ref, **label):
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
        for index, raw in enumerate(parts):
            # SEV-2: the loop is Python work outside any subprocess; bound it by the same deadline.
            if index % _NAME_CHECK_EVERY == 0 and self.deadline.remaining() <= 0:
                self._error(ERR_TIMEOUT, True)  # complete: false, never a silent partial pass
                return
            name, lossy = _decode_name(raw)
            base = name.rsplit("/", 1)[-1]
            lowered = base.lower()
            if any(fnmatch.fnmatchcase(lowered, pat) for pat in TRACKED_NAME_PATTERNS):
                if not self.add_hit(rule_id, name=name, name_lossy=lossy):
                    return

    @staticmethod
    def _oids(data: bytes) -> list[str]:
        return [t for t in _decode(data).split() if _OID_RE.match(t)]


_REPEAT_RE = re.compile(r"\{(\d+)(?:,(\d+))?\}")


def _largest_repeat(pattern: str) -> int:
    """The largest repeat count `{n}` / `{n,m}` in a pattern (0 if none)."""
    return max((int(n) for pair in _REPEAT_RE.findall(pattern) for n in pair if n), default=0)


def selftest_pattern() -> str:
    """The rule pattern the self-test compiles: the one with the largest repeat count, then the
    longest (today the unquoted-credential rule: `{7,1024}` and `{1024}`, 7560 characters). Every
    other rule has a smaller repeat count, so a library that compiles this one compiles them all.
    The anchored variants used for the label (`ANCHORED_RULES`) are shorter and carry no larger
    repeat count (pinned by a test)."""
    return max((pat for _, pat in RULES), key=lambda pat: (_largest_repeat(pat), len(pat)))


def _selftest_call(root: str, pattern: str, deadline: Deadline, max_bytes: int):
    # The empty tree is a built-in git object: nothing is read, only the pattern is compiled.
    return run_git(git_argv(root, "grep", "--no-color", "-q", "-E", "-e", pattern, EMPTY_TREE, "--"),
                   deadline, max_bytes, (0, 1))


def _regex_selftest(root: str, cfg: PocAuditConfig, deadline: Deadline) -> str | None:
    """T611-3: compile the largest rule once through `git grep` (same executor, hardening and
    aggregate deadline as every other call) and return None or an error code. A compile failure
    exits non-zero (`git_failed`); a second, trivial pattern then tells "the compile call failed while a
    trivial pattern compiled" (`regex_unsupported`, usually a low `RE_DUP_MAX`) from any other git
    failure (`git_failed`, unchanged). The
    control call runs only on the failure path: a normal scan pays for exactly one cheap call.
    Fails closed: any error, timeout included, ends the scan; nothing is ever treated as a pass."""
    res = _selftest_call(root, selftest_pattern(), deadline, cfg.max_bytes)
    if res.error is None:
        return None
    if res.error != ERR_GIT_FAILED:
        return res.error
    control = _selftest_call(root, "a", deadline, cfg.max_bytes)
    return ERR_REGEX_UNSUPPORTED if control.error is None else control.error


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
    if scope != "tracked_names":  # the only scope that runs no `git grep -E` and no `git log -G`
        failure = _regex_selftest(root, cfg, deadline)
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
