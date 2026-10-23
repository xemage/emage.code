#!/usr/bin/env python3
"""Offline rehearsal of scripts/publish-release.py main() (T619).

Needs no network, no tag, no push and no credential. It copies the release
document ``docs/releases/<tag>.md`` (and ``CHANGELOG.md`` when present) into a
temporary directory, points the module's ``ROOT`` there, replaces ``run_git``
and ``gitlab_request`` with in-process fakes, makes ``urllib`` refuse to open
any URL, and runs the real ``main()`` without ``--skip-api``. It then reports
what a tag run would write and what it would send as the Release description.
The repository tree is never written.

The run fails unless the description equals the release document byte-for-byte
(T640 / C3) and the CHANGELOG.md section lists no merge commit (filter F1: the
fake ``git log`` returns merge subjects unless it is given ``--no-merges``).

``--template-shaped`` rehearses a document built from ``docs/releases/_template.md``
(title ``# Release v1.2.3``) and additionally fails unless the description has
exactly one top-level title line.

The token travels as the CI job passes it: through an environment variable named by
``--token-env`` (set for the run only, restored afterwards), never in argv.

Usage: python3 scripts/dry-run-publish-release.py [--tag vX.Y.Z | --template-shaped]
``--tag`` defaults to the ``Latest release: vX.Y.Z`` marker of README.md; the run is
refused when there is neither.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import os
import re
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, NamedTuple

REPO = Path(__file__).resolve().parent.parent
TEMPLATE_TAG = "v1.2.3"
PLACEHOLDER_TOKEN = "DRY-RUN-PLACEHOLDER"  # not a credential; never sent anywhere
TOKEN_ENV = "DRY_RUN_RELEASE_TOKEN"  # the variable the rehearsal reads the placeholder from
MARKER_RE = re.compile(r"^Latest release:\s*(v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?)\s*$", re.M)
MERGE_SUBJECTS = [  # what GitLab writes for a merge; dropped only by ``git log --no-merges``
    "Merge branch 'feature/42-sample' into 'develop'",
    "Merge branch 'bugfix/43-sample' into 'develop'",
]
SAMPLE_SUBJECTS = [
    "feat(release): single release document",
    "fix(ci): drop the root release-notes artifact",
    "docs: update release runbook",
]


def load_publish_release(repo: Path = REPO) -> Any:
    path = repo / "scripts" / "publish-release.py"
    spec = importlib.util.spec_from_file_location("publish_release", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load publish-release module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fake_run_git(tag: str, previous_tag: str):
    def run_git(args: list[str]) -> str:
        if args[:1] == ["tag"]:
            return f"{tag}\n{previous_tag}"
        if args[:1] == ["rev-parse"]:
            return "false"
        if args[:1] == ["merge-base"]:
            return "0" * 40
        if args[:1] == ["rev-list"]:
            return str(len(SAMPLE_SUBJECTS))
        if args[:1] == ["log"]:
            merges = [] if "--no-merges" in args else MERGE_SUBJECTS
            return "\x00".join(merges + SAMPLE_SUBJECTS) + "\x00"  # the real log is NUL-framed (SEC-T676-05)
        return ""  # fetch and anything else: no-op

    return run_git


def _refuse_network(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("dry run attempted network access")


class _RefusingOpener:
    """Stands in for the module's redirect-refusing OPENER: any ``open`` is a failed rehearsal."""

    def open(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("dry run attempted network access (OPENER)")


def resolve_release_source(module: Any, tag: str, source_dir: Path) -> Path:
    """Validate ``tag`` against the CI tag rule and keep the source under ``source_dir``."""
    module.validate_tag(tag)
    base = source_dir.resolve()
    source = (base / f"{tag}.md").resolve()
    if not source.is_relative_to(base):
        raise module.ReleasePublishError(f"release document escapes {base}: {source}")
    if not source.is_file():
        raise module.ReleasePublishError(f"missing release document: {source}")
    return source


class DryRunSource(NamedTuple):
    """Where a dry run reads from (immutable; a NamedTuple loads without sys.modules registration).

    ``source_dir`` defaults to ``<repo>/docs/releases``; ``copy_changelog`` copies
    the repo CHANGELOG.md into the work directory first (False for fixture runs).
    """

    repo: Path = REPO
    source_dir: Path | None = None
    copy_changelog: bool = True


def top_level_titles(description: str) -> list[str]:
    """Return the ``# `` title lines of ``description``, ignoring fenced code blocks."""
    titles: list[str] = []
    in_fence = False
    for line in description.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and re.match(r"# \S", line):
            titles.append(line)
    return titles


def write_template_shaped_document(repo: Path, source_dir: Path, tag: str = TEMPLATE_TAG) -> Path:
    """Write ``<tag>.md`` into ``source_dir`` from the release template (vX.Y.Z -> tag)."""
    load_publish_release(repo).validate_tag(tag)  # the tag becomes a file name: same rule as the CI tag
    template = (repo / "docs" / "releases" / "_template.md").read_text(encoding="utf-8")
    source_dir.mkdir(parents=True, exist_ok=True)
    document = source_dir / f"{tag}.md"
    document.write_text(template.replace("vX.Y.Z", tag), encoding="utf-8")
    return document


def run_dry_run(tag: str, work: Path, source: DryRunSource | None = None) -> dict[str, Any]:
    """Run publish-release main() inside ``work``; return what it produced."""
    source = source or DryRunSource()
    repo = source.repo
    module = load_publish_release(repo)
    document = resolve_release_source(module, tag, source.source_dir or repo / "docs" / "releases")
    target = work / "docs" / "releases"
    target.mkdir(parents=True)
    shutil.copyfile(document, target / f"{tag}.md")
    if source.copy_changelog and (repo / "CHANGELOG.md").is_file():
        shutil.copyfile(repo / "CHANGELOG.md", work / "CHANGELOG.md")

    sent: list[dict[str, Any]] = []

    def fake_gitlab_request(method, url, token, payload=None, token_header="PRIVATE-TOKEN"):
        sent.append({"method": method, "url": url, "payload": payload, "token_header": token_header})
        if method == "GET":
            raise module.ReleasePublishError(f"GitLab API GET {url} failed: 404 fake", 404)
        return {"tag_name": tag}

    module.ROOT = work
    module.run_git = _fake_run_git(tag, "v0.0.0")
    module.gitlab_request = fake_gitlab_request
    module.OPENER = _RefusingOpener()
    original_urlopen = urllib.request.urlopen
    urllib.request.urlopen = _refuse_network
    argv = sys.argv
    sys.argv = [
        "publish-release.py", "--tag", tag,
        "--api-v4-url", "https://gitlab.invalid/api/v4", "--expected-host", "gitlab.invalid",
        "--project-id", "0", "--token-env", TOKEN_ENV,
        "--token-header", "JOB-TOKEN",  # as the CI release job (T686)
    ]
    previous_token = os.environ.get(TOKEN_ENV)
    out = io.StringIO()
    cwd = None
    try:  # everything that changes process state is inside the try: the finally undoes it
        os.environ[TOKEN_ENV] = PLACEHOLDER_TOKEN
        cwd = os.getcwd()
        os.chdir(work)  # a stray relative-path write lands in the temp root, not the caller's cwd
        with contextlib.redirect_stdout(out):
            code = module.main()
    finally:
        if cwd is not None:
            os.chdir(cwd)
        sys.argv = argv
        urllib.request.urlopen = original_urlopen
        if previous_token is None:
            os.environ.pop(TOKEN_ENV, None)
        else:
            os.environ[TOKEN_ENV] = previous_token
    files = sorted(p.relative_to(work).as_posix() for p in work.rglob("*") if p.is_file())
    changelog = work / "CHANGELOG.md"
    return {
        "exit": code, "stdout": out.getvalue(), "files": files, "sent": sent, "work": work,
        "document": document.read_bytes().decode("utf-8"),
        "changelog": changelog.read_text(encoding="utf-8") if changelog.is_file() else "",
    }


def _report_calls(sent: list[dict[str, Any]]) -> None:
    for call in sent:
        desc = (call["payload"] or {}).get("description")
        print(f"fake GitLab call: {call['method']} {call['url']}")
        if desc is None:
            continue
        print(f"  description: {len(desc)} chars, {len(desc.splitlines())} lines")
        print("  first lines:\n    " + "\n    ".join(desc.splitlines()[:3]))
        print(f"  top-level title lines: {top_level_titles(desc)}")


def _description(result: dict[str, Any]) -> str:
    posts = [c for c in result["sent"] if c["method"] == "POST"]
    return posts[0]["payload"]["description"] if posts else ""


def changelog_entry(changelog: str, tag: str) -> str:
    """Return the ``## [<tag>] - date`` section of ``changelog`` (up to the next ``## `` heading)."""
    lines = changelog.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(f"## [{tag}] - ")), None)
    if start is None:
        return ""
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start:end]).strip()


def check_result(result: dict[str, Any], tag: str) -> list[str]:
    """Return the T640 problems of a dry-run ``result`` (empty list when all hold)."""
    problems: list[str] = []
    if result["exit"] != 0:
        problems.append(f"exit code {result['exit']}")
    if "release-notes.md" in result["files"]:
        problems.append("root release-notes.md written")
    if _description(result) != result["document"]:
        problems.append("description differs from the release document")
    entry = changelog_entry(result["changelog"], tag)
    if not entry:
        problems.append("CHANGELOG.md has no section for the tag")
    if "erge branch" in entry or re.search(r"^- merge ", entry, re.M):
        problems.append("CHANGELOG.md section lists a merge commit")
    for sample in SAMPLE_SUBJECTS:
        if sample.split(": ", 1)[1] not in entry:
            problems.append(f"CHANGELOG.md section misses commit {sample!r}")
    return problems


def current_release_tag(repo: Path = REPO) -> str | None:
    """The ``Latest release: vX.Y.Z`` marker of README.md, or None when it is absent."""
    readme = repo / "README.md"
    if not readme.is_file():
        return None
    match = MARKER_RE.search(readme.read_text(encoding="utf-8", errors="ignore"))
    return match.group(1) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", default=None, help="release tag (default: the README.md 'Latest release' marker)")
    parser.add_argument("--template-shaped", action="store_true",
                        help=f"rehearse a template-shaped document ({TEMPLATE_TAG}); needs exactly one title line")
    args = parser.parse_args()
    tag = TEMPLATE_TAG if args.template_shaped else (args.tag or current_release_tag())
    if tag is None:
        print("dry run refused: no --tag and no 'Latest release: vX.Y.Z' marker in README.md")
        return 2
    try:
        load_publish_release().validate_tag(tag)
    except Exception as exc:  # ReleasePublishError from the loaded module
        print(f"dry run refused: {exc}")
        return 2
    with tempfile.TemporaryDirectory(prefix="dry-run-publish-release-") as tmp:
        source = None
        if args.template_shaped:
            fixtures = Path(tmp) / "fixture-releases"
            write_template_shaped_document(REPO, fixtures)
            source = DryRunSource(source_dir=fixtures, copy_changelog=False)
        result = run_dry_run(tag, Path(tmp) / "work", source)
        work: Path = result["work"]
        print(f"exit code: {result['exit']}")
        print("script output:\n  " + result["stdout"].strip().replace("\n", "\n  "))
        print("files in the temp root after the run:")
        for name in result["files"]:
            print(f"  {name}")
        print(f"root release-notes.md written: {'release-notes.md' in result['files']}")
        _report_calls(result["sent"])
        print(f"description equals the release document byte-for-byte: {_description(result) == result['document']}")
        print(f"CHANGELOG.md section for {tag}:\n  " + changelog_entry(result["changelog"], tag).replace("\n", "\n  "))
        problems = check_result(result, tag)
        if args.template_shaped and len(top_level_titles(_description(result))) != 1:
            problems.append("description does not have exactly one top-level title line")
        for problem in problems:
            print(f"problem: {problem}")
        print("DRY RUN " + ("FAILED" if problems else "OK"))
        return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
