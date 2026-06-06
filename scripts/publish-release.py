#!/usr/bin/env python3
"""Generate release artifacts and publish a GitLab release fail-closed."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
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
SIMPLE_RELEASE_BRANCH_RE = re.compile(r"^release/v\d+\.\d+\.\d+$")


class ReleasePublishError(RuntimeError):
    """Raised when release artifact generation or publishing fails."""


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
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
    return [line for line in output.splitlines() if line]


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
        base = run_git(["merge-base", previous_tag, current_tag])
        count = run_git(["rev-list", "--count", f"{base}..{current_tag}"])
        direct = run_git(["rev-list", "--count", f"{previous_tag}..{current_tag}"])
        if int(count) >= int(direct):
            return f"{base}..{current_tag}"
    except ReleasePublishError:
        pass
    return f"{previous_tag}..{current_tag}"


def get_commit_subjects(current_tag: str, previous_tag: str | None) -> list[str]:
    revision = _revision_range(current_tag, previous_tag)
    output = run_git(["log", revision, "--pretty=%s"])
    subjects = [line.strip() for line in output.splitlines() if line.strip()]
    if not subjects:
        raise ReleasePublishError(f"no commits found for revision range '{revision}'")
    return subjects


def load_release_brief(tag: str) -> str:
    brief_path = ROOT / "docs" / "releases" / f"{tag}.md"
    if not brief_path.is_file():
        raise ReleasePublishError(
            f"missing release brief: docs/releases/{tag}.md "
            "(copy docs/releases/_template.md and fill Install + Highlights)"
        )
    return brief_path.read_text(encoding="utf-8").strip() + "\n"


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


def render_release_notes(
    tag: str,
    previous_tag: str | None,
    grouped: dict[str, list[str]],
    brief: str,
) -> str:
    brief_body = brief
    if brief_body.startswith(f"# Release {tag}"):
        brief_body = "\n".join(brief_body.splitlines()[1:]).lstrip("\n")

    changelog = render_changelog_section(previous_tag, grouped)
    return f"# Release {tag}\n\n{brief_body}\n\n---\n\n{changelog}\n"


def update_changelog(tag: str, notes_body: str) -> str:
    today = dt.date.today().isoformat()
    heading = f"## [{tag}] - {today}"
    changelog_path = ROOT / "CHANGELOG.md"

    existing = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else ""
    if heading in existing:
        return existing

    section_lines = [heading, ""]
    for line in notes_body.splitlines():
        if line.startswith("#"):
            continue
        section_lines.append(line)
    section = "\n".join(section_lines).strip() + "\n\n"

    if not existing.strip():
        return "# Changelog\n\n" + section

    if existing.startswith("# Changelog"):
        parts = existing.split("\n", 2)
        prefix = "\n".join(parts[:2]).rstrip() + "\n\n"
        remainder = parts[2] if len(parts) > 2 else ""
        return prefix + section + remainder.lstrip("\n")
    return "# Changelog\n\n" + section + existing


def write_artifacts(release_notes: str, changelog: str) -> None:
    (ROOT / "release-notes.md").write_text(release_notes, encoding="utf-8")
    (ROOT / "CHANGELOG.md").write_text(changelog, encoding="utf-8")

    notes_size = (ROOT / "release-notes.md").stat().st_size
    if notes_size == 0:
        raise ReleasePublishError("release-notes.md is empty")


def gitlab_request(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url=url, method=method, data=data)
    request.add_header("PRIVATE-TOKEN", token)
    request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="ignore")
        raise ReleasePublishError(f"GitLab API {method} {url} failed: {exc.code} {message}") from exc
    except urllib.error.URLError as exc:
        raise ReleasePublishError(f"GitLab API {method} {url} failed: {exc.reason}") from exc


def create_or_update_release(tag: str, api_v4_url: str, project_id: str, token: str, description: str) -> None:
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
        if " 404 " not in str(exc):
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
    parser.add_argument("--token", required=True)
    parser.add_argument("--skip-api", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_git(["fetch", "--tags", "--force"])
    ensure_full_history()

    tags = get_tag_list()
    previous_tag = resolve_previous_tag(args.tag, tags)
    brief = load_release_brief(args.tag)
    subjects = get_commit_subjects(args.tag, previous_tag)
    grouped = classify_subjects(subjects)

    release_notes = render_release_notes(args.tag, previous_tag, grouped, brief)
    changelog = update_changelog(args.tag, release_notes)
    write_artifacts(release_notes, changelog)

    if not args.skip_api:
        create_or_update_release(
            tag=args.tag,
            api_v4_url=args.api_v4_url,
            project_id=args.project_id,
            token=args.token,
            description=release_notes,
        )

    print(f"release-publish: generated artifacts for {args.tag}")
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