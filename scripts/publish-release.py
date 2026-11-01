#!/usr/bin/env python3
"""Regenerate CHANGELOG.md and publish a GitLab release fail-closed.

The release has ONE release document, ``docs/releases/<tag>.md`` (it starts
``# Release <tag>``). The GitLab Release description is that document, whole and
unchanged (T640 / ruling C3). The commit list generated from Conventional
Commits (merge commits excluded, filter F1) goes into ``CHANGELOG.md`` only,
which is the only file this script writes; no root ``release-notes.md`` is
written. Offline rehearsal: ``scripts/dry-run-publish-release.py``.

The API token is read from an environment variable named by ``--token-env``
(CI: ``--token-env CI_JOB_TOKEN --token-header JOB-TOKEN``, the GitLab job token;
T686), so the value never appears in argv, in the process list or in a job log.
``--token-header`` names the one HTTP header that carries it and is limited to a
fixed allowlist (``TOKEN_HEADERS``: ``PRIVATE-TOKEN``, the default, and
``JOB-TOKEN``). ``--token`` is still accepted but deprecated: it prints a warning
(never the value) because argv is world-readable on a runner.
The API target is parsed, not prefix-matched (``validate_api_target``), the
host can be pinned (``--expected-host``, default ``CI_SERVER_HOST``), and the
HTTP opener refuses every redirect, so the token header is never re-sent to a
second location (T675).
"""

from __future__ import annotations

import argparse
import datetime as dt
import http.client
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable, NamedTuple


ROOT = Path(__file__).resolve().parent.parent
RELEASE_TITLE_MAP = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance",
    "refactor": "Refactor",
    "docs": "Documentation",
    "test": "Tests",
    "ci": "CI",
    "chore": "Chores",
    "revert": "Reverts",
}
SUBJECT_RE = re.compile(r"^(?P<type>[a-z]+)(?:\([^)]+\))?(?:!)?:\s+(?P<desc>.+)$")
MERGE_BRANCH_RE = re.compile(r"^Merge branch '([^']+)' into '([^']+)'$")
TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$")  # the CI tag rule
SIMPLE_RELEASE_BRANCH_RE = re.compile(r"^release/v\d+\.\d+\.\d+$")
# A released changelog entry: any H2 except ``## [Unreleased]`` (T716, D-T710-2).
RELEASED_HEADING_RE = re.compile(r"^## (?!\[Unreleased\][ \t]*$)", re.M | re.I)
# The only API base shape: .../api/v4. A segment is never "." or "..".
API_PATH_RE = re.compile(r"(/(?!\.{1,2}(?:/|$))[A-Za-z0-9._~-]+)*/api/v4")
ENV_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")
# T676 (SEC-T675-10), T685 (SEC-T676-12), T716 (SEC-T685-02): a commit subject loses every character that makes a
# changelog line read differently from its bytes. A CATEGORY test, so a code point the old explicit class missed
# (U+180E, U+206A-206F, U+FFF0-FFF8, U+1BCA0-1BCA3, U+1D173-1D17A, the unassigned rest of U+E0000-E0FFF) cannot slip
# through: Cc (C0 and C1 controls), Cf (format: zero-width, LRM/RLM, ALM, bidi embeddings and isolates, BOM, soft
# hyphen, Unicode tags), Cs (surrogates), Co (private use), Cn (unassigned in this Python's Unicode database), Zl and
# Zp (line and paragraph separators). Plus the default-ignorable or blank code points whose category is Mn, Lo or So:
# U+034F COMBINING GRAPHEME JOINER, the Hangul fillers U+115F/U+1160/U+3164/U+FFA0, the Khmer inherent vowels
# U+17B4/U+17B5, the Mongolian variation selectors U+180B-180D and U+180F, the braille blank U+2800, and the variation
# selectors U+FE00-FE0F and U+E0100-E01EF. Cosmetic cost, by design and tested: U+200D (ZWJ, Cf) and U+FE0F (VS16) go,
# so an emoji ZWJ sequence prints as its separate emoji and an emoji loses its presentation selector; no emoji code
# point is removed. A character newer than this Python's Unicode database counts as Cn and is removed too.
# Markdown is escaped when the changelog is rendered (markdown_entry), not here.
SUBJECT_UNSAFE_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"})
SUBJECT_INVISIBLE_MARKS = frozenset(
    "\u034f\u115f\u1160\u17b4\u17b5\u180b\u180c\u180d\u180f\u2800\u3164\uffa0"
    + "".join(map(chr, range(0xFE00, 0xFE10))) + "".join(map(chr, range(0xE0100, 0xE01F0)))
)
HTTP_TIMEOUT_SECONDS = 30
# T686: the only headers the token may travel in (a fixed allowlist, never taken from input); the default keeps the
# behaviour of every earlier call. The job token goes in JOB-TOKEN (GitLab "Releases API" accepts it), a personal,
# project or group access token in PRIVATE-TOKEN.
DEFAULT_TOKEN_HEADER = "PRIVATE-TOKEN"
TOKEN_HEADERS = (DEFAULT_TOKEN_HEADER, "JOB-TOKEN")
# Never passed to git: both CI token variables by name (the job token is in every job's environment), plus
# main() adds the --token-env name.
WITHHELD_ENV_NAMES = {"WIKI_TOKEN", "CI_JOB_TOKEN"}
# T686 (SEC-T686-01): withholding by name is not enough: GitLab exposes the job token under a second name
# (CI_REGISTRY_PASSWORD) and inside URL-shaped variables (CI_REPOSITORY_URL = https://gitlab-ci-token:<token>@host/...).
# So the child environment is (1) an ALLOWLIST of names git needs and (2) minus every variable whose value contains
# one of the secret values (the values of the withheld names, and the token main() resolved, also from --token).
# The same rule is mirrored in the release job's apk bootstrap in .gitlab-ci.yml (tests pin the two together).
# git reads the checkout credential from .git/config (the clone URL the runner wrote), not from the environment.
# T716 (SEC-T686-07): every name with the reason it is passed. Dropped, because each is a configuration or execution
# channel that neither the image's git nor apk needs: GIT_EXEC_PATH (the directory git runs its sub-commands from),
# GIT_ASKPASS (a program git runs to ask for a credential; the checkout credential is in .git/config and
# GIT_TERMINAL_PROMPT=0 makes a missing one fail), GIT_CONFIG_GLOBAL and GIT_CONFIG_SYSTEM (another configuration file,
# which can set core.fsmonitor, core.sshCommand or a credential helper) and GIT_CONFIG_COUNT/KEY_n/VALUE_n (configuration
# entries from the environment: the same channel, and a re-encoded token inside a VALUE_n passed the substring filter).
# With them gone git reads its defaults. That the runner sets none of them for the job is (unverified) until a tag
# pipeline runs. The apk bootstrap in .gitlab-ci.yml passes exactly the CHILD_ENV_APK_REASONS names and the LC_ rule.
_PROXY = "egress proxy of a runner without direct access (libcurl for git, apk); TLS still checks the server"
_CA = "trust anchor of a private CA or a TLS-inspecting proxy; a path only, it adds no code or configuration"
CHILD_ENV_APK_REASONS = {
    "PATH": "finds git and apk",
    "HOME": "per-user files of git and apk live under it; without it git warns and guesses",
    "LANG": "locale of messages and of path-name decoding",
    "LANGUAGE": "message language (gettext)",
    "TMPDIR": "where temporary files go",
    "TZ": "time zone of the dates git prints",
    "SSL_CERT_FILE": _CA + " (OpenSSL)",
    "SSL_CERT_DIR": _CA + " (OpenSSL)",
    "CURL_CA_BUNDLE": _CA + " (curl; whether libcurl inside git reads it is unverified)",
    "http_proxy": _PROXY, "https_proxy": _PROXY, "HTTP_PROXY": _PROXY, "HTTPS_PROXY": _PROXY,
    "ALL_PROXY": _PROXY + " (libcurl's proxy for every scheme)",
    "no_proxy": "hosts that bypass the proxy (an internal GitLab host)",
    "NO_PROXY": "hosts that bypass the proxy (an internal GitLab host)",
}
CHILD_ENV_REASONS = {
    **CHILD_ENV_APK_REASONS,
    "GIT_SSL_CAINFO": _CA + " (git's https, a self-managed GitLab)",
    "GIT_SSL_CAPATH": _CA + " (git's https, a self-managed GitLab)",
    "GIT_TERMINAL_PROMPT": "only turns the credential prompt off, so a missing credential fails instead of waiting",
    "GIT_CONFIG_NOSYSTEM": "only turns the system configuration file off; it cannot add configuration",
}
CHILD_ENV_APK_NAMES = frozenset(CHILD_ENV_APK_REASONS)
CHILD_ENV_NAMES = frozenset(CHILD_ENV_REASONS)
# T716 (SEC-T686-08): the locale variables (LC_ALL, LC_CTYPE, ...); the apk bootstrap uses this same pattern text.
CHILD_ENV_PATTERN = re.compile(r"LC_[A-Z_]+")
WITHHELD_ENV_VALUES: set[str] = set()  # main() adds the resolved token (it may come from --token, not from a name)


class ReleasePublishError(RuntimeError):
    """Raised when release artifact generation or publishing fails.

    ``status`` is the HTTP status code when the failure is an HTTP error response.
    """

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


def validate_tag(tag: str) -> str:
    """Fail closed unless ``tag`` matches the CI release-tag rule (no newline, no path parts)."""
    if not TAG_RE.fullmatch(tag):
        raise ReleasePublishError(f"invalid release tag {tag!r}: must match {TAG_RE.pattern}")
    return tag


def _api_url_problem(api_v4_url: str, expected_host: str | None) -> str | None:
    """Return why ``api_v4_url`` is not an acceptable API base, or None when it is."""
    if not api_v4_url.startswith("https://"):
        return "must start with https://"
    if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 or ch == "\\" for ch in api_v4_url):
        return "must not contain whitespace, control characters or backslashes"
    try:
        parts = urllib.parse.urlsplit(api_v4_url)
        parts.port  # noqa: B018 -- raises ValueError on a malformed or out-of-range port
    except ValueError:
        return "is not a valid URL"
    if parts.scheme != "https" or not parts.hostname:
        return "must be an https URL with a host name"
    if "@" in parts.netloc or parts.username is not None or parts.password is not None:
        return "must not contain user information"
    if parts.query or parts.fragment or "?" in api_v4_url or "#" in api_v4_url:
        return "must not contain a query or a fragment"
    if not API_PATH_RE.fullmatch(parts.path):
        return "must end with /api/v4 (no trailing slash)"
    if expected_host is not None and parts.hostname.lower() != expected_host.strip().lower():
        return "host does not match the expected GitLab host"
    return None


def validate_api_target(api_v4_url: str, project_id: str, expected_host: str | None = None) -> None:
    """Fail closed unless the API base is a clean https ``.../api/v4`` URL and the project id is digits.

    ``expected_host`` (CI: ``CI_SERVER_HOST``) pins the host name when given, so a
    wrong ``--api-v4-url`` can never receive the token. The checks are on a real
    URL parse: https only, a host name, no user information, no query, no fragment.
    """
    problem = _api_url_problem(api_v4_url, expected_host)
    if problem:
        raise ReleasePublishError(f"invalid --api-v4-url: {problem}")
    if not (project_id.isascii() and project_id.isdigit()):
        raise ReleasePublishError("invalid --project-id: must be all ASCII digits")


def resolve_expected_host(flag: str | None, environ: dict[str, str] | None = None) -> str | None:
    """The host to pin: ``--expected-host``, else ``$CI_SERVER_HOST``; required in CI, never empty.

    An empty value (an unset CI variable expands to ``""``) is an error, not "no pin".
    In CI (``$CI`` set) the pin is mandatory.
    """
    environ = os.environ if environ is None else environ
    host = flag if flag is not None else environ.get("CI_SERVER_HOST")
    if host is None:
        if environ.get("CI"):
            raise ReleasePublishError("--expected-host is required in CI (pass \"${CI_SERVER_HOST}\")")
        return None
    if not host.strip():
        raise ReleasePublishError("invalid --expected-host: must not be empty")
    return host.strip()


def resolve_token(token: str | None, token_env: str | None, environ: dict[str, str] | None = None) -> str:
    """Return the API token from ``--token-env`` (preferred) or the deprecated ``--token``.

    Messages name the variable, never the value. A token with a control character
    is refused (it could split an HTTP header).
    """
    environ = os.environ if environ is None else environ
    if token and token_env:
        raise ReleasePublishError("give either --token-env or --token, not both")
    if token_env:
        if not ENV_NAME_RE.fullmatch(token_env):
            raise ReleasePublishError("invalid --token-env: must be an environment variable name")
        value = environ.get(token_env, "")
        if not value:
            raise ReleasePublishError(f"environment variable {token_env} is not set or empty")
    elif token:
        print(
            "release-publish: warning: --token puts the token in argv; use --token-env NAME",
            file=sys.stderr,
        )
        value = token
    else:
        raise ReleasePublishError("no API token: set --token-env NAME (or use --skip-api)")
    if CONTROL_CHARS_RE.search(value):
        raise ReleasePublishError("the API token contains a control character")
    return value


def secret_values(environ: dict[str, str]) -> set[str]:
    """The non-empty values that must not reach a child: those of the withheld names, plus the resolved token."""
    values = {environ[name] for name in WITHHELD_ENV_NAMES if environ.get(name)}
    return values | {v for v in WITHHELD_ENV_VALUES if v}


def child_environment(environ: dict[str, str] | None = None) -> dict[str, str]:
    """The environment git gets: allowlisted names only, and no variable whose value contains a secret value.

    Names alone do not protect the job token (``CI_REGISTRY_PASSWORD`` and ``CI_REPOSITORY_URL`` carry it too), so a
    variable is dropped when its value contains the token, whatever it is called.
    """
    environ = os.environ if environ is None else environ
    secrets = secret_values(environ)
    return {
        k: v for k, v in environ.items()
        if (k in CHILD_ENV_NAMES or CHILD_ENV_PATTERN.fullmatch(k))
        and k not in WITHHELD_ENV_NAMES and not any(secret in v for secret in secrets)
    }


def run_git(args: list[str]) -> str:
    """Stdout of git, decoded from bytes: text mode would turn a lone CR in a commit subject into a line break."""
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        env=child_environment(),
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).decode("utf-8", "replace").strip()
        raise ReleasePublishError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.decode("utf-8", "replace").strip()


def ensure_full_history() -> None:
    """Unshallow CI clones so release notes include the full commit range."""
    is_shallow = run_git(["rev-parse", "--is-shallow-repository"]).strip()
    if is_shallow == "true":
        run_git(["fetch", "--unshallow", "--tags", "origin"])


def tag_sort_key(tag: str) -> tuple:
    """Semantic-version precedence of a release tag (T716, T717-D3): ``v1.0.0-rc.1`` < ``v1.0.0`` < ``v1.1.0``.

    git's ``--sort=v:refname`` without ``versionsort.suffix`` puts ``v1.0.0-rc.1`` AFTER ``v1.0.0``, so the commit range
    of the next release would start at the rc. As ``semver_key`` in check-main-develop-drift.py, a pre-release sorts
    before its final; pre-release identifiers compare as SemVer 2.0.0 says (numbers numerically, below names).
    """
    core, _, pre = tag[1:].partition("-")
    major, minor, patch = (int(x) for x in core.split("."))
    idents = tuple((0, int(x), "") if x.isdigit() else (1, 0, x) for x in pre.split(".")) if pre else ()
    return (major, minor, patch, 0 if pre else 1, idents)


def get_tag_list() -> list[str]:
    """Release tags, newest first by semantic version (not git's version sort)."""
    output = run_git(["tag", "--list"])
    # Only release tags: a stray tag name must never become ``previous_tag`` (and so
    # reach git arguments and CHANGELOG.md).
    tags = [line for line in output.splitlines() if TAG_RE.fullmatch(line)]
    return sorted(tags, key=tag_sort_key, reverse=True)


def resolve_previous_tag(current_tag: str, tags: list[str]) -> str | None:
    try:
        index = tags.index(current_tag)
    except ValueError as exc:
        raise ReleasePublishError(f"current tag '{current_tag}' not found in local git tags") from exc
    return tags[index + 1] if index + 1 < len(tags) else None


def _revision_range(current_tag: str, previous_tag: str | None) -> str:
    if previous_tag is None:
        return current_tag
    # Prefer merge-base range when histories diverged (non-linear GitFlow).
    try:
        base = run_git(["merge-base", "--end-of-options", previous_tag, current_tag])
        count = run_git(["rev-list", "--count", "--end-of-options", f"{base}..{current_tag}"])
        direct = run_git(
            ["rev-list", "--count", "--end-of-options", f"{previous_tag}..{current_tag}"]
        )
        if int(count) >= int(direct):
            return f"{base}..{current_tag}"
    except ReleasePublishError:
        pass
    return f"{previous_tag}..{current_tag}"


def subject_char_is_unsafe(char: str) -> bool:
    """True for a character a changelog subject must not keep (see SUBJECT_UNSAFE_CATEGORIES)."""
    return unicodedata.category(char) in SUBJECT_UNSAFE_CATEGORIES or char in SUBJECT_INVISIBLE_MARKS


def strip_unsafe_subject(text: str) -> str:
    return "".join(char for char in text if not subject_char_is_unsafe(char))


def get_commit_subjects(current_tag: str, previous_tag: str | None) -> list[str]:
    revision = _revision_range(current_tag, previous_tag)
    # Filter F1: merge commits are excluded structurally, not by subject text.
    # Framed by NUL characters and decoded from bytes (SEC-T676-05): neither a lone CR (text mode would turn it into "\n"), nor
    # \x0b, \x0c, \x1c-\x1e, \x85, \u2028, \u2029 (str.splitlines()), nor "\n" can split one subject into several
    # changelog entries; git never puts a NUL inside a subject.
    output = run_git(["log", "--no-merges", "--pretty=%s%x00", "--end-of-options", revision, "--"])
    subjects = [strip_unsafe_subject(chunk).strip() for chunk in output.split("\x00")]
    subjects = [line for line in subjects if line]
    if not subjects:
        raise ReleasePublishError(f"no commits found for revision range '{revision}'")
    return subjects


def load_release_brief(tag: str) -> str:
    """Return the release document of ``tag`` exactly as stored; fail closed if missing or blank."""
    validate_tag(tag)
    releases_dir = ROOT / "docs" / "releases"
    brief_path = releases_dir / f"{tag}.md"
    if not brief_path.is_file():
        raise ReleasePublishError(
            f"missing release brief: docs/releases/{tag}.md "
            "(copy docs/releases/_template.md and fill Install + Highlights)"
        )
    # The tagged commit controls this path: a symlink (or a symlinked docs/releases)
    # could publish any file the runner can read as the release description.
    expected_dir = ROOT.resolve() / "docs" / "releases"
    if releases_dir.is_symlink() or brief_path.is_symlink() or not brief_path.resolve().is_relative_to(expected_dir):
        raise ReleasePublishError(f"release brief must be a regular file under docs/releases: {tag}.md")
    try:
        brief = brief_path.read_bytes().decode("utf-8")  # no newline translation: byte-for-byte
    except (OSError, UnicodeDecodeError) as exc:
        raise ReleasePublishError(f"release brief is not readable UTF-8 text: docs/releases/{tag}.md") from exc
    if not brief.strip():
        raise ReleasePublishError(f"release brief is empty: docs/releases/{tag}.md")
    return brief


def classify_subjects(subjects: Iterable[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {title: [] for title in RELEASE_TITLE_MAP.values()}
    grouped["Other"] = []
    for subject in subjects:
        match = SUBJECT_RE.match(subject)
        if not match:
            merge_match = MERGE_BRANCH_RE.match(subject)
            if merge_match:
                source_branch = merge_match.group(1)
                target_branch = merge_match.group(2)
                if source_branch.startswith("bugfix/"):
                    grouped["Bug Fixes"].append(
                        f"merge {source_branch} into {target_branch}"
                    )
                    continue
                if source_branch.startswith("feature/"):
                    grouped["Features"].append(
                        f"merge {source_branch} into {target_branch}"
                    )
                    continue
                if source_branch.startswith("release/"):
                    grouped["Chores"].append(
                        f"merge {source_branch} into {target_branch}"
                    )
                    continue

            if SIMPLE_RELEASE_BRANCH_RE.match(subject):
                grouped["Chores"].append(f"release branch {subject}")
                continue

            grouped["Other"].append(subject)
            continue
        commit_type = match.group("type")
        title = RELEASE_TITLE_MAP.get(commit_type, "Other")
        grouped[title].append(match.group("desc"))
    return grouped


# T716 (SEC-T675-10): a changelog entry is a commit subject, so it must not become Markdown structure: no raw HTML
# (an unclosed "<!--" would hide every later entry), no link or image, no character reference (``&#8238;`` would bring
# back the bidi override the subject lost), no heading, list, rule or fence at the start of the item. Outside code
# spans the characters \ < > [ ] & and a backtick of an unmatched run are backslash-escaped (CommonMark renders an
# escaped punctuation character as itself); code spans, emphasis and underscores are kept, because subjects use them.
# The GitLab Release description never holds a subject: it is the release document, whole (render_release_description).
MARKDOWN_ESCAPES = str.maketrans({char: "\\" + char for char in "\\<>[]&`"})
BACKTICK_RUN_RE = re.compile(r"`+")
LEADING_BLOCK_RE = re.compile(r"(?:#{1,6}|[-+*]|\d{1,9}(?P<num>[.)]))(?=[ \t]|$)|(?P<rule>[-*_])(?:[ \t]*(?P=rule)){2,}[ \t]*$|~{3}")


def code_span_parts(text: str) -> list[tuple[bool, str]]:
    """``text`` as (is_code_span, part) pairs, matched as CommonMark matches them: a backtick run opens a code span that
    the next run of the SAME length closes; a run with no closer is literal text."""
    runs = list(BACKTICK_RUN_RE.finditer(text))
    parts: list[tuple[bool, str]] = []
    start, i = 0, 0
    while i < len(runs):
        opener = runs[i]
        closer = next((j for j in range(i + 1, len(runs)) if len(runs[j].group()) == len(opener.group())), None)
        if closer is None:
            i += 1
            continue
        parts += [(False, text[start:opener.start()]), (True, text[opener.start():runs[closer].end()])]
        start, i = runs[closer].end(), closer + 1
    return parts + [(False, text[start:])]


def markdown_entry(text: str) -> str:
    """One changelog entry with every Markdown structure outside code spans escaped (see MARKDOWN_ESCAPES)."""
    out = "".join(part if is_code else part.translate(MARKDOWN_ESCAPES) for is_code, part in code_span_parts(text))
    lead = LEADING_BLOCK_RE.match(out)
    if lead:
        cut = lead.start("num") if lead.group("num") else 0
        out = out[:cut] + "\\" + out[cut:]
    return out


def render_changelog_section(previous_tag: str | None, grouped: dict[str, list[str]]) -> str:
    lines: list[str] = ["## Changelog"]
    if previous_tag:
        lines.append(f"_Commits since {previous_tag}._")
    else:
        lines.append("_Initial release._")
    lines.append("")

    wrote = False
    for section, entries in grouped.items():
        if not entries:
            continue
        wrote = True
        lines.append(f"### {section}")
        lines.extend(f"- {markdown_entry(entry)}" for entry in entries)
        lines.append("")

    if not wrote:
        lines.extend(["- No additional commit changes recorded.", ""])
    return "\n".join(lines).strip() + "\n"


def render_release_description(brief: str) -> str:
    """The GitLab Release description is the release document, whole (no title strip, no appended list)."""
    return brief


def update_changelog(tag: str, changelog_section: str) -> str:
    """Insert the generated commit list under ``## [tag] - date``; H1/H2 lines are dropped, ``###`` groups kept."""
    today = dt.date.today().isoformat()
    heading = f"## [{tag}] - {today}"
    changelog_path = ROOT / "CHANGELOG.md"

    try:
        existing = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else ""
    except (OSError, UnicodeDecodeError) as exc:
        raise ReleasePublishError("CHANGELOG.md is not readable UTF-8 text") from exc
    if heading in existing:
        return existing

    section_lines = [heading, ""]
    for line in changelog_section.splitlines():
        if line.startswith("# ") or line.startswith("## "):
            continue
        section_lines.append(line)
    section = "\n".join(section_lines).strip() + "\n\n"

    if not existing.strip():
        return "# Changelog\n\n" + section

    if existing.startswith("# Changelog"):
        # K-12: the entry goes below the introductory paragraph(s), above the newest
        # existing entry; with no entry yet, at the end. T716 (D-T710-2): ``## [Unreleased]``
        # is not an entry and stays on top, as Keep a Changelog orders it.
        first_entry = RELEASED_HEADING_RE.search(existing)
        head = existing[: first_entry.start()] if first_entry else existing
        tail = existing[first_entry.start():] if first_entry else ""
        return head.rstrip("\n") + "\n\n" + section + tail
    return "# Changelog\n\n" + section + existing


def write_artifacts(changelog: str) -> None:
    """Write CHANGELOG.md, the only file this script produces."""
    (ROOT / "CHANGELOG.md").write_text(changelog, encoding="utf-8")


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect: urllib would re-send the token header to the new location."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None  # the caller then sees the 3xx as an HTTPError


OPENER = urllib.request.build_opener(_RefuseRedirects)


def validate_token_header(name: str) -> str:
    """Fail closed unless ``name`` is exactly one of ``TOKEN_HEADERS`` (case-sensitive; the value is never echoed)."""
    if name not in TOKEN_HEADERS:
        raise ReleasePublishError(f"invalid --token-header: must be one of {', '.join(TOKEN_HEADERS)}")
    return name


class ApiCredential(NamedTuple):
    """The API token and the one header that carries it (T716, TL-T708-06); the repr never shows the token."""

    token: str
    header: str = DEFAULT_TOKEN_HEADER

    def __repr__(self) -> str:
        return f"ApiCredential(header={self.header!r})"


class ApiTarget(NamedTuple):
    """Where a release goes: the API base, the project id, the credential and the host pin (T716, TL-T708-06)."""

    api_v4_url: str
    project_id: str
    credential: ApiCredential
    expected_host: str | None = None


def gitlab_request(method: str, url: str, credential: ApiCredential, payload: dict | None = None) -> dict:
    validate_token_header(credential.header)
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url=url, method=method, data=data)
    request.add_header(credential.header, credential.token)
    request.add_header("Content-Type", "application/json")

    try:
        with OPENER.open(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:  # includes a refused redirect (3xx)
        message = _error_body(exc)
        raise ReleasePublishError(f"GitLab API {method} {url} failed: {exc.code} {message}", exc.code) from exc
    except urllib.error.URLError as exc:
        raise ReleasePublishError(f"GitLab API {method} {url} failed: {exc.reason}") from exc
    except (OSError, http.client.HTTPException, ValueError) as exc:
        # A socket timeout or reset during read(), a short read, a body that is not UTF-8 or JSON.
        raise ReleasePublishError(f"GitLab API {method} {url} failed: {type(exc).__name__}") from exc


def _error_body(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="ignore")
    except (OSError, http.client.HTTPException):
        return ""


def create_or_update_release(tag: str, target: ApiTarget, description: str) -> None:
    validate_token_header(target.credential.header)
    validate_api_target(target.api_v4_url, target.project_id, target.expected_host)
    endpoint = f"{target.api_v4_url}/projects/{target.project_id}/releases/{tag}"
    payload = {
        "name": tag,
        "tag_name": tag,
        "description": description,
        "ref": tag,
    }

    exists = False
    try:
        current = gitlab_request("GET", endpoint, target.credential)
        exists = current.get("tag_name") == tag
    except ReleasePublishError as exc:
        if exc.status != 404:
            raise

    if exists:
        response = gitlab_request("PUT", endpoint, target.credential, payload)
    else:
        collection = f"{target.api_v4_url}/projects/{target.project_id}/releases"
        response = gitlab_request("POST", collection, target.credential, payload)

    if response.get("tag_name") != tag:
        raise ReleasePublishError(f"GitLab release publish failed: unexpected response {response}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--api-v4-url", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--token-env", help="name of the environment variable that holds the API token")
    parser.add_argument(
        "--token-header",
        choices=TOKEN_HEADERS,
        default=DEFAULT_TOKEN_HEADER,
        help="the HTTP header that carries the token: PRIVATE-TOKEN (default; access tokens) or JOB-TOKEN (CI_JOB_TOKEN)",
    )
    parser.add_argument("--token", help="DEPRECATED: the token in argv is visible to every process; use --token-env")
    parser.add_argument(
        "--expected-host",
        default=None,
        help="pin the host of --api-v4-url (default: $CI_SERVER_HOST when set; required in CI)",
    )
    parser.add_argument("--skip-api", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_tag(args.tag)
    validate_token_header(args.token_header)
    expected_host = resolve_expected_host(args.expected_host)
    validate_api_target(args.api_v4_url, args.project_id, expected_host)
    token = None if args.skip_api else resolve_token(args.token, args.token_env)
    if args.token_env:
        WITHHELD_ENV_NAMES.add(args.token_env)
    if token and not args.token_env:
        WITHHELD_ENV_VALUES.add(token)  # the deprecated --token: no variable name to withhold, so withhold the value
    run_git(["fetch", "--tags", "--force"])
    ensure_full_history()

    tags = get_tag_list()
    previous_tag = resolve_previous_tag(args.tag, tags)
    brief = load_release_brief(args.tag)
    subjects = get_commit_subjects(args.tag, previous_tag)
    grouped = classify_subjects(subjects)

    description = render_release_description(brief)
    changelog = update_changelog(args.tag, render_changelog_section(previous_tag, grouped))
    write_artifacts(changelog)

    if not args.skip_api:
        target = ApiTarget(args.api_v4_url, args.project_id, ApiCredential(token, args.token_header), expected_host)
        create_or_update_release(args.tag, target, description)

    print(f"release-publish: regenerated CHANGELOG.md for {args.tag}")
    if args.skip_api:
        print("release-publish: skipped GitLab API publish by request")
    else:
        print(f"release-publish: published GitLab release for {args.tag}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ReleasePublishError as exc:
        print(f"release-publish: {exc}")
        sys.exit(1)