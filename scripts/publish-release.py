#!/usr/bin/env python3
"""Regenerate CHANGELOG.md and publish a GitLab release fail-closed.

The release has ONE release document, ``docs/releases/<tag>.md`` (it starts
``# Release <tag>``). The GitLab Release description is that document, whole and
unchanged (T640 / ruling C3). The commit list generated from Conventional
Commits (merge commits excluded, filter F1) goes into ``CHANGELOG.md`` only,
which is the only file this script writes; no root ``release-notes.md`` is
written. Offline rehearsal: ``scripts/dry-run-publish-release.py``.

The API token is read from an environment variable named by ``--token-env``
(CI: ``--token-env WIKI_TOKEN``), so the value never appears in argv, in the
process list or in a job log. ``--token`` is still accepted but deprecated: it
prints a warning (never the value) because argv is world-readable on a runner.
The API target is parsed, not prefix-matched (``validate_api_target``), the
host can be pinned (``--expected-host``, default ``CI_SERVER_HOST``), and the
HTTP opener refuses every redirect, so the ``PRIVATE-TOKEN`` header is never
re-sent to a second location (T675).
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
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


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
# The only API base shape: .../api/v4. A segment is never "." or "..".
API_PATH_RE = re.compile(r"(/(?!\.{1,2}(?:/|$))[A-Za-z0-9._~-]+)*/api/v4")
ENV_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")
HTTP_TIMEOUT_SECONDS = 30
WITHHELD_ENV_NAMES = {"WIKI_TOKEN"}  # never passed to git: main() adds the --token-env name


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


def child_environment() -> dict[str, str]:
    """A copy of the environment without the API token variable (git has no use for it)."""
    return {k: v for k, v in os.environ.items() if k not in WITHHELD_ENV_NAMES}


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=child_environment(),
    )
    if result.returncode != 0:
        raise ReleasePublishError(
            f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def ensure_full_history() -> None:
    """Unshallow CI clones so release notes include the full commit range."""
    is_shallow = run_git(["rev-parse", "--is-shallow-repository"]).strip()
    if is_shallow == "true":
        run_git(["fetch", "--unshallow", "--tags", "origin"])


def get_tag_list() -> list[str]:
    output = run_git(["tag", "--sort=-v:refname"])
    # Only release tags: a stray tag name must never become ``previous_tag`` (and so
    # reach git arguments and CHANGELOG.md).
    return [line for line in output.splitlines() if TAG_RE.fullmatch(line)]


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


def get_commit_subjects(current_tag: str, previous_tag: str | None) -> list[str]:
    revision = _revision_range(current_tag, previous_tag)
    # Filter F1: merge commits are excluded structurally, not by subject text.
    output = run_git(["log", "--no-merges", "--pretty=%s", "--end-of-options", revision, "--"])
    subjects = [CONTROL_CHARS_RE.sub("", line).strip() for line in output.splitlines()]
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
        lines.extend(f"- {entry}" for entry in entries)
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
        # existing entry (the first ``## `` heading); with no entry yet, after the intro.
        first_entry = re.search(r"^## ", existing, re.M)
        head = existing[: first_entry.start()] if first_entry else existing
        tail = existing[first_entry.start():] if first_entry else ""
        return head.rstrip("\n") + "\n\n" + section + tail
    return "# Changelog\n\n" + section + existing


def write_artifacts(changelog: str) -> None:
    """Write CHANGELOG.md, the only file this script produces."""
    (ROOT / "CHANGELOG.md").write_text(changelog, encoding="utf-8")


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect: urllib would re-send ``PRIVATE-TOKEN`` to the new location."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None  # the caller then sees the 3xx as an HTTPError


OPENER = urllib.request.build_opener(_RefuseRedirects)


def gitlab_request(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url=url, method=method, data=data)
    request.add_header("PRIVATE-TOKEN", token)
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


def create_or_update_release(
    tag: str, api_v4_url: str, project_id: str, token: str, description: str,
    expected_host: str | None = None,
) -> None:
    validate_api_target(api_v4_url, project_id, expected_host)
    endpoint = f"{api_v4_url}/projects/{project_id}/releases/{tag}"
    payload = {
        "name": tag,
        "tag_name": tag,
        "description": description,
        "ref": tag,
    }

    exists = False
    try:
        current = gitlab_request("GET", endpoint, token)
        exists = current.get("tag_name") == tag
    except ReleasePublishError as exc:
        if exc.status != 404:
            raise

    if exists:
        response = gitlab_request("PUT", endpoint, token, payload)
    else:
        response = gitlab_request(
            "POST", f"{api_v4_url}/projects/{project_id}/releases", token, payload
        )

    if response.get("tag_name") != tag:
        raise ReleasePublishError(f"GitLab release publish failed: unexpected response {response}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--api-v4-url", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--token-env", help="name of the environment variable that holds the API token")
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
    expected_host = resolve_expected_host(args.expected_host)
    validate_api_target(args.api_v4_url, args.project_id, expected_host)
    token = None if args.skip_api else resolve_token(args.token, args.token_env)
    if args.token_env:
        WITHHELD_ENV_NAMES.add(args.token_env)
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
        create_or_update_release(
            tag=args.tag,
            api_v4_url=args.api_v4_url,
            project_id=args.project_id,
            token=token,
            description=description,
            expected_host=expected_host,
        )

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