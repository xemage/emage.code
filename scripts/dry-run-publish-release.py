#!/usr/bin/env python3
"""Offline rehearsal of scripts/publish-release.py main() (T619).

Needs no network, no tag, no push and no credential. It copies the release
document ``docs/releases/<tag>.md`` (and ``CHANGELOG.md`` when present) into a
temporary directory, points the module's ``ROOT`` there, replaces ``run_git``
and ``gitlab_request`` with in-process fakes, makes ``urllib`` refuse to open
any URL, and runs the real ``main()`` without ``--skip-api``. It then reports
what a tag run would write and what it would send as the Release description.
The repository tree is never written.

``--template-shaped`` rehearses a document built from ``docs/releases/_template.md``
(title ``# Release v1.2.3``) and fails unless the description has exactly one
top-level title line (T635 / C1).

Usage: python3 scripts/dry-run-publish-release.py [--tag v7.0.1 | --template-shaped]
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
CHANGELOG_SEPARATOR = "\n\n---\n\n"  # as joined by render_release_description
PLACEHOLDER_TOKEN = "DRY-RUN-PLACEHOLDER"  # not a credential; never sent anywhere
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
            return "\n".join(SAMPLE_SUBJECTS)
        return ""  # fetch and anything else: no-op

    return run_git


def _refuse_network(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("dry run attempted network access")


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

    def fake_gitlab_request(method, url, token, payload=None):
        sent.append({"method": method, "url": url, "payload": payload})
        if method == "GET":
            raise module.ReleasePublishError(f"GitLab API GET {url} failed: 404 fake")
        return {"tag_name": tag}

    module.ROOT = work
    module.run_git = _fake_run_git(tag, "v0.0.0")
    module.gitlab_request = fake_gitlab_request
    original_urlopen = urllib.request.urlopen
    urllib.request.urlopen = _refuse_network
    argv = sys.argv
    sys.argv = [
        "publish-release.py", "--tag", tag,
        "--api-v4-url", "https://gitlab.invalid/api/v4",
        "--project-id", "0", "--token", PLACEHOLDER_TOKEN,
    ]
    out = io.StringIO()
    cwd = os.getcwd()
    os.chdir(work)  # a stray relative-path write lands in the temp root, not the caller's cwd
    try:
        with contextlib.redirect_stdout(out):
            code = module.main()
    finally:
        os.chdir(cwd)
        sys.argv = argv
        urllib.request.urlopen = original_urlopen
    files = sorted(p.relative_to(work).as_posix() for p in work.rglob("*") if p.is_file())
    return {"exit": code, "stdout": out.getvalue(), "files": files, "sent": sent, "work": work}


def _report_calls(sent: list[dict[str, Any]]) -> None:
    for call in sent:
        desc = (call["payload"] or {}).get("description")
        print(f"fake GitLab call: {call['method']} {call['url']}")
        if desc is None:
            continue
        print(f"  description: {len(desc)} chars, {len(desc.splitlines())} lines")
        print("  first lines:\n    " + "\n    ".join(desc.splitlines()[:3]))
        print(f"  top-level title lines: {top_level_titles(desc)}")
        changelog = desc.split(CHANGELOG_SEPARATOR)[-1].strip().splitlines()
        print("  changelog section:\n    " + "\n    ".join(changelog))


def _description(result: dict[str, Any]) -> str:
    posts = [c for c in result["sent"] if c["method"] == "POST"]
    return posts[0]["payload"]["description"] if posts else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", default="v7.0.1")
    parser.add_argument("--template-shaped", action="store_true",
                        help=f"rehearse a template-shaped document ({TEMPLATE_TAG}); needs exactly one title line")
    args = parser.parse_args()
    tag = TEMPLATE_TAG if args.template_shaped else args.tag
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
        print("CHANGELOG.md head:\n  " + "\n  ".join((work / "CHANGELOG.md").read_text().splitlines()[:4]))
        ok = result["exit"] == 0 and "release-notes.md" not in result["files"]
        if args.template_shaped:
            ok = ok and len(top_level_titles(_description(result))) == 1
        print("DRY RUN " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
