#!/usr/bin/env python3
"""Audit the pinned MCP server packages of servers.yaml (T676: SEC-T646-03, -05, -06, K-17, T638-L-2).

The `npx` entries of ``implementation/knowledge/mcp/servers.yaml`` are not part of any npm project, so
``npm audit`` cannot see them (SEC-T646-05). This script reads the exact pins from servers.yaml and
builds a THROWAWAY ``package.json`` from them, so the usual tools work on the real pins:

  list                          print every pin (kind, server, package, version)
  generate DIR                  write DIR/package.json (npm pins) and DIR/requirements-uvx.txt (PyPI pins)
  audit [--audit-level L]       generate in a temporary directory, resolve with
        [--signatures]          ``npm install --package-lock-only --ignore-scripts`` and run ``npm audit``;
                                with --signatures also ``npm install --ignore-scripts`` and
                                ``npm audit signatures`` (registry signatures and provenance of the
                                whole tree). Exit 1 when a finding reaches the audit level.
        [--accept GHSA-x:DATE]  a reviewed, EXPIRING acceptance of one advisory (repeatable; the date is
                                mandatory, YYYY-MM-DD, last day it counts). An accepted advisory is still
                                printed, marked ACCEPTED, and does not count as a finding; an expired
                                acceptance fails the run. Acceptances are recorded in an artifact
                                (docs/artifacts/brave-audit-acceptance-v1.md) and listed in the checklist.
  provenance                    ask the npm registry whether the pinned version, and the ``latest``
        [--require]             version, carry a provenance attestation (SEC-T646-03). --require: exit 1
                                when a pinned version has none.

Always printed by ``audit``: a MANUAL ADVISORY READ notice for the three reference servers whose version
scheme moved from calendar versions (2025.x, 2026.x) to ``1.0.0`` (SEC-T646-06). Advisory ranges written
in calendar form sort ABOVE ``1.0.0`` in semver, so ``npm audit`` can both over- and under-report them:
read the advisories of those packages by hand at every pin bump (docs/wiki/mcp-pin-bump-checklist.md).

Safety properties (each has a test with a mutation proof in tests/functional/test_audit_mcp_pins.py):
  - a pin must be an exact ``name@MAJOR.MINOR.PATCH[-pre]``; a tag, a range or a missing version stops the
    script (the same rule as tests/functional/test_mcp_package_pins.py);
  - ``--ignore-scripts`` is always passed to npm, so no install script of an audited package runs;
  - npm runs with a fixed argv (no shell), an environment without anything that looks like a secret, an
    empty user and global configuration file and ``--registry https://registry.npmjs.org/``, so a
    ``.npmrc`` of the maintainer (registry, auth token) can neither redirect nor receive the traffic;
  - the audit fails closed: a reply without both ``vulnerabilities`` and ``metadata`` is an error and an
    unknown severity counts as critical;
  - the registry is reached over https at registry.npmjs.org only, never through a redirect, with a
    timeout and a size limit; text taken from a reply is stripped of control characters before printing;
  - a version that is not an exact pin is never written to the manifest.

Standard library plus PyYAML (already required by the repository tests). The script only reads
servers.yaml and talks to the npm registry; it changes nothing in the repository.
Exit codes: 0 ok, 1 findings, 2 error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

REPO = Path(__file__).resolve().parent.parent
SERVERS_YAML = REPO / "implementation" / "knowledge" / "mcp" / "servers.yaml"
REGISTRY = "https://registry.npmjs.org"
REGISTRY_HOST = "registry.npmjs.org"
MAX_REPLY_BYTES = 8 * 1024 * 1024
LEVELS = ("info", "low", "moderate", "high", "critical")
# SEC-T646-06: moved from calendar versions to 1.0.0 (and 2.0.0 on 2026-10-19); read their advisories by hand.
CALENDAR_VERSION_PACKAGES = (
    "@modelcontextprotocol/server-memory",
    "@modelcontextprotocol/server-sequential-thinking",
    "@modelcontextprotocol/server-filesystem",
)
NPM_PIN = re.compile(r"^(?P<name>(?:@[a-z0-9][a-z0-9._~-]*/)?[a-z0-9][a-z0-9._~-]*)"
                     r"@(?P<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)$")
PYPI_PIN = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)@(?P<version>[0-9][0-9A-Za-z.!+_-]*)$")
GHSA_RE = re.compile(r"GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}")
UNSAFE_TEXT_RE = re.compile("[\x00-\x1f\x7f-\x9f\u061c\u200b-\u200f\u2028\u2029\u202a-\u202e\u2060-\u2069\ufeff]")
SECRET_NAME = re.compile(r"(TOKEN|KEY|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH|COOKIE)", re.I)


class AuditError(Exception):
    """A usage or environment error (exit code 2); never carries a secret."""


def safe_text(value: object) -> str:
    """Text from a registry or npm reply, as one printable line: control and bidirectional characters removed."""
    return UNSAFE_TEXT_RE.sub("", str(value))


@dataclass(frozen=True)
class Pin:
    kind: str  # "npm" | "pypi" | "docker"
    server: str
    name: str
    version: str


def first_package_arg(args: list) -> str:
    """The first argument that is not a flag: the package spec of an `npx` or `uvx` entry."""
    for arg in args:
        if isinstance(arg, str) and not arg.startswith("-"):
            return arg
    raise AuditError("no package argument")


def npm_pin(server: str, spec: str) -> Pin:
    match = NPM_PIN.match(spec)
    if not match:
        raise AuditError(f"{server}: {spec!r} is not an exact npm pin (name@MAJOR.MINOR.PATCH)")
    return Pin("npm", server, match["name"], match["version"])


def pypi_pin(server: str, spec: str) -> Pin:
    match = PYPI_PIN.match(spec)
    if not match:
        raise AuditError(f"{server}: {spec!r} is not an exact uvx pin (name@version)")
    return Pin("pypi", server, match["name"], match["version"])


def docker_pin(server: str, args: list) -> Pin | None:
    for arg in args:
        if isinstance(arg, str) and "@sha256:" in arg:
            name, digest = arg.split("@", 1)
            return Pin("docker", server, name, digest)
    return None


def server_pin(server: str, entry: dict) -> Pin | None:
    command, args = entry.get("command"), entry.get("args") or []
    if command == "npx":
        return npm_pin(server, first_package_arg(args))
    if command == "uvx":
        return pypi_pin(server, first_package_arg(args))
    if command == "docker":
        return docker_pin(server, args)
    return None


def load_pins(path: Path = SERVERS_YAML) -> list[Pin]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    servers = data.get("servers") if isinstance(data, dict) else None
    if not isinstance(servers, dict) or not servers:
        raise AuditError(f"{path}: no `servers` mapping")
    pins = []
    for server, entry in servers.items():
        pin = server_pin(str(server), entry) if isinstance(entry, dict) else None
        if pin:
            pins.append(pin)
    return pins


def build_package_json(pins: list[Pin]) -> dict:
    """The throwaway manifest: every npm pin as an exact dependency; one version per package."""
    deps: dict[str, str] = {}
    for pin in (p for p in pins if p.kind == "npm"):
        if deps.setdefault(pin.name, pin.version) != pin.version:
            raise AuditError(f"{pin.name} is pinned to two versions")
    if not deps:
        raise AuditError("no npm pins found in servers.yaml")
    return {"name": "emage-mcp-pin-audit", "version": "0.0.0", "private": True,
            "description": "Throwaway manifest generated from servers.yaml; never published.",
            "dependencies": dict(sorted(deps.items()))}


def build_requirements(pins: list[Pin]) -> str:
    lines = sorted(f"{p.name}=={p.version}" for p in pins if p.kind == "pypi")
    return "".join(f"{line}\n" for line in lines)


def write_manifest(directory: Path, pins: list[Pin]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    manifest = build_package_json(pins)
    (directory / "package.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (directory / "requirements-uvx.txt").write_text(build_requirements(pins), encoding="utf-8")


def clean_env(environ: dict[str, str]) -> dict[str, str]:
    """The environment npm gets: nothing that looks like a secret (the registry needs none)."""
    return {k: v for k, v in environ.items() if not SECRET_NAME.search(k)}


Runner = Callable[[list[str], Path], "subprocess.CompletedProcess[str]"]


def run_npm(argv: list[str], cwd: Path) -> "subprocess.CompletedProcess[str]":
    npm = shutil.which("npm")
    if not npm:
        raise AuditError("npm is not on PATH")
    user, glob = Path(cwd) / ".emage-empty-user-npmrc", Path(cwd) / ".emage-empty-global-npmrc"
    for empty in (user, glob):  # a user or global .npmrc could change the registry or add a token (two files: npm refuses one twice)
        empty.write_text("", encoding="utf-8")
    fixed = ["--userconfig", str(user), "--globalconfig", str(glob), "--registry", REGISTRY + "/"]
    return subprocess.run([npm, *fixed, *argv], cwd=cwd, env=clean_env(dict(os.environ)), capture_output=True,
                          text=True, timeout=900, check=False, shell=False)


def npm_install_args(full: bool) -> list[str]:
    base = ["install", "--ignore-scripts", "--no-audit", "--no-fund"]
    return base if full else ["install", "--package-lock-only", *base[1:]]


def parse_accept(value: str) -> tuple[str, dt.date]:
    """``GHSA-xxxx-xxxx-xxxx:YYYY-MM-DD``; the expiry date is mandatory (last day the acceptance counts)."""
    advisory, sep, day = value.partition(":")
    if not sep or not GHSA_RE.fullmatch(advisory) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise argparse.ArgumentTypeError(f"{safe_text(value)!r}: expected GHSA-xxxx-xxxx-xxxx:YYYY-MM-DD (expiry mandatory)")
    try:
        return advisory, dt.date.fromisoformat(day)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{safe_text(value)!r}: not a calendar date") from exc


def advisory_id(via: dict) -> str | None:
    match = GHSA_RE.search(str(via.get("url", "")))
    return match.group(0) if match else None


def fully_accepted(name: str, vulns: dict, active: set[str], seen: frozenset = frozenset()) -> bool:
    """True when every advisory under ``name``, and every package it is vulnerable through, is accepted."""
    vias = (vulns.get(name) or {}).get("via") or []
    if name in seen or not vias:
        return False
    for via in vias:
        if isinstance(via, dict):
            if advisory_id(via) not in active:
                return False
        elif not isinstance(via, str) or via not in vulns or not fully_accepted(via, vulns, active, seen | {name}):
            return False
    return True


def severity_index(severity: object) -> int:
    """Position in LEVELS; a severity npm adds later, or a malformed one, counts as critical (fail closed)."""
    return LEVELS.index(severity) if severity in LEVELS else len(LEVELS) - 1


def summarise_audit(report: dict, level: str, accepted: dict | None = None, today: dt.date | None = None) -> tuple[list[str], int]:
    """(lines to print, number of findings at or above `level`) from `npm audit --json`.

    ``accepted`` maps advisory id to the last day of its acceptance. An accepted package is printed as ACCEPTED
    and not counted; an advisory whose acceptance has expired counts like any other.
    """
    floor = LEVELS.index(level)
    day = today or dt.date.today()
    active = {a for a, until in (accepted or {}).items() if until >= day}
    vulns = report.get("vulnerabilities") or {}
    lines, hits = [], 0
    for name, vuln in sorted(vulns.items()):
        severity = safe_text(vuln.get("severity", "unknown"))
        via = [v for v in vuln.get("via", []) if isinstance(v, dict)]
        titles = "; ".join(f"{safe_text(v.get('title'))} [{safe_text(v.get('range'))}] {safe_text(v.get('url'))}"
                           for v in via) or "via a dependency"
        done = fully_accepted(name, vulns, active)
        lines.append(f"  {'ACCEPTED ' if done else ''}{severity:<8} {safe_text(name)} (direct: {bool(vuln.get('isDirect'))}): {titles}")
        hits += 1 if (not done and severity_index(vuln.get("severity")) >= floor) else 0
    return lines, hits


def acceptance_lines(accepted: dict, today: dt.date) -> tuple[list[str], int]:
    """Print every acceptance with its expiry; an expired one is a failure of its own."""
    lines, expired = [], 0
    for advisory, until in sorted(accepted.items()):
        stale = until < today
        expired += 1 if stale else 0
        lines.append(f"  {'EXPIRED' if stale else 'accepted'} {advisory} until {until.isoformat()}")
    return lines, expired


def manual_read_notice(pins: list[Pin]) -> list[str]:
    names = {p.name: p.version for p in pins if p.kind == "npm"}
    due = [f"{n}@{names[n]}" for n in CALENDAR_VERSION_PACKAGES if n in names]
    if not due:
        return []
    return ["MANUAL ADVISORY READ (SEC-T646-06): these moved from calendar versions to 1.0.0; semver sorts the",
            "calendar-form advisory ranges ABOVE them, so the npm audit result for them is not conclusive.",
            "Read the advisories by hand (GitHub Advisory Database, ecosystem npm) and record the date:",
            *[f"  - {entry}" for entry in due]]


def parse_json(text: str, what: str) -> dict:
    try:
        value = json.loads(text)
    except ValueError as exc:
        raise AuditError(f"{what}: reply is not JSON") from exc
    if not isinstance(value, dict):
        raise AuditError(f"{what}: reply is not a JSON object")
    return value


def audit_directory(directory: Path, level: str, runner: Runner, options: dict) -> tuple[list[str], int]:
    full = bool(options.get("full"))
    install = runner(npm_install_args(full), directory)
    if install.returncode != 0:
        raise AuditError("npm install failed (the registry may be unreachable)")
    result = runner(["audit", "--json"], directory)
    report = parse_json(result.stdout, "npm audit")
    if not isinstance(report.get("vulnerabilities"), dict) or not isinstance(report.get("metadata"), dict):
        raise AuditError("npm audit reply lacks `vulnerabilities` and `metadata` (an error reply is not a clean result)")
    lines, hits = summarise_audit(report, level, options.get("accepted"), options.get("today"))
    if full:
        sig = runner(["audit", "signatures"], directory)
        lines.append("npm audit signatures: " + ("ok" if sig.returncode == 0 else "FAILED"))
        hits += 1 if sig.returncode != 0 else 0
        lines.extend("  " + safe_text(ln) for ln in (sig.stdout or "").strip().splitlines()[:8])
    return lines, hits


def command_audit(args: argparse.Namespace, runner: Runner = run_npm, today: dt.date | None = None) -> int:
    pins = load_pins(Path(args.servers))
    day = today or dt.date.today()
    accepted = dict(getattr(args, "accept", None) or [])
    if len(accepted) != len(getattr(args, "accept", None) or []):
        raise AuditError("the same advisory is accepted twice")
    work = Path(tempfile.mkdtemp(prefix="emage-mcp-pin-audit-"))
    try:
        write_manifest(work, pins)
        options = {"full": args.signatures, "accepted": accepted, "today": day}
        lines, hits = audit_directory(work, args.audit_level, runner, options)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"npm pins audited: {sum(1 for p in pins if p.kind == 'npm')} (audit level: {args.audit_level})")
    print("\n".join(lines) if lines else "  no known vulnerabilities")
    if accepted:
        accept_lines, expired = acceptance_lines(accepted, day)
        print("acceptances (reviewed, expiring):\n" + "\n".join(accept_lines))
        hits += expired
    print("\n".join(manual_read_notice(pins)))
    if any(p.kind == "pypi" for p in pins):
        print("PyPI pins are not covered by npm: run `pip-audit -r requirements-uvx.txt --no-deps` on the "
              "file written by `generate DIR`.")
    print("docker digests are not covered either: check the image's release notes and advisories by hand.")
    print(f"result: {'FINDINGS' if hits else 'no finding at or above the audit level'}")
    return 1 if hits else 0


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """The registry is read from one host only: a redirect is an error, never followed."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


OPENER = urllib.request.build_opener(_RefuseRedirects)


def registry_url(name: str, version: str) -> str:
    return f"{REGISTRY}/{urllib.parse.quote(name, safe='@')}/{urllib.parse.quote(version, safe='')}"


def fetch_registry_json(url: str) -> dict:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != REGISTRY_HOST or parsed.username or parsed.query:
        raise AuditError("refusing a registry URL outside https://registry.npmjs.org")
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with OPENER.open(request, timeout=30) as reply:  # host checked above; redirects are refused
        body = reply.read(MAX_REPLY_BYTES + 1)
    if len(body) > MAX_REPLY_BYTES:
        raise AuditError("registry reply too large")
    return parse_json(body.decode("utf-8", "replace"), "registry")


def has_provenance(meta: dict) -> bool:
    attestations = (meta.get("dist") or {}).get("attestations")
    return isinstance(attestations, dict) and bool(attestations.get("provenance"))


def provenance_rows(pins: list[Pin], fetch: Callable[[str], dict]) -> list[tuple[Pin, bool, str, bool]]:
    rows = []
    for pin in (p for p in pins if p.kind == "npm"):
        pinned = fetch(registry_url(pin.name, pin.version))
        latest = fetch(registry_url(pin.name, "latest"))
        rows.append((pin, has_provenance(pinned), str(latest.get("version")), has_provenance(latest)))
    return rows


def command_provenance(args: argparse.Namespace, fetch: Callable[[str], dict] = fetch_registry_json) -> int:
    rows = provenance_rows(load_pins(Path(args.servers)), fetch)
    missing = 0
    for pin, pinned_ok, latest_version, latest_ok in rows:
        missing += 0 if pinned_ok else 1
        print(f"{pin.name}@{pin.version}: provenance {'yes' if pinned_ok else 'NO'}; "
              f"latest {safe_text(latest_version)}: provenance {'yes' if latest_ok else 'NO'}"
              + ("" if latest_version == pin.version else "  (pin differs from latest)"))
    print(f"pinned versions without provenance: {missing}")
    return 1 if (args.require and missing) else 0


def command_list(args: argparse.Namespace) -> int:
    for pin in load_pins(Path(args.servers)):
        print(f"{pin.kind}\t{pin.server}\t{pin.name}\t{pin.version}")
    return 0


def command_generate(args: argparse.Namespace) -> int:
    write_manifest(Path(args.directory), load_pins(Path(args.servers)))
    print(f"wrote {Path(args.directory) / 'package.json'} and requirements-uvx.txt")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--servers", default=str(SERVERS_YAML), help="servers.yaml to read")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list").set_defaults(func=command_list)
    gen = sub.add_parser("generate")
    gen.add_argument("directory")
    gen.set_defaults(func=command_generate)
    aud = sub.add_parser("audit")
    aud.add_argument("--audit-level", choices=LEVELS, default="low")
    aud.add_argument("--signatures", action="store_true", help="full install + `npm audit signatures`")
    aud.add_argument("--accept", action="append", default=[], type=parse_accept, metavar="GHSA-x:YYYY-MM-DD",
                     help="reviewed acceptance of one advisory, with a mandatory expiry date (repeatable)")
    aud.set_defaults(func=command_audit)
    prov = sub.add_parser("provenance")
    prov.add_argument("--require", action="store_true")
    prov.set_defaults(func=command_provenance)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except AuditError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 -- the message names the type only
        print(f"error: unexpected {type(exc).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
