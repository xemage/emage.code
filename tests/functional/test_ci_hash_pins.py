"""T676 (SEC-T675-09, SEC-T675-03, SEC-T646-04, SEC-014) -- hash-locked Python packages and supported CI images.

Six contracts, each with a mutation proof (the guard's input is damaged in memory and the checker must
then report an error):

  1. every `pip install` in .gitlab-ci.yml is `--require-hashes -r ci/requirements-*.txt`, with no extra
     package, index, find-links or editable argument (the unit-tests job binds the host Docker socket);
  2. every lock file (`ci/*.txt`, `implementation/runtime/*/requirements-mcp-server.lock.txt`) pins every
     entry to `==` with at least one sha256 hash, holds every direct requirement of its input file at a
     version the input allows, and the two runtime locks are identical;
  3. `httpx2` is at least 2.12.0 (GHSA-8xx6-hgc6-gc2m) in both runtime requirement files and every lock;
  4. no CI image is end of life (Node <= 20 or an odd Node major, Alpine <= 3.21, Python <= 3.9; table dated
     2026-10-22), and every image still carries its sha256 digest;
  5. T739 (plan-136): `release-docs-gate` installs `ci/requirements-release.txt` before the gate runs, in the exact
     form, and that lock holds only markdown-it-py and mdurl, at the versions and hashes of the CI lock;
  6. T741 (SEC-T739-05, SEC-T741-01 to -04, -09, -10): `ci_pin_problems` covers these routes. Anywhere in the file: a
     merge key, an explicit tag, a plain scalar starting with a colon, a key that is not a string. On the three tag
     jobs: the keys, stage, rules, variables and image, the `needs` of `release`, and the before_script and script of
     the two gates. At the file level: the refused top-level keys, the stages, the variables and the key names of
     `default`. On any job: a `CI_` variable in `variables` or `parallel:matrix`. Outside the tag jobs: any job that
     could run in a tag pipeline.
     T744 (SEC-T741-12, -17) adds the script and artifacts of `release`, the values of `default.tags` and
     `default.interruptible`, and `GIT_STRATEGY: clone` on the two gates. The before_script of `release` is not pinned
     here (test_publish_release_job_token reads it), and no pin can stop what a job's script does on a branch: that stays
     with code review.
     T750 (SEC-T745-01, -04, -05, -07) adds `GIT_STRATEGY: clone` on `release`, `timeout` on the docs gate, the removal of
     the clone credential that opens the docs gate's before_script, and scripts/run-allowlisted.py on every command of
     the two gates. The allowlist filters a child's environment only: the job's shell keeps its variables, and in the
     drift gate the clone credential stays readable in its file. scripts/run-allowlisted.py itself is code that every
     gate command passes through, and no pin reads it: a change to it is for code review, and test_run_allowlisted only
     catches a careless one, such as an exit under CI's variables (SEC-T751-02).
     SEC-T745-06: none of this binds a project-level `GIT_STRATEGY`. GitLab's order of precedence puts a project variable
     above `variables` in the job (docs.gitlab.com/ci/variables/, read 2026-11-06; for this name not run), so one would
     beat the pin with every test green. The project must hold no variable of that name. It holds none today (its only
     CI/CD variable is WIKI_TOKEN, per the orchestrator, 2026-11-06), and no test reads the project's variables.
     The rule on tag jobs (SEC-T741-16) assumes nobody can set a pipeline variable: a person running a pipeline on a tag
     with `CI_COMMIT_BRANCH=x` would make a branch condition true with no file edit. That is this project's setting
     (`ci_pipeline_variables_minimum_override_role` is `no_one_allowed`, read 2026-11-06), and no test reads it.
     The limit: this guards a merge, because `unit-tests` runs on merge request and branch pipelines, not on a tag. A
     tag cut from a commit that never went through them is not guarded. The check reads the file with PyYAML, and
     GitLab's parser can differ on what PyYAML does not refuse.
     T810 (SEC-T741-17, plan-159) adds `tags: ["release-gate"]` on the three tag jobs, exactly, and refuses the name
     `release-gate` anywhere else in the file (`default`, the file-level variables, hidden jobs, a variable that a
     `tags` entry could expand), a `$` in any other job's `tags`, and an `extends` of a tag job. The runner's own
     settings (protected, run untagged jobs off, `allowed_images`) are the user's, and no test reads them.
"""
from __future__ import annotations

import datetime as dt
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.repo import repo_root

ROOT = repo_root()
CI_YML = ROOT / ".gitlab-ci.yml"
LOCKS = {
    "ci/requirements-ci.txt": "ci/requirements-ci.in",
    "ci/requirements-gate.txt": "ci/requirements-gate.in",
    "ci/requirements-release.txt": "ci/requirements-release.in",
    "implementation/runtime/security/requirements-mcp-server.lock.txt":
        "implementation/runtime/security/requirements-mcp-server.txt",
    "implementation/runtime/memory/requirements-mcp-server.lock.txt":
        "implementation/runtime/memory/requirements-mcp-server.txt",
}
HTTPX2_FLOOR = (2, 12, 0)
ENTRY = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)==(?P<version>[0-9][0-9A-Za-z.!+_-]*)(?P<marker>\s*;[^\\]*)?\s*\\?$")
HASH = re.compile(r"^\s+--hash=sha256:[0-9a-f]{64}\s*\\?$")
INPUT_REQ = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)\s*(?P<op>==|>=)?\s*(?P<version>[0-9][0-9A-Za-z.]*)?\s*$")
RUN_ALLOWLISTED = "python3 -I scripts/run-allowlisted.py"
KEEP_JOB_TOKEN = f"{RUN_ALLOWLISTED} --keep CI_JOB_TOKEN --"
RELEASE_GATE_JOB = "release-docs-gate"
RELEASE_GATE_REMOVE = 'rm -rf .git "${CI_PROJECT_DIR}.tmp"'
RELEASE_GATE_INSTALL = (f"{RUN_ALLOWLISTED} -- python3 -m pip install --no-cache-dir --disable-pip-version-check --quiet "
                        "--require-hashes --only-binary=:all: -r ci/requirements-release.txt")
RELEASE_GATE_COMMAND = f'{RUN_ALLOWLISTED} -- python3 scripts/verify-release-docs.py --tag "${{CI_COMMIT_TAG}}"'
RELEASE_GATE_TIMEOUT = "10 minutes"
DRIFT_GATE_JOB = "main-develop-drift-gate"
DRIFT_GATE_APK = f"{RUN_ALLOWLISTED} -- apk add --no-cache 'git~=2.54'"
DRIFT_GATE_FETCHES = [f"{KEEP_JOB_TOKEN} git fetch origin main develop --depth=1",
                      f"{KEEP_JOB_TOKEN} git fetch --force origin 'refs/tags/*:refs/tags/*'"]
DRIFT_GATE_DRIFT = f"{RUN_ALLOWLISTED} -- python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop"
DRIFT_GATE_TREE = f'{RUN_ALLOWLISTED} -- python3 scripts/check-release-tag-tree.py --tag "${{CI_COMMIT_TAG}}" --main-ref origin/main'
RELEASE_JOB = "release"
RELEASE_COMMAND = ('python3 scripts/publish-release.py --tag "${CI_COMMIT_TAG}" --api-v4-url "${CI_API_V4_URL}" '
                   '--expected-host "${CI_SERVER_HOST}" --project-id "${CI_PROJECT_ID}" '
                   "--token-env CI_JOB_TOKEN --token-header JOB-TOKEN")
RELEASE_ARTIFACTS = {"paths": ["CHANGELOG.md"], "expire_in": "never"}
RELEASE_GATE_RULES = [{"if": r"$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$/"}]
PINNED_IMAGE = re.compile(r"python:3\.12-alpine@sha256:[0-9a-f]{64}")
ANY_PINNED_IMAGE = re.compile(r"[a-z0-9./-]+:[A-Za-z0-9._-]+@sha256:[0-9a-f]{64}")
GATE_KEYS = {"stage", "image", "tags", "before_script", "script", "rules"}
RELEASE_GATE_TAG = "release-gate"  # T810 (SEC-T741-17): the user's dedicated project runner (plan-159)
RELEASE_GATE_TAGS = [RELEASE_GATE_TAG]
# "keys" is the whole allowlist of a job; each "exact" value is compared with the parsed value; `image` is PINNED_IMAGE.
PINNED_JOBS = {
    RELEASE_GATE_JOB: {
        "keys": GATE_KEYS | {"variables", "timeout"},
        "exact": {"stage": "release", "tags": RELEASE_GATE_TAGS, "variables": {"GIT_STRATEGY": "clone"},
                  "timeout": RELEASE_GATE_TIMEOUT,
                  "before_script": [RELEASE_GATE_REMOVE, RELEASE_GATE_INSTALL], "script": [RELEASE_GATE_COMMAND],
                  "rules": RELEASE_GATE_RULES},
    },
    DRIFT_GATE_JOB: {
        "keys": GATE_KEYS | {"variables"},
        "exact": {
            "stage": "release", "tags": RELEASE_GATE_TAGS, "variables": {"GIT_DEPTH": "1", "GIT_STRATEGY": "clone"},
            "rules": RELEASE_GATE_RULES,
            "before_script": [DRIFT_GATE_APK],
            "script": [*DRIFT_GATE_FETCHES, DRIFT_GATE_DRIFT, DRIFT_GATE_TREE],
        },
    },
    RELEASE_JOB: {
        "keys": GATE_KEYS | {"variables", "needs", "artifacts"},
        "exact": {"stage": "release", "tags": RELEASE_GATE_TAGS, "needs": [RELEASE_GATE_JOB, DRIFT_GATE_JOB],
                  "variables": {"GIT_DEPTH": "0", "GIT_STRATEGY": "clone"},
                  "script": [RELEASE_COMMAND], "artifacts": RELEASE_ARTIFACTS, "rules": RELEASE_GATE_RULES},
    },
}
# GitLab still honours the global image, services, cache, before_script and after_script (docs: deprecated keywords).
REFUSED_TOP_LEVEL = ("include", "workflow", "spec", "image", "services", "cache", "before_script", "after_script")
FILE_VARIABLES = {"GIT_DEPTH": "20", "GIT_SUBMODULE_STRATEGY": "none"}
FILE_STAGES = ["lint", "test", "verify", "sync", "wiki-sync", "release"]
DEFAULT_KEYS = {"image", "interruptible", "tags"}
DEFAULT_TAGS = ["docker"]  # the runner of every job without its own `tags`; the three tag jobs set RELEASE_GATE_TAGS
FILE_LEVEL_KEYS = {"default", "variables", "stages", *REFUSED_TOP_LEVEL}
NOT_TAG_CONDITIONS = {  # none of these is true in a tag pipeline, where CI_COMMIT_BRANCH is not set
    '$CI_PIPELINE_SOURCE == "merge_request_event"',
    "$CI_COMMIT_BRANCH",
    '$CI_COMMIT_BRANCH == "develop"',
    '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == "develop"',
}
RELEASE_LOCK_PACKAGES = {"markdown-it-py", "mdurl"}
FORBIDDEN_PIP_FLAGS = ("-i", "--index-url", "--extra-index-url", "-f", "--find-links", "--trusted-host",
                       "-e", "--editable", "--no-deps", "--pre", "--no-index", "--break-system-packages")


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version.split("+")[0])[:4])


# ---- 1. the CI file ------------------------------------------------------------------------------------

def ci_command_lines(ci_text: str) -> list[str]:
    """Every command line of every script, before_script and after_script block (and `default`)."""
    document = yaml.safe_load(ci_text)
    lines: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("script", "before_script", "after_script") and isinstance(value, list):
                    for item in value:
                        lines.extend(str(item).splitlines())
                else:
                    walk(value)

    walk(document)
    return [ln.strip() for ln in lines if ln.strip()]


def pip_install_problems(ci_text: str, root=ROOT) -> list[str]:
    """Problems with every pip/uv install invocation in the pipeline; an empty list means all are locked."""
    problems, seen = [], 0
    for line in ci_command_lines(ci_text):
        if not re.search(r"\b(pip3?|uv|pipx)\b\s+(?:\S+\s+)*?(install|sync|add)\b|-m\s+pip\b|\bpip3?\s+download\b", line):
            continue
        if re.match(r"^(#|echo\b)", line):
            continue
        seen += 1
        try:
            tokens = shlex.split(line)
        except ValueError:
            problems.append(f"unparseable pip line: {line!r}")
            continue
        problems.extend(pip_tokens_problems(tokens, line, root))
    if not seen:
        problems.append("no pip install found: the parser would pass a pipeline with none")
    return problems


def pip_tokens_problems(tokens: list[str], line: str, root) -> list[str]:
    if "install" not in tokens or tokens[:1] in (["uv"], ["pipx"]):
        return [f"not a plain `pip install` (uv, pipx and other forms are refused): {line!r}"]
    args = tokens[tokens.index("install") + 1:]
    out = []
    if "--require-hashes" not in args:
        out.append(f"missing --require-hashes: {line!r}")
    if "--only-binary=:all:" not in args:  # SEC-T676-08: an sdist would run its build backend inside the job
        out.append(f"missing --only-binary=:all: (no source builds): {line!r}")
    out.extend(f"forbidden pip flag {a!r}: {line!r}" for a in args if a.split("=")[0] in FORBIDDEN_PIP_FLAGS)
    files = [args[i + 1] for i, a in enumerate(args[:-1]) if a == "-r"]
    if len(files) != 1:
        out.append(f"exactly one `-r ci/requirements-*.txt` is required: {line!r}")
    positional = [a for i, a in enumerate(args) if not a.startswith("-") and (i == 0 or args[i - 1] != "-r")]
    if positional:
        out.append(f"package or path argument outside the lock: {positional!r} in {line!r}")
    for file in files:
        if not re.fullmatch(r"ci/requirements-[a-z]+\.txt", file) or not (root / file).is_file():
            out.append(f"{file!r} is not an existing ci/requirements-*.txt: {line!r}")
    return out


# ---- 2. the lock files ---------------------------------------------------------------------------------

def parse_lock(text: str) -> tuple[dict[str, list[str]], list[str]]:
    """({normalized name: [versions]}, problems). Every entry needs `==` and at least one sha256 hash."""
    entries: dict[str, list[str]] = {}
    problems: list[str] = []
    current: str | None = None
    hashes = 0
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if HASH.match(line):
            hashes += 1
            continue
        match = ENTRY.match(line)
        if current is not None and hashes == 0:
            problems.append(f"line {number}: {current} has no sha256 hash")
        if not match:
            problems.append(f"line {number}: not an exact `name==version` entry: {line.strip()!r}")
            current, hashes = None, 0
            continue
        current, hashes = match["name"], 0
        entries.setdefault(norm(match["name"]), []).append(match["version"])
    if current is not None and hashes == 0:
        problems.append(f"{current} has no sha256 hash")
    if not entries:
        problems.append("lock has no entries")
    return entries, problems


def input_requirements(text: str) -> dict[str, tuple[str | None, str | None]]:
    found = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        match = INPUT_REQ.match(line)
        if not match:
            raise AssertionError(f"input line not understood by the test (extend it): {line!r}")
        found[norm(match["name"])] = (match["op"], match["version"])
    return found


def lock_problems(lock_text: str, input_text: str) -> list[str]:
    entries, problems = parse_lock(lock_text)
    for name, (op, wanted) in input_requirements(input_text).items():
        versions = entries.get(name)
        if not versions:
            problems.append(f"{name} is required by the input file but absent from the lock")
        elif op == "==" and wanted not in versions:
            problems.append(f"{name}=={wanted} required, locked {versions}")
        elif op == ">=" and any(version_tuple(v) < version_tuple(wanted) for v in versions):
            problems.append(f"{name}>={wanted} required, locked {versions}")
    return problems


# ---- 5. the release gate's parser ---------------------------------------------------------------------

def mapping_keys(ci_text: str) -> list[yaml.Node]:
    """The key node of every mapping in the file. `seen` ends a recursive alias: without it this never returns."""
    keys: list[yaml.Node] = []
    seen: set[int] = set()
    stack = [yaml.compose(ci_text, Loader=yaml.SafeLoader)]
    while stack:
        node = stack.pop()
        if node is None or id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, yaml.SequenceNode):
            stack.extend(node.value)
        elif isinstance(node, yaml.MappingNode):
            for key, value in node.value:
                keys.append(key)
                stack.extend((key, value))
    return keys


def is_merge_key(key: yaml.Node) -> bool:
    return key.tag == "tag:yaml.org,2002:merge" or (isinstance(key, yaml.ScalarNode) and key.value == "<<")


def merge_key_lines(ci_text: str) -> list[int]:
    """SEC-T741-01: the line of every merge key, from the node tree: plain, quoted or `!!merge`, in any mapping.
    `!!binary PDw=` is one too, and spelling_problems refuses it.

    PyYAML and GitLab disagree here: on an explicit key PyYAML keeps the explicit value, while GitLab's lint lets a `<<`
    written after it override it, also inside a rule, and it merges a quoted "<<" that PyYAML keeps as a plain key. So a
    check of parsed values cannot see this route. A `<<` inside a block scalar is text, not a key.
    """
    return sorted(key.start_mark.line + 1 for key in mapping_keys(ci_text) if is_merge_key(key))


def spelling_problems(ci_text: str) -> list[str]:
    """SEC-T741-09: keys PyYAML keeps apart and GitLab folds into one, so that a check of parsed values reads another
    key than the one that runs. GitLab's lint runs `exit 0` as the gate for an added `:release-docs-gate:`, and it reads
    `!!null release-docs-gate`, `!!binary PDw=` (`<<`) and `!!binary aW5jbHVkZQ==` (`include`) by their text.
    """
    problems = []
    for event in yaml.parse(ci_text, Loader=yaml.SafeLoader):
        line = event.start_mark.line + 1
        if getattr(event, "tag", None) is not None:
            problems.append(f"line {line}: the explicit tag {event.tag} is refused (SEC-T741-09)")
        if isinstance(event, yaml.ScalarEvent) and event.implicit[0] and event.value.startswith(":"):
            problems.append(f"line {line}: a plain scalar starting with a colon is a symbol to GitLab (SEC-T741-09)")
    problems += [f"line {key.start_mark.line + 1}: a key must be a string, not {key.tag} (SEC-T741-09)"
                 for key in mapping_keys(ci_text)
                 if key.tag != "tag:yaml.org,2002:str" and not is_merge_key(key)]
    return problems


def job_variable_names(job: dict) -> list[str]:
    """The names a job sets for itself, in `variables` and in `parallel:matrix`."""
    variables = job.get("variables")
    names = list(variables) if isinstance(variables, dict) else []
    parallel = job.get("parallel")
    matrix = parallel.get("matrix") if isinstance(parallel, dict) else None
    for row in matrix if isinstance(matrix, list) else []:
        names += list(row) if isinstance(row, dict) else []
    return [str(name) for name in names]


def predefined_variable_problems(ci: dict) -> list[str]:
    """SEC-T741-10: a job that sets `CI_COMMIT_BRANCH` itself makes `if: $CI_COMMIT_BRANCH` true in a tag pipeline,
    which GitLab's dry run on a tag confirms, so the conditions in NOT_TAG_CONDITIONS would no longer exclude it."""
    return [f"{name}: the variable {variable} is refused, a job may not set a CI_ variable (SEC-T741-10)"
            for name, job in ci.items() if isinstance(job, dict)
            for variable in job_variable_names(job) if variable.startswith("CI_")]


def pinned_job_problems(name: str, job: object) -> list[str]:
    """SEC-T739-05, SEC-T741-02, SEC-T741-04: an allowlist, so a key added later is refused too. Parsed values only, so
    a comment counts for nothing, and merge_key_lines covers what PyYAML does not parse as GitLab does.

    An allowed failure or a manual gate would let `release` go on, because its `needs` does not stop a release after
    an allowed failure. `before_script` runs before `script` in the same shell, so an `exit 0` there skips the gate.
    """
    if not isinstance(job, dict):
        return [f"{name} is not a job"]
    pin = PINNED_JOBS[name]
    problems = []
    if set(job) != pin["keys"]:
        problems.append(f"{name} must have exactly the keys {sorted(pin['keys'])}, not {sorted(map(str, job))}")
    for field, wanted in pin["exact"].items():
        if job.get(field) != wanted:
            problems.append(f"{name} does not run the gate as pinned: {field} must be {wanted!r}"
                            if field == "script" else f"{name} must have exactly this {field}: {wanted!r}")
    image = job.get("image")
    if not (isinstance(image, str) and PINNED_IMAGE.fullmatch(image)):
        problems.append(f"{name} must have an image string matching {PINNED_IMAGE.pattern}, not {image!r}")
    return problems


def release_gate_job_problems(ci_text: str) -> list[str]:
    return pinned_job_problems(RELEASE_GATE_JOB, yaml.safe_load(ci_text).get(RELEASE_GATE_JOB))


def file_level_problems(ci: dict) -> list[str]:
    """SEC-T741-03: what reaches every job from outside it. `spec` also has a header form: see ci_pin_problems."""
    problems = [f"the top-level key {key} is refused: it reaches the pinned jobs from outside"
                for key in REFUSED_TOP_LEVEL if key in ci]
    if ci.get("variables") != FILE_VARIABLES:
        problems.append(f"the top-level variables must be exactly {FILE_VARIABLES!r}")
    if ci.get("stages") != FILE_STAGES:
        problems.append(f"the stages must be exactly {FILE_STAGES!r}")
    default = ci.get("default")
    if not isinstance(default, dict) or set(default) != DEFAULT_KEYS:
        problems.append(f"default must hold exactly {sorted(DEFAULT_KEYS)}")
        return problems
    if default["tags"] != DEFAULT_TAGS:
        problems.append(f"default.tags must be exactly {DEFAULT_TAGS!r}")
    if default["interruptible"] is not True:  # `is`: 1 == True in Python, and 1 is not what GitLab accepts here
        problems.append("default.interruptible must be exactly true")
    return problems


def tag_runnable_job_problems(ci: dict) -> list[str]:
    """SEC-T741-03, -11, -15: outside the pinned jobs, no job may be able to run in a tag pipeline, whatever it does.

    The gates declare no `needs`, so they receive the artifacts of every earlier job there, and the ways to make those
    are not a closed list: `pages` makes them without an `artifacts` key. So this asks where a job can run, not what it
    makes. Each rule needs an `if` from NOT_TAG_CONDITIONS, and a job with no `rules` is refused, as one with `only` or
    one inheriting them through `extends` has none of its own. A hidden job does not run: a job that extends it needs
    its own rules here, and predefined_variable_problems walks its variables.
    """
    problems = []
    for name, job in ci.items():
        if name in PINNED_JOBS or name in FILE_LEVEL_KEYS or str(name).startswith(".") or not isinstance(job, dict):
            continue
        rules = job.get("rules")
        if not (isinstance(rules, list) and rules
                and all(isinstance(rule, dict) and rule.get("if") in NOT_TAG_CONDITIONS for rule in rules)):
            problems.append(f"{name} could run in a tag pipeline: "
                            "each of its rules needs an if from NOT_TAG_CONDITIONS")
    return problems


def strings_in(node: object) -> list[str]:
    """Every string in a parsed value, mapping keys included."""
    if isinstance(node, dict):
        return [s for key, value in node.items() for s in strings_in(key) + strings_in(value)]
    if isinstance(node, list):
        return [s for item in node for s in strings_in(item)]
    return [node] if isinstance(node, str) else []


def runner_tag_problems(ci: dict) -> list[str]:
    """T810 (SEC-T741-17): only the three tag jobs reach the dedicated runner. A job-level `tags` replaces
    `default.tags`, and GitLab expands variables in `tags`, so outside the tag jobs the name may not occur at all, no
    other job's `tags` may hold a `$`, and nothing may `extends` a tag job (it would inherit the tag). Hidden jobs, the
    file-level keys and `default` are walked too. A comment counts for nothing: these are parsed values."""
    problems = []
    for name, node in ci.items():
        if name in PINNED_JOBS:
            continue
        if any(RELEASE_GATE_TAG in s for s in strings_in(name) + strings_in(node)):
            problems.append(f"{name} names {RELEASE_GATE_TAG}: only the three tag jobs may (SEC-T741-17)")
        if not isinstance(node, dict) or name in FILE_LEVEL_KEYS:
            continue
        if any("$" in s for s in strings_in(node.get("tags"))):
            problems.append(f"{name}: a variable in tags is refused, it could expand to {RELEASE_GATE_TAG} (SEC-T741-17)")
        extends = node.get("extends")
        if set(strings_in(extends)) & set(PINNED_JOBS):
            problems.append(f"{name} extends a tag job and would inherit its runner tag (SEC-T741-17)")
    return problems


def ci_images(ci_text: str) -> list[tuple[str, object]]:
    """SEC-T741-04: (where, parsed value) of the `image` of `default`, of every job, and of the file level."""
    ci = yaml.safe_load(ci_text)
    found = [("the file level", ci["image"])] if "image" in ci else []
    return found + [(name, body["image"]) for name, body in ci.items() if isinstance(body, dict) and "image" in body]


def image_pin_problems(ci_text: str) -> list[str]:
    """A text search skips `image: x # comment` and the mapping forms, so this walks the parsed values. No mapping."""
    return [f"{where}: image must be a string with a sha256 digest, not {image!r}"
            for where, image in ci_images(ci_text)
            if not (isinstance(image, str) and ANY_PINNED_IMAGE.fullmatch(image))]


def ci_pin_problems(ci_text: str) -> list[str]:
    """Every pin of contract 6 on the CI file. A file that does not load as one plain document is refused: a `spec`
    header before `---` and a `!reference` tag end here, because PyYAML cannot read them as GitLab does."""
    try:
        lines = merge_key_lines(ci_text)
        spelling = spelling_problems(ci_text)
        ci = yaml.safe_load(ci_text)
    except yaml.YAMLError as failure:
        return [f"the CI file does not load as one plain document: {getattr(failure, 'problem', failure)}"]
    if not isinstance(ci, dict):
        return ["the CI file does not load as one plain document: it is not a mapping"]
    problems = [f"line {line}: a merge key is refused, PyYAML and GitLab read it differently (SEC-T741-01)"
                for line in lines]
    problems += spelling
    problems += predefined_variable_problems(ci)
    problems += file_level_problems(ci)
    problems += tag_runnable_job_problems(ci)
    problems += runner_tag_problems(ci)
    problems += image_pin_problems(ci_text)
    for name in PINNED_JOBS:
        problems += pinned_job_problems(name, ci.get(name))
    return problems


def lock_hashes(text: str) -> dict[tuple[str, str], set[str]]:
    """{(normalized name, version): the sha256 hashes of that entry}."""
    found: dict[tuple[str, str], set[str]] = {}
    current: tuple[str, str] | None = None
    for line in text.splitlines():
        entry = ENTRY.match(line)
        if entry:
            current = (norm(entry["name"]), entry["version"])
            found[current] = set()
        elif current is not None and HASH.match(line):
            found[current].add(line.split("sha256:")[1].split()[0])
    return found


def release_lock_problems(release_text: str, ci_text: str) -> list[str]:
    """The release lock adds no package, version or wheel that the CI lock does not already hold."""
    release, ci = lock_hashes(release_text), lock_hashes(ci_text)
    names = {name for name, _ in release}
    problems = [f"unexpected package set in the release lock: {sorted(names)}"] if names != RELEASE_LOCK_PACKAGES else []
    for key, hashes in release.items():
        if key not in ci:
            problems.append(f"{key[0]}=={key[1]} is not the version of ci/requirements-ci.txt")
        elif hashes != ci[key]:
            problems.append(f"{key[0]}=={key[1]} has other hashes than ci/requirements-ci.txt")
    return problems


# ---- 4. images -----------------------------------------------------------------------------------------

def eol_image_problems(ci_text: str) -> list[str]:
    """The end-of-life check on a pipeline's parsed images. Text that is not a pipeline goes to eol_problems_of: parsed
    as YAML, repeated `image:` lines would collapse to the last one, and the others would go unchecked."""
    return eol_problems_of(ci_images(ci_text))


def eol_problems_of(images: list[tuple[str, object]]) -> list[str]:
    """Images that are end of life on 2026-10-22: Node <= 20 or odd majors, Alpine <= 3.21, Python <= 3.9."""
    problems = []
    for where, image in images:
        if not isinstance(image, str):
            problems.append(f"{where}: image is not a string: {image!r}")
            continue
        name, _, rest = image.partition(":")
        tag = rest.split("@")[0]
        if "@sha256:" not in image:
            problems.append(f"{image}: no digest")
        if name == "node":
            major = int(re.match(r"\d+", tag).group(0))
            if major <= 20 or major % 2:
                problems.append(f"{image}: Node {major} is end of life or not an LTS line")
        elif name == "alpine" and version_tuple(tag)[:2] <= (3, 21):
            problems.append(f"{image}: Alpine {tag} is end of life")
        elif name == "python" and version_tuple(tag)[:2] <= (3, 9):
            problems.append(f"{image}: Python {tag} is end of life")
    return problems


class TestCiPipInstallsAreHashLocked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ci = CI_YML.read_text(encoding="utf-8")

    def test_every_pip_install_is_hash_locked(self):
        self.assertEqual(pip_install_problems(self.ci), [])

    def test_the_install_lines_use_their_own_locks(self):
        self.assertIn("-r ci/requirements-ci.txt", self.ci)
        self.assertIn("-r ci/requirements-gate.txt", self.ci)
        self.assertIn("-r ci/requirements-release.txt", self.ci)
        self.assertNotIn("pip install --no-cache-dir pyyaml", self.ci)

    def test_mutation_a_floating_package_is_detected(self):
        bad = self.ci.replace("--require-hashes --only-binary=:all: -r ci/requirements-gate.txt", "--only-binary=:all: pyyaml jsonschema")
        self.assertTrue(any("require-hashes" in p for p in pip_install_problems(bad)))

    def test_mutation_dropping_require_hashes_is_detected(self):
        bad = self.ci.replace("--require-hashes --only-binary=:all: -r ci/requirements-ci.txt", "--only-binary=:all: -r ci/requirements-ci.txt")
        self.assertTrue(any("missing --require-hashes" in p for p in pip_install_problems(bad)))

    def test_mutation_dropping_only_binary_is_detected(self):
        bad = self.ci.replace(" --only-binary=:all:", "", 1)
        self.assertNotEqual(bad, self.ci)
        self.assertTrue(any("--only-binary" in p for p in pip_install_problems(bad)))
        self.assertEqual(self.ci.count("--only-binary=:all:"), 3)  # all three install lines carry it

    def test_mutation_an_extra_package_beside_the_lock_is_detected(self):
        bad = self.ci.replace("-r ci/requirements-ci.txt", "-r ci/requirements-ci.txt requests")
        self.assertTrue(any("outside the lock" in p for p in pip_install_problems(bad)))

    def test_mutation_an_extra_index_and_a_missing_lock_file_are_detected(self):
        bad = self.ci.replace("--require-hashes --only-binary=:all: -r ci/requirements-ci.txt",
                              "--require-hashes --only-binary=:all: --extra-index-url https://x.example -r ci/requirements-ci.txt")
        self.assertTrue(any("forbidden pip flag" in p for p in pip_install_problems(bad)))
        bad = self.ci.replace("ci/requirements-gate.txt", "ci/requirements-nope.txt")
        self.assertTrue(any("not an existing" in p for p in pip_install_problems(bad)))

    def test_mutation_an_added_unlocked_install_line_is_detected(self):
        bad = self.ci.replace("  script:\n    - python3 tests/run.py", "  script:\n    - pip install requests\n    - python3 tests/run.py")
        self.assertNotEqual(bad, self.ci)
        self.assertTrue(pip_install_problems(bad))

    def test_uv_and_pipx_installs_are_refused(self):
        for line in ("uv pip install requests", "pipx install pyyaml"):
            bad = self.ci.replace("  script:\n    - python3 tests/run.py", f"  script:\n    - {line}\n    - python3 tests/run.py")
            self.assertTrue(pip_install_problems(bad), line)

    def test_a_pipeline_without_any_pip_install_is_not_a_pass(self):
        self.assertTrue(pip_install_problems("job:\n  script:\n    - echo hi\n"))


class TestLockFiles(unittest.TestCase):
    def read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_every_lock_is_complete_and_matches_its_input(self):
        for lock, source in LOCKS.items():
            with self.subTest(lock=lock):
                self.assertEqual(lock_problems(self.read(lock), self.read(source)), [])

    def test_every_lock_documents_its_regeneration_command(self):
        for lock, source in LOCKS.items():
            with self.subTest(lock=lock):
                header = "\n".join(self.read(lock).splitlines()[:3])
                self.assertIn("--generate-hashes", header)
                self.assertIn(source.rsplit("/", 1)[-1], header)

    def test_the_two_runtime_locks_are_identical_and_hold_the_sdk_pin(self):
        security = self.read("implementation/runtime/security/requirements-mcp-server.lock.txt")
        self.assertEqual(security, self.read("implementation/runtime/memory/requirements-mcp-server.lock.txt"))
        pin = re.search(r"^mcp==(\S+)$", self.read("implementation/runtime/security/requirements-mcp-server.txt"), re.M)
        self.assertIn(pin.group(1), parse_lock(security)[0]["mcp"])

    def test_httpx2_is_at_least_the_patched_floor_everywhere(self):
        for rel in ("implementation/runtime/security/requirements-mcp-server.txt",
                    "implementation/runtime/memory/requirements-mcp-server.txt"):
            self.assertRegex(self.read(rel), r"(?m)^httpx2>=2\.12\.0$", rel)
        for lock in LOCKS:
            entries, _ = parse_lock(self.read(lock))
            for version in entries.get("httpx2", []):
                with self.subTest(lock=lock, version=version):
                    self.assertGreaterEqual(version_tuple(version), HTTPX2_FLOOR)

    def test_the_ci_lock_holds_every_package_the_job_used_to_install(self):
        entries, _ = parse_lock(self.read("ci/requirements-ci.txt"))
        for name in ("pyyaml", "jsonschema", "requests", "pyarrow", "cryptography", "mcp"):
            self.assertIn(name, entries)
        self.assertGreaterEqual(version_tuple(entries["cryptography"][0]), (43, 0, 1))

    def test_mutation_an_entry_without_any_hash_is_detected(self):
        lock = self.read("ci/requirements-gate.txt")
        bad = re.sub(r"(?m)^(pyyaml==\S+) \\\n(?:    --hash=\S+(?: \\)?\n)+", r"\1\n", lock)
        self.assertNotEqual(bad, lock)
        problems = lock_problems(bad, self.read("ci/requirements-gate.in"))
        self.assertTrue(any("pyyaml has no sha256 hash" in p for p in problems), problems)

    def test_mutation_a_malformed_hash_is_detected(self):
        lock = self.read("ci/requirements-gate.txt")
        bad = re.sub(r"--hash=sha256:[0-9a-f]{64}", "--hash=sha256:abc", lock)
        self.assertTrue(lock_problems(bad, self.read("ci/requirements-gate.in")))

    def test_mutation_a_range_in_a_lock_is_detected(self):
        lock = self.read("ci/requirements-gate.txt")
        bad = re.sub(r"(?m)^pyyaml==", "pyyaml>=", lock, count=1)
        self.assertTrue(any("not an exact" in p for p in lock_problems(bad, self.read("ci/requirements-gate.in"))))

    def test_mutation_a_requirement_dropped_from_the_lock_is_detected(self):
        lock = self.read("ci/requirements-gate.txt")
        bad = re.sub(r"(?ms)^jsonschema==.*?(?=^\S)", "", lock, count=1)
        self.assertNotEqual(bad, lock)
        self.assertTrue(any("absent from the lock" in p for p in lock_problems(bad, self.read("ci/requirements-gate.in"))))

    def test_mutation_a_stale_lock_version_is_detected(self):
        lock = self.read("ci/requirements-ci.txt")
        bad = re.sub(r"(?m)^mcp==\S+", "mcp==2.1.0", lock, count=1)
        self.assertTrue(any("mcp==2.2.0 required" in p for p in lock_problems(bad, self.read("ci/requirements-ci.in"))))

    def test_mutation_an_unpatched_httpx2_floor_is_detected(self):
        lock = self.read("implementation/runtime/security/requirements-mcp-server.lock.txt")
        bad = re.sub(r"(?m)^httpx2==2\.1[46]\.0", "httpx2==2.5.0", lock)
        self.assertNotEqual(bad, lock)
        problems = lock_problems(bad, self.read("implementation/runtime/security/requirements-mcp-server.txt"))
        self.assertTrue(any("httpx2>=2.12.0 required" in p for p in problems))


class TestReleaseGateParserInstall(unittest.TestCase):
    """T739 (plan-136): no MR pipeline runs this job, so these pins are what guards its install until a tag pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.ci = CI_YML.read_text(encoding="utf-8")
        cls.release = (ROOT / "ci/requirements-release.txt").read_text(encoding="utf-8")
        cls.ci_lock = (ROOT / "ci/requirements-ci.txt").read_text(encoding="utf-8")

    def _mutated_ci(self, old: str, new: str) -> str:
        bad = self.ci.replace(old, new)
        self.assertNotEqual(bad, self.ci)
        return bad

    def test_the_job_installs_the_lock_before_the_gate_runs(self):
        self.assertEqual(release_gate_job_problems(self.ci), [])

    def test_mutation_removing_the_install_is_detected(self):
        bad = self._mutated_ci(f"    - '{RELEASE_GATE_INSTALL}'\n", "")
        self.assertTrue(any("before_script" in p for p in release_gate_job_problems(bad)))

    def test_mutation_installing_after_the_gate_is_detected(self):
        bad = self._mutated_ci(f"    - '{RELEASE_GATE_INSTALL}'\n", "")
        bad = bad.replace(f"    - {RELEASE_GATE_COMMAND}\n", f"    - {RELEASE_GATE_COMMAND}\n    - '{RELEASE_GATE_INSTALL}'\n")
        self.assertTrue(any("before_script" in p for p in release_gate_job_problems(bad)))

    def test_mutation_another_form_or_lock_is_detected(self):
        for old, new in (("--require-hashes --only-binary=:all: -r ci/requirements-release.txt",
                          "--only-binary=:all: -r ci/requirements-release.txt"),
                         ("--only-binary=:all: -r ci/requirements-release.txt", "-r ci/requirements-release.txt"),
                         ("-r ci/requirements-release.txt", "-r ci/requirements-ci.txt")):
            with self.subTest(new):
                self.assertTrue(release_gate_job_problems(self._mutated_ci(old, new)))

    def test_mutation_dropping_the_gate_is_detected(self):
        bad = self._mutated_ci(f"    - {RELEASE_GATE_COMMAND}\n", "    - echo skipped\n")
        self.assertTrue(any("does not run the gate" in p for p in release_gate_job_problems(bad)))

    def test_the_release_lock_matches_the_ci_lock(self):
        self.assertEqual(release_lock_problems(self.release, self.ci_lock), [])
        self.assertEqual({key[0] for key in lock_hashes(self.release)}, RELEASE_LOCK_PACKAGES)

    def test_mutation_another_version_on_either_side_is_detected(self):
        problems = release_lock_problems(self.release.replace("markdown-it-py==4.2.0", "markdown-it-py==4.3.0"), self.ci_lock)
        self.assertTrue(any("not the version" in p for p in problems), problems)
        problems = release_lock_problems(self.release, self.ci_lock.replace("mdurl==0.1.2", "mdurl==0.1.3"))
        self.assertTrue(any("not the version" in p for p in problems), problems)

    def test_mutation_another_hash_is_detected(self):
        bad = re.sub(r"--hash=sha256:[0-9a-f]{64}", "--hash=sha256:" + "0" * 64, self.release, count=1)
        self.assertNotEqual(bad, self.release)
        self.assertTrue(any("other hashes" in p for p in release_lock_problems(bad, self.ci_lock)))

    def test_mutation_an_extra_or_a_missing_package_is_detected(self):
        extra = self.release + "pyyaml==6.0.3 \\\n    --hash=sha256:" + "0" * 64 + "\n"
        self.assertTrue(any("package set" in p for p in release_lock_problems(extra, self.ci_lock)))
        missing = re.sub(r"(?ms)^mdurl==.*", "", self.release)
        self.assertTrue(any("package set" in p for p in release_lock_problems(missing, self.ci_lock)))


class _CiMutations(unittest.TestCase):
    """Each mutation is confirmed applied: the old text occurs exactly once where the mutation says it does."""

    RULE = f"    - if: '{RELEASE_GATE_RULES[0]['if']}'\n"
    STAGE = "  stage: release\n"
    SCRIPT = f"    - {RELEASE_GATE_COMMAND}\n"

    @classmethod
    def setUpClass(cls):
        cls.ci = CI_YML.read_text(encoding="utf-8")

    def _in_job(self, old: str, new: str, job: str = RELEASE_GATE_JOB) -> str:
        """The CI text with ``old`` replaced in this job's block only. It says nothing about how the result parses."""
        block = re.search(rf"(?ms)^{re.escape(job)}:\n.*?(?=^\S|\Z)", self.ci)
        self.assertIsNotNone(block, job)
        self.assertEqual(block[0].count(old), 1, old)
        return self.ci[:block.start()] + block[0].replace(old, new) + self.ci[block.end():]

    def _mutated_job(self, old: str, new: str, job: str = RELEASE_GATE_JOB) -> str:
        """``_in_job``, for a mutation PyYAML sees: this job loads changed, and every other top-level key unchanged."""
        bad = self._in_job(old, new, job)
        before, after = yaml.safe_load(self.ci), yaml.safe_load(bad)
        self.assertNotEqual(after.pop(job), before.pop(job))
        self.assertEqual(after, before)
        return bad

    def _in_file(self, old: str, new: str) -> str:
        self.assertEqual(self.ci.count(old), 1, old)
        return self.ci.replace(old, new)

    def _assert_ci_refused(self, bad: str, expected: str) -> None:
        self.assertNotEqual(bad, self.ci)
        problems = ci_pin_problems(bad)
        self.assertTrue(any(expected in problem for problem in problems), problems)


class TestReleaseGateJobPin(_CiMutations):
    """T741 (SEC-T739-05): each mutation changes this job only. The tag pattern is on other jobs too, so a replace over
    the whole file would mutate those as well."""

    def _assert_refused(self, bad: str, *expected: str) -> None:
        problems = release_gate_job_problems(bad)
        for text in expected:
            self.assertTrue(any(text in problem for problem in problems), problems)

    def test_the_pipeline_as_it_is_passes(self):
        self.assertEqual(release_gate_job_problems(self.ci), [])

    def test_mutation_a_key_on_the_job_is_refused(self):
        for name, added in (("allow_failure", "  allow_failure: true\n"),
                            ("allow_failure with exit codes", "  allow_failure:\n    exit_codes: 1\n"),
                            ("when", "  when: manual\n"),
                            ("extends", "  extends: .soft\n"),
                            ("after_script", "  after_script:\n    - echo done\n"),
                            ("a key added later", "  retry: 2\n")):
            with self.subTest(name):
                self._assert_refused(self._mutated_job(self.STAGE, self.STAGE + added), "must have exactly the keys")

    def test_mutation_a_key_inside_the_rule_is_refused(self):
        for name, added in (("allow_failure", "      allow_failure: true\n"), ("when", "      when: manual\n")):
            with self.subTest(name):
                self._assert_refused(self._mutated_job(self.RULE, self.RULE + added), "exactly this rules")

    def test_mutation_a_second_rule_is_refused(self):
        self._assert_refused(self._mutated_job(self.RULE, self.RULE + "    - when: always\n"), "exactly this rules")

    def test_mutation_a_changed_tag_pattern_is_refused(self):
        for old, new in (("/^v[0-9]+", "/v[0-9]+"), ("?$/", "?/"), ("$CI_COMMIT_TAG =~", "$CI_COMMIT_REF_NAME =~")):
            with self.subTest(new):
                self._assert_refused(self._mutated_job(old, new), "exactly this rules")

    def test_mutation_another_script_line_is_refused(self):
        for name, new in (("exit 0 before the gate", f"    - exit 0\n{self.SCRIPT}"),
                          ("a line after the gate", f"{self.SCRIPT}    - echo done\n")):
            with self.subTest(name):
                self._assert_refused(self._mutated_job(self.SCRIPT, new), "does not run the gate")

    def test_mutation_another_stage_is_refused(self):
        self._assert_refused(self._mutated_job(self.STAGE, "  stage: test\n"), "exactly this stage")

    def test_a_missing_job_is_refused(self):
        self.assertEqual(release_gate_job_problems("stages: [release]\n"), [f"{RELEASE_GATE_JOB} is not a job"])


class TestCiMergeKeys(_CiMutations):
    """T741 (SEC-T741-01). These mutations go through `_in_job`, not `_mutated_job`: PyYAML does not see most of them.
    Each test proves the mutation's line, and the blind ones prove that the parsed pin alone still passes."""

    MERGE_SCRIPT = '  <<: {script: ["exit 0"]}\n'
    MERGE_RULES = '  <<: {rules: [{if: "$CI_COMMIT_BRANCH"}]}\n'

    def _assert_line_refused(self, bad: str, written: str) -> None:
        line = bad[:bad.index(written)].count("\n") + 1
        self.assertEqual(merge_key_lines(bad), [line])
        self.assertIn(f"line {line}: a merge key is refused, PyYAML and GitLab read it differently (SEC-T741-01)",
                      ci_pin_problems(bad))

    def _assert_blind_to_a_parsed_pin(self, bad: str) -> None:
        self.assertEqual(yaml.safe_load(bad)[RELEASE_GATE_JOB], yaml.safe_load(self.ci)[RELEASE_GATE_JOB])
        self.assertEqual(release_gate_job_problems(bad), [])

    def test_the_pipeline_has_none_and_its_heredoc_is_not_one(self):
        self.assertIn("<<'PY'", self.ci)
        self.assertEqual(merge_key_lines(self.ci), [])
        self.assertEqual(merge_key_lines("j:\n  script:\n    - |\n      <<: x\n      <<EOF\n"), [])

    def test_mutation_a_trailing_merge_overriding_script_is_refused(self):
        bad = self._in_job(self.RULE, self.RULE + self.MERGE_SCRIPT)
        self._assert_blind_to_a_parsed_pin(bad)
        self._assert_line_refused(bad, self.MERGE_SCRIPT)

    def test_mutation_a_trailing_merge_overriding_rules_is_refused(self):
        bad = self._in_job(self.RULE, self.RULE + self.MERGE_RULES)
        self._assert_blind_to_a_parsed_pin(bad)
        self._assert_line_refused(bad, self.MERGE_RULES)

    def test_mutation_a_merge_inside_the_rule_is_refused(self):
        written = '      <<: {if: "$CI_COMMIT_BRANCH"}\n'
        bad = self._in_job(self.RULE, self.RULE + written)
        self._assert_blind_to_a_parsed_pin(bad)
        self._assert_line_refused(bad, written)

    def test_mutation_a_leading_merge_is_refused(self):
        bad = self._in_job(self.STAGE, self.MERGE_SCRIPT + self.STAGE)
        self._assert_blind_to_a_parsed_pin(bad)
        self._assert_line_refused(bad, self.MERGE_SCRIPT)

    def test_mutation_an_additive_merge_is_refused_twice(self):
        written = "  <<: {allow_failure: true}\n"
        bad = self._in_job(self.STAGE, written + self.STAGE)
        self.assertIs(yaml.safe_load(bad)[RELEASE_GATE_JOB]["allow_failure"], True)
        self._assert_line_refused(bad, written)
        self._assert_ci_refused(bad, "must have exactly the keys")

    def test_mutation_a_quoted_or_tagged_merge_is_refused(self):
        for written in ('  "<<": {script: ["exit 0"]}\n', "  '<<': {script: ['exit 0']}\n",
                        '  "\\x3c\\x3c": {script: ["exit 0"]}\n', '  !!merge x: {script: ["exit 0"]}\n'):
            with self.subTest(written):
                self._assert_line_refused(self._in_job(self.RULE, self.RULE + written), written)

    def test_mutation_an_alias_merge_outside_the_pinned_jobs_is_refused(self):
        written = "  <<: *lint\n"
        bad = self._in_file("markdown-links:\n", "markdown-links: &lint\n")
        bad = bad.replace("verify-knowledge-drift:\n", f"verify-knowledge-drift:\n{written}", 1)
        self.assertNotEqual(bad.count(written), 0)
        self._assert_line_refused(bad, written)

    def test_a_recursive_alias_ends(self):
        """In a child, with a time limit and a memory cap: without the walker's `seen` this loops and its stack grows
        without bound. That took a devcontainer down during T741's mutation run, so a lost guard must fail, not hang."""
        code = ("import resource\n"
                "_, hard = resource.getrlimit(resource.RLIMIT_AS)\n"
                "cap = 2 * 1024 ** 3 if hard == resource.RLIM_INFINITY else min(hard, 2 * 1024 ** 3)\n"
                "resource.setrlimit(resource.RLIMIT_AS, (cap, hard))\n"
                "from tests.functional.test_ci_hash_pins import merge_key_lines\n"
                "print(merge_key_lines('a: &x\\n  b: *x\\n'))\n")
        run = subprocess.run([sys.executable, "-c", code], cwd=repo_root(), capture_output=True, text=True, timeout=60,
                             check=False)
        self.assertEqual((run.returncode, run.stdout.strip()), (0, "[]"), run.stderr[-500:])


class TestCiKeySpellings(_CiMutations):
    """T741 (SEC-T741-09). The symbol and tag routes were run through GitLab's CI lint, which reads the key by its text.
    `_assert_spelling_refused` first proves that a check of parsed values alone still sees the real job."""

    GATE = "  stage: release\n  script: [\"exit 0\"]\n  rules:\n    - when: always\n"

    def _assert_spelling_refused(self, bad: str, expected: str) -> None:
        self.assertEqual(release_gate_job_problems(bad), [])
        self._assert_ci_refused(bad, expected)

    def test_mutation_a_job_spelled_as_a_symbol_is_refused(self):
        self._assert_spelling_refused(f"{self.ci}\n:release-docs-gate:\n{self.GATE}", "starting with a colon")

    def test_mutation_a_job_spelled_with_a_tag_is_refused(self):
        self._assert_spelling_refused(f"{self.ci}\n!!null release-docs-gate:\n{self.GATE}", "the explicit tag")

    def test_mutation_a_binary_merge_key_is_refused(self):
        bad = f"{self.ci}\n!!binary PDw=:\n  release-docs-gate:\n    stage: release\n    script: [a]\n"
        self.assertEqual(merge_key_lines(bad), [])
        self._assert_spelling_refused(bad, "the explicit tag")

    def test_mutation_a_refused_top_level_key_in_another_spelling_is_refused(self):
        for name, text, expected in (("symbol", ":include: ci/x.yml\n", "starting with a colon"),
                                     ("binary", "!!binary aW5jbHVkZQ==: ci/x.yml\n", "the explicit tag"),
                                     ("symbol variables", ":variables: {PYTHONPATH: x}\n", "starting with a colon")):
            with self.subTest(name):
                self._assert_spelling_refused(text + self.ci, expected)

    def test_mutation_a_job_key_as_a_symbol_is_refused(self):
        for key in (":artifacts: {paths: [scripts/]}", ":image: evil:latest", ":variables: {CI_COMMIT_BRANCH: y}"):
            with self.subTest(key):
                self._assert_ci_refused(f"x:\n  script: [a]\n  {key}\n{self.ci}", "starting with a colon")

    def test_mutation_a_key_that_is_not_a_string_is_refused(self):
        for key in ("1", "on", "~", "2026-01-01"):
            with self.subTest(key):
                self._assert_ci_refused(f"{key}: x\n{self.ci}", "a key must be a string")

    def test_a_colon_that_is_not_a_plain_scalar_is_left_alone(self):
        """Control: quoted and block text stays text in both parsers."""
        self.assertEqual(spelling_problems('j:\n  script:\n    - ": x"\n    - |\n      :x\n'), [])
        self.assertEqual(spelling_problems(self.ci), [])


class TestCiPredefinedVariables(_CiMutations):
    """T741 (SEC-T741-10). GitLab's dry run on a tag runs a job that sets its own `CI_COMMIT_BRANCH`."""

    JOB = "x:\n  stage: test\n  script: [a]\n  artifacts: {paths: [scripts/]}\n  rules:\n    - if: $CI_COMMIT_BRANCH\n"

    def test_the_condition_alone_passes_this_job(self):
        """Control: without the variable, this job is one of the artifact jobs the rule pin allows."""
        self.assertEqual(ci_pin_problems(self.JOB + self.ci), [])

    def test_mutation_a_job_setting_its_own_condition_is_refused(self):
        for name in ("CI_COMMIT_BRANCH", "CI_PIPELINE_SOURCE"):
            with self.subTest(name):
                self._assert_ci_refused(f"{self.JOB}  variables: {{{name}: y}}\n{self.ci}", f"the variable {name}")

    def test_mutation_a_matrix_or_hidden_job_setting_it_is_refused(self):
        matrix = f"{self.JOB}  parallel:\n    matrix:\n      - CI_COMMIT_BRANCH: [y]\n{self.ci}"
        self._assert_ci_refused(matrix, "the variable CI_COMMIT_BRANCH")
        hidden = f".x:\n  variables: {{CI_COMMIT_BRANCH: y}}\n{self.ci}"
        self._assert_ci_refused(hidden, ".x: the variable CI_COMMIT_BRANCH")

    def test_another_variable_is_left_alone(self):
        self.assertEqual(ci_pin_problems(f"{self.JOB}  variables: {{DOCKER_HOST: y}}\n{self.ci}"), [])


class TestCiTagJobPins(_CiMutations):
    """T741 (SEC-T741-02, -04): `release` and the drift gate from parsed values, as an allowlist, and all three
    images."""

    NEEDS = '  needs: ["release-docs-gate", "main-develop-drift-gate"]\n'
    IMAGE = re.compile(r"  image: (python:3\.12-alpine@sha256:[0-9a-f]{64})\n")

    def test_the_pipeline_as_it_is_passes_every_pin(self):
        self.assertEqual(ci_pin_problems(self.ci), [])

    def test_mutation_softening_keys_on_both_jobs_are_refused(self):
        for job in (DRIFT_GATE_JOB, RELEASE_JOB):
            for added in ("  allow_failure: true\n", "  when: manual\n", "  when: always\n", "  retry: 2\n"):
                with self.subTest(job=job, added=added):
                    self._assert_ci_refused(self._mutated_job(self.STAGE, self.STAGE + added, job), "exactly the keys")
            for added in ("      allow_failure: true\n", "      when: manual\n", "      when: always\n"):
                with self.subTest(job=job, rule=added):
                    self._assert_ci_refused(self._mutated_job(self.RULE, self.RULE + added, job), "exactly this rules")

    def test_mutation_a_key_dropped_from_a_job_is_refused(self):
        """The keys are an equality: `artifacts` has no exact value, so only this check sees it go."""
        block = "  artifacts:\n    paths:\n      - CHANGELOG.md\n    expire_in: never\n"
        self._assert_ci_refused(self._mutated_job(block, "", RELEASE_JOB), "exactly the keys")

    def test_mutation_needs_emptied_with_the_old_line_in_a_comment_is_refused(self):
        bad = self._mutated_job(self.NEEDS, f"  #{self.NEEDS[1:]}  needs: []\n", RELEASE_JOB)
        self.assertIn('needs: ["release-docs-gate", "main-develop-drift-gate"]', bad)
        self._assert_ci_refused(bad, "exactly this needs")

    def test_mutation_an_optional_or_missing_need_is_refused(self):
        for new in ('  needs: [{job: "release-docs-gate", optional: true}, "main-develop-drift-gate"]\n',
                    '  needs: ["main-develop-drift-gate"]\n',
                    '  needs: ["release-docs-gate", "main-develop-drift-gate", "unit-tests"]\n'):
            with self.subTest(new):
                self._assert_ci_refused(self._mutated_job(self.NEEDS, new, RELEASE_JOB), "exactly this needs")

    def test_mutation_the_job_variables_are_refused(self):
        for job, depth in ((DRIFT_GATE_JOB, "1"), (RELEASE_JOB, "0")):
            line = f'    GIT_DEPTH: "{depth}"\n'
            for new in (f'    GIT_DEPTH: "{depth}9"\n', f"{line}    PYTHONPATH: x\n"):
                with self.subTest(job=job, new=new):
                    self._assert_ci_refused(self._mutated_job(line, new, job), "exactly this variables")

    def test_mutation_the_drift_gate_commands_are_refused(self):
        tree = f"    - {DRIFT_GATE_TREE}\n"
        for name, new in (("dropped", ""), ("exit 0 before it", f"    - exit 0\n{tree}"),
                          ("softened", tree.replace("\n", " || true\n"))):
            with self.subTest(name):
                bad = self._mutated_job(tree, new, DRIFT_GATE_JOB)
                self._assert_ci_refused(bad, "does not run the gate")
        before = f"    - {DRIFT_GATE_APK}\n"
        bad = self._mutated_job(before, f"{before}    - exit 0\n", DRIFT_GATE_JOB)
        self._assert_ci_refused(bad, "exactly this before_script")

    def test_mutation_another_image_form_is_refused_on_each_tag_job(self):
        forms = {"a tag with a comment": "  image: evil:latest # x\n",
                 "a flow mapping": "  image: {name: evil:latest}\n",
                 "a block mapping": "  image:\n    name: evil:latest\n", "a digest on a foreign name":
                 f"  image: evil:latest@sha256:{'0' * 64}\n", "a mapping with the pinned value": None}
        for job in PINNED_JOBS:
            old = self.IMAGE.search(re.search(rf"(?ms)^{re.escape(job)}:\n.*?(?=^\S|\Z)", self.ci)[0])
            forms["a mapping with the pinned value"] = f"  image: {{name: {old[1]}}}\n"
            forms["the pinned value with text after it"] = f"  image: {old[1]}x\n"
            for name, new in forms.items():
                with self.subTest(job=job, form=name):
                    self._assert_ci_refused(self._mutated_job(old[0], new, job), f"{job} must have an image string")

    def test_mutation_an_image_form_on_any_job_or_default_is_seen_by_the_digest_walk(self):
        old = f"  image: {dict(ci_images(self.ci))['unit-tests']}\n"
        forms = {"  image: evil:latest # x\n": "unit-tests: image must be",
                 "  image: {name: evil:latest}\n": "unit-tests: image must be",
                 "  image:\n    name: evil:latest\n": "unit-tests: image must be"}
        for new, expected in forms.items():
            with self.subTest(new):
                bad = self._mutated_job(old, new, "unit-tests")
                self.assertTrue(any(expected in p for p in image_pin_problems(bad)), image_pin_problems(bad))
                self.assertTrue(eol_image_problems(bad))
                self._assert_ci_refused(bad, expected)
        bad = self._mutated_job(old, old.replace("\n", "x\n"), "unit-tests")
        self._assert_ci_refused(bad, "unit-tests: image must be")
        default = f"  image: {dict(ci_images(self.ci))['default']}\n"
        bad = self._in_file(default, "  image: {name: evil:latest}\n")
        self.assertTrue(any("default: image must be" in p for p in image_pin_problems(bad)))
        self.assertTrue(any("the file level: image must be" in p for p in image_pin_problems("image: evil:latest\n")))


class TestCiGateCredentialsAndCheckout(_CiMutations):
    """T744, T750 (SEC-T745-01, -04, -05, -07; SEC-T741-17). No merge request pipeline runs the three tag jobs, so this and
    the lint's dry run are all that guards these lines until a tag pipeline: a release candidate would prove them first."""

    REMOVE = f"    - {RELEASE_GATE_REMOVE}\n"
    INSTALL = f"    - '{RELEASE_GATE_INSTALL}'\n"
    CLONE = "    GIT_STRATEGY: clone\n"
    TIMEOUT = f"  timeout: {RELEASE_GATE_TIMEOUT}\n"
    FETCHES = [f"    - {line}\n" for line in DRIFT_GATE_FETCHES]
    DRIFT_LINES = (f"    - {DRIFT_GATE_DRIFT}\n", f"    - {DRIFT_GATE_TREE}\n")

    def _assert_before_script_refused(self, old: str, new: str) -> None:
        self._assert_ci_refused(self._mutated_job(old, new), "exactly this before_script")

    def test_the_removal_opens_the_before_script(self):
        job = yaml.safe_load(self.ci)[RELEASE_GATE_JOB]
        self.assertEqual(job["before_script"], [RELEASE_GATE_REMOVE, RELEASE_GATE_INSTALL])

    def test_mutation_another_form_of_the_removal_is_refused(self):
        for name, old, new in (("dropped", self.REMOVE, ""),
                               ("only a comment", self.REMOVE, f"    # {self.REMOVE.strip()}\n"),
                               ("softened", self.REMOVE, self.REMOVE.replace("\n", " || true\n")),
                               ("not the runner's directory", self.REMOVE, "    - rm -rf .git\n"),
                               ("not .git", self.REMOVE, '    - rm -rf "${CI_PROJECT_DIR}.tmp"\n')):
            with self.subTest(name):
                self._assert_before_script_refused(old, new)
        bad = self._mutated_job(self.REMOVE, "")
        self.assertEqual(bad.count(self.INSTALL), 1)
        self._assert_ci_refused(bad.replace(self.INSTALL, self.INSTALL + self.REMOVE), "exactly this before_script")

    def test_the_removal_clears_the_credential_files_in_a_shell(self):
        """Synthetic files, laid out as GitLab Runner 19.5.2 does, in `sh -e` as the runner's script runs. It succeeds with
        neither directory there too, because a runner may lay them out differently."""
        command = f"set -e; {yaml.safe_load(self.ci)[RELEASE_GATE_JOB]['before_script'][0]}; ls -A .; ls -A .."
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            (project / ".git").mkdir(parents=True)
            (project / ".git/config").write_text("[include]\n", encoding="utf-8")
            (project / "README.md").write_text("kept\n", encoding="utf-8")
            credential = Path(f"{project}.tmp") / ".gitlab-runner.ext.conf"
            credential.parent.mkdir()
            credential.write_text("synthetic\n", encoding="utf-8")
            for _ in range(2):  # the second time with nothing left to remove
                run = subprocess.run(["sh", "-c", command], cwd=project, env={"PATH": "/usr/bin:/bin", "CI_PROJECT_DIR": str(project)},
                                     capture_output=True, text=True, timeout=30, check=False)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stdout.split(), ["README.md", "project"])

    def test_every_line_of_the_docs_gate_runs_without_a_kept_variable(self):
        job = yaml.safe_load(self.ci)[RELEASE_GATE_JOB]
        for line in (job["before_script"][1], *job["script"]):
            self.assertTrue(line.startswith(f"{RUN_ALLOWLISTED} -- "), line)
        scripts = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in
                            ("scripts/verify-release-docs.py", "scripts/check-version-consistency.py"))
        self.assertNotRegex(scripts, r"os\.environ|getenv")  # the gate reads no variable, so it loses none

    def test_nothing_in_the_docs_gate_starts_git(self):
        """`rm -rf .git` rests on this. The version check is the gate's only child process."""
        for path in ("scripts/verify-release-docs.py", "scripts/check-version-consistency.py"):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"""["']git["']""", path)
            self.assertNotRegex(text, r"os\.(system|popen|exec|spawn)", path)
        gate = (ROOT / "scripts/verify-release-docs.py").read_text(encoding="utf-8")
        self.assertEqual(gate.count("subprocess.run("), 1)
        self.assertNotIn("subprocess", (ROOT / "scripts/check-version-consistency.py").read_text(encoding="utf-8"))

    def test_mutation_a_line_without_the_allowlist_or_with_a_kept_variable_is_refused(self):
        wrapped = f"{RUN_ALLOWLISTED} -- "
        for job, field, old in ((RELEASE_GATE_JOB, "before_script", self.INSTALL), (RELEASE_GATE_JOB, "does not run", self.SCRIPT),
                                (DRIFT_GATE_JOB, "before_script", f"    - {DRIFT_GATE_APK}\n"),
                                (DRIFT_GATE_JOB, "does not run", self.DRIFT_LINES[0]),
                                (DRIFT_GATE_JOB, "does not run", self.DRIFT_LINES[1])):
            for name, new in (("no allowlist", old.replace(wrapped, "")),
                              ("a token kept", old.replace(wrapped, f"{KEEP_JOB_TOKEN} "))):
                with self.subTest(job=job, line=old, form=name):
                    self._assert_ci_refused(self._mutated_job(old, new, job), field)

    def test_mutation_the_fetches_are_refused(self):
        for old in self.FETCHES:
            for name, new in (("no allowlist", old.replace(f"{KEEP_JOB_TOKEN} ", "")),
                              ("no token", old.replace(KEEP_JOB_TOKEN, f"{RUN_ALLOWLISTED} --")),
                              ("another name kept", old.replace("CI_JOB_TOKEN", "WIKI_TOKEN")),
                              ("a second name kept", old.replace("--keep CI_JOB_TOKEN", "--keep CI_JOB_TOKEN --keep WIKI_TOKEN"))):
                with self.subTest(line=old, form=name):
                    self._assert_ci_refused(self._mutated_job(old, new, DRIFT_GATE_JOB), "does not run the gate")

    def test_mutation_another_timeout_is_refused(self):
        for new in ("  timeout: 3 hours\n", "  timeout: 11 minutes\n", "  timeout: 1h\n"):
            with self.subTest(new):
                self._assert_ci_refused(self._mutated_job(self.TIMEOUT, new), "exactly this timeout")
        self._assert_ci_refused(self._mutated_job(self.TIMEOUT, ""), "exactly the keys")
        for job in (DRIFT_GATE_JOB, RELEASE_JOB):  # the other two have no such key: the keys are an equality
            with self.subTest(job):
                self._assert_ci_refused(self._mutated_job(self.STAGE, self.STAGE + self.TIMEOUT, job), "exactly the keys")

    def test_the_old_names_are_gone(self):
        self.assertNotIn("ANTHROPIC_API_KEY", self.ci)
        self.assertNotIn("unset ", "\n".join(ci_command_lines(self.ci)))

    def test_mutation_another_git_strategy_is_refused_on_each_tag_job(self):
        for job in PINNED_JOBS:
            for new in ("    GIT_STRATEGY: fetch\n", "    GIT_STRATEGY: none\n", "    GIT_STRATEGY: empty\n",
                        f"{self.CLONE}    GIT_CLEAN_FLAGS: none\n"):
                with self.subTest(job=job, new=new):
                    self._assert_ci_refused(self._mutated_job(self.CLONE, new, job), "exactly this variables")
        for job in (DRIFT_GATE_JOB, RELEASE_JOB):
            self._assert_ci_refused(self._mutated_job(self.CLONE, "", job), "exactly this variables")
        for name in ("exactly the keys", "exactly this variables"):
            with self.subTest(name):
                self._assert_ci_refused(self._mutated_job(f"  variables:\n{self.CLONE}", ""), name)

    def test_control_a_clone_keeps_the_commands_the_drift_gate_fetches_with(self):
        """Two runner paths: GitLab Runner's shells/abstract.go, read 2026-11-06. `clone` removes the directory and then
        takes the same `git init`, `git remote add origin`, `git fetch` as `fetch`; the native clone flag sets the same
        refspec. Neither is a tag pipeline: this shows the commands, on a local repository, resolve `origin/main`."""
        with tempfile.TemporaryDirectory() as tmp:
            origin, work, job_dir = Path(tmp) / "o.git", Path(tmp) / "w", Path(tmp) / "job"

            def git(cwd: Path, *args: str) -> str:
                return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=60, check=True).stdout

            for path, kind in ((origin, ["--bare"]), (work, []), (job_dir, [])):
                git(Path(tmp), "init", "-q", "-b", "main", *kind, str(path))
            git(work, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "c")
            git(work, "push", "-q", origin.as_uri(), "main", "main:develop", "main:refs/tags/v1.0.0")
            git(job_dir, "remote", "add", "origin", origin.as_uri())
            git(job_dir, "fetch", "-q", "--depth=1", "origin", "+refs/tags/v1.0.0:refs/tags/v1.0.0")
            self.assertEqual(git(job_dir, "for-each-ref", "refs/remotes"), "")  # nothing yet, so the next lines must do it
            for line in yaml.safe_load(self.ci)[DRIFT_GATE_JOB]["script"][:2]:
                command = shlex.split(line.removeprefix(f"{KEEP_JOB_TOKEN} "))
                self.assertEqual(command[0], "git")
                git(job_dir, *command[1:])
            for ref in ("origin/main", "origin/develop", "v1.0.0"):
                self.assertTrue(git(job_dir, "rev-parse", "--verify", ref).strip(), ref)


class TestCiReleaseJobAndDefaultValues(_CiMutations):
    """T744 (SEC-T741-12). Parsed values, so a comment holding the old line satisfies nothing. The script line lives here
    and in the CI file on purpose: changing either fails this until the two agree."""

    LINE = f"    - {RELEASE_COMMAND}\n"
    PATHS = "      - CHANGELOG.md\n"
    EXPIRE = "    expire_in: never\n"
    TAGS = "  tags:\n    - docker\n"
    INTERRUPTIBLE = "  interruptible: true\n"

    def test_mutation_another_release_script_is_refused(self):
        forms = {"exit 0 first": f"    - exit 0\n{self.LINE}", "a line after it": f"{self.LINE}    - echo done\n",
                 "softened": self.LINE.replace("\n", " || true\n"), "only a comment": f"    # {self.LINE.strip()}\n    - exit 0\n",
                 "another credential": self.LINE.replace("--token-env CI_JOB_TOKEN", "--token-env WIKI_TOKEN"),
                 "another host check": self.LINE.replace("${CI_SERVER_HOST}", "evil.example")}
        for name, new in forms.items():
            with self.subTest(name):
                self._assert_ci_refused(self._mutated_job(self.LINE, new, RELEASE_JOB), "does not run the gate as pinned")

    def test_mutation_other_release_artifacts_are_refused(self):
        for old, new in ((self.PATHS, f"{self.PATHS}      - scripts/\n"), (self.PATHS, "      - scripts/\n"),
                         (self.EXPIRE, "    expire_in: 1 day\n"), (self.EXPIRE, f"{self.EXPIRE}    when: always\n"),
                         (self.EXPIRE, f"{self.EXPIRE}    public: true\n"), (self.EXPIRE, "")):
            with self.subTest(new):
                self._assert_ci_refused(self._mutated_job(old, new, RELEASE_JOB), "exactly this artifacts")

    def test_mutation_other_default_tags_are_refused(self):
        for new in ("  tags:\n    - dind\n", f"{self.TAGS}    - dind\n", "  tags: []\n", "  tags: docker\n"):
            with self.subTest(new):
                self._assert_ci_refused(self._in_file(self.TAGS, new), "default.tags must be exactly")

    def test_mutation_another_default_interruptible_is_refused(self):
        for new in ("  interruptible: false\n", "  interruptible: 1\n", '  interruptible: "true"\n', "  interruptible:\n"):
            with self.subTest(new):
                self._assert_ci_refused(self._in_file(self.INTERRUPTIBLE, new), "default.interruptible must be exactly true")


class TestCiReleaseGateRunnerTag(_CiMutations):
    """T810 (SEC-T741-17, plan-159): the three tag jobs run on the dedicated runner, and nothing else names its tag.
    Only a tag pipeline proves the routing; these pin the file that GitLab reads."""

    TAG_LINE = '  tags: ["release-gate"]\n'
    TAG_JOBS = (RELEASE_GATE_JOB, DRIFT_GATE_JOB, RELEASE_JOB)
    UNIT_TAGS = "  tags:\n    - dind"
    DEFAULT_TAGS_TEXT = "  tags:\n    - docker\n"
    BRANCH_RULES = "  script: [a]\n  rules:\n    - if: $CI_COMMIT_BRANCH\n"

    def test_exactly_the_three_tag_jobs_carry_the_tag(self):
        ci = yaml.safe_load(self.ci)
        carriers = sorted(name for name, job in ci.items() if isinstance(job, dict) and RELEASE_GATE_TAG in strings_in(job.get("tags")))
        self.assertEqual(carriers, sorted(self.TAG_JOBS))
        self.assertEqual(ci["default"]["tags"], DEFAULT_TAGS)
        self.assertEqual(runner_tag_problems(ci), [])

    def test_mutation_a_tag_job_without_the_tag_is_refused(self):
        for job in self.TAG_JOBS:
            with self.subTest(job=job, form="dropped"):
                bad = self._mutated_job(self.TAG_LINE, "", job)
                self._assert_ci_refused(bad, "exactly the keys")
                self._assert_ci_refused(bad, "exactly this tags")
            for new in ('  tags: ["docker"]\n', "  tags: []\n", '  tags: ["release-gate-x"]\n'):
                with self.subTest(job=job, new=new):
                    self._assert_ci_refused(self._mutated_job(self.TAG_LINE, new, job), "exactly this tags")

    def test_mutation_a_tag_job_with_an_extra_tag_is_refused(self):
        for job in self.TAG_JOBS:
            for new in ('  tags: ["release-gate", "docker"]\n', '  tags: ["dind", "release-gate"]\n',
                        "  tags:\n    - release-gate\n    - release-gate\n", "  tags: release-gate\n"):
                with self.subTest(job=job, new=new):
                    self._assert_ci_refused(self._mutated_job(self.TAG_LINE, new, job), "exactly this tags")

    def test_mutation_a_branch_job_with_the_tag_is_refused(self):
        forms = {
            "unit-tests, a second tag": self._mutated_job(self.UNIT_TAGS, "  tags:\n    - release-gate\n    - dind", "unit-tests"),
            "unit-tests, only the tag": self._mutated_job(self.UNIT_TAGS, "  tags:\n    - release-gate", "unit-tests"),
            "markdown-links, an added tags": self._mutated_job("  stage: lint\n", "  stage: lint\n" + self.TAG_LINE, "markdown-links"),
            "a hidden job": self.ci + "\n.gate-runner:\n" + self.TAG_LINE,
            "a branch job added": self.ci + "\nlater-job:\n" + self.TAG_LINE + self.BRANCH_RULES,
            "default": self._in_file(self.DEFAULT_TAGS_TEXT, self.DEFAULT_TAGS_TEXT + "    - release-gate\n"),
            "a variable holding it": self._mutated_job(self.UNIT_TAGS, "  tags:\n    - $GATE\n    - dind", "unit-tests")
                                     .replace("    DOCKER_HOST:", "    GATE: release-gate\n    DOCKER_HOST:", 1),
        }
        for name, bad in forms.items():
            with self.subTest(name):
                self._assert_ci_refused(bad, "names release-gate: only the three tag jobs may")

    def test_mutation_a_variable_in_another_jobs_tags_is_refused(self):
        for new in ("  tags:\n    - $RUNNER_TAG", "  tags:\n    - ${RUNNER_TAG}", "  tags:\n    - dind-$X"):
            with self.subTest(new):
                self._assert_ci_refused(self._mutated_job(self.UNIT_TAGS, new, "unit-tests"), "a variable in tags is refused")

    def test_mutation_extending_a_tag_job_is_refused(self):
        for extends in ("release", '["release-docs-gate"]', '[".base", "main-develop-drift-gate"]'):
            with self.subTest(extends):
                bad = self.ci + f"\nlater-job:\n  extends: {extends}\n" + self.BRANCH_RULES
                self._assert_ci_refused(bad, "extends a tag job and would inherit its runner tag")


class TestCiFilePin(_CiMutations):
    """T741 (SEC-T741-03): what reaches the pinned jobs from the file level, or through artifacts in a tag pipeline."""

    UNIT = "unit-tests"
    BRANCH_RULE = "    - if: $CI_COMMIT_BRANCH\n"

    def test_mutation_a_refused_top_level_key_is_refused(self):
        values = {"include": "include: ci/x.yml\n", "workflow": "workflow:\n  rules:\n    - when: always\n",
                  "spec": "spec:\n  inputs:\n    a:\n      default: b\n", "image": "image: evil:latest\n",
                  "services": "services:\n  - redis:7\n", "cache": "cache:\n  paths: [x]\n",
                  "before_script": "before_script:\n  - exit 0\n", "after_script": "after_script:\n  - echo done\n"}
        self.assertEqual(set(values), set(REFUSED_TOP_LEVEL))
        for key, text in values.items():
            with self.subTest(key):
                bad = text + self.ci
                self.assertIn(key, yaml.safe_load(bad))
                self._assert_ci_refused(bad, f"the top-level key {key} is refused")

    def test_mutation_a_file_that_is_not_one_plain_document_is_refused(self):
        spec_header = "spec:\n  inputs:\n    a:\n      default: b\n---\n" + self.ci
        self._assert_ci_refused(spec_header, "does not load as one plain document")
        reference = self._in_job(self.STAGE, f"{self.STAGE}  allow_failure: !reference [.x, y]\n")
        self._assert_ci_refused(reference, "does not load as one plain document")
        for text in ("", "- a\n"):
            with self.subTest(text):
                self.assertEqual(ci_pin_problems(text),
                                 ["the CI file does not load as one plain document: it is not a mapping"])

    def test_mutation_the_top_level_variables_are_refused(self):
        line = '  GIT_DEPTH: "20"\n'
        for new in (f"{line}  PYTHONPATH: x\n", '  GIT_DEPTH: "1"\n'):
            with self.subTest(new):
                self._assert_ci_refused(self._in_file(line, new), "the top-level variables must be exactly")

    def test_mutation_the_stages_are_refused(self):
        old = "  - wiki-sync\n  - release\n"
        for new in ("  - release\n  - wiki-sync\n", f"{old}  - later\n", "  - wiki-sync\n"):
            with self.subTest(new):
                self._assert_ci_refused(self._in_file(old, new), "the stages must be exactly")

    def test_mutation_another_key_in_default_is_refused(self):
        old = "  interruptible: true\n"
        for new in (f"{old}  after_script:\n    - echo done\n", f"{old}  hooks:\n    pre_get_sources_script: exit 0\n",
                    f"{old}  retry: 2\n", ""):
            with self.subTest(new):
                self._assert_ci_refused(self._in_file(old, new), "default must hold exactly")

    def test_mutation_a_job_that_could_run_on_a_tag_is_refused(self):
        tag_rule = "    - if: $CI_COMMIT_TAG\n"
        for name, new in (("a tag rule", tag_rule), ("a rule beside the others", f"{self.BRANCH_RULE}{tag_rule}"),
                          ("no if", "    - when: always\n"),
                          ("the if is widened", "    - if: $CI_COMMIT_BRANCH || $CI_COMMIT_TAG\n")):
            with self.subTest(name):
                bad = self._mutated_job(self.BRANCH_RULE, new, self.UNIT)
                self._assert_ci_refused(bad, "could run in a tag pipeline")

    def test_mutation_a_job_without_rules_is_refused_whatever_it_does(self):
        """SEC-T741-11, -15. GitLab's dry run on a tag runs the `pages` forms and the plain job, and shows no artifacts
        key on them: this route cannot be seen by asking what a job makes."""
        for name, text in (("artifacts", "x:\n  script: [a]\n  artifacts:\n    paths: [scripts/]\n"),
                           ("pages publish", "x:\n  script: [a]\n  pages:\n    publish: scripts\n"),
                           ("pages true", "x:\n  script: [a]\n  pages: true\n"),
                           ("named pages", "pages:\n  script: [a]\n  publish: scripts\n"),
                           ("nothing at all", "x:\n  script: [a]\n"),
                           ("only", "x:\n  script: [a]\n  only: [tags]\n"),
                           ("extends", "x:\n  script: [a]\n  extends: .y\n")):
            with self.subTest(name):
                self.assertEqual(yaml.safe_load(text).keys() & set(REFUSED_TOP_LEVEL), set())
                self._assert_ci_refused(text + self.ci, "could run in a tag pipeline")

    def test_a_job_that_cannot_run_on_a_tag_is_left_alone(self):
        """Control: the rule is about where a job runs, so `pages` and `artifacts` are free on a branch."""
        rules = "  rules:\n    - if: $CI_COMMIT_BRANCH\n"
        for extra in ("", "  pages: true\n", "  artifacts:\n    paths: [x]\n", "  extends: .y\n"):
            with self.subTest(extra):
                self.assertEqual(ci_pin_problems(f"x:\n  script: [a]\n{extra}{rules}{self.ci}"), [])

    def test_a_hidden_job_is_left_alone_but_its_variables_are_not(self):
        """Control: a hidden job does not run, and a job that extends it needs its own rules."""
        self.assertEqual(ci_pin_problems(".y:\n  artifacts:\n    paths: [x]\n" + self.ci), [])
        self._assert_ci_refused(".y:\n  variables: {CI_COMMIT_BRANCH: y}\n" + self.ci, "the variable CI_COMMIT_BRANCH")


EOL_TABLE_DATE = dt.date(2026, 10, 22)  # the day the table in eol_image_problems was written
MAX_REVIEW_AGE_DAYS = 120


def review_problems(ci_text: str, today: dt.date) -> list[str]:
    """The pipeline must say when its images were last reviewed, and that date must be recent and not before the table."""
    match = re.search(r"^# ci_images_reviewed_on: (\d{4}-\d{2}-\d{2})", ci_text, re.M)
    if not match:
        return ["no `# ci_images_reviewed_on: YYYY-MM-DD` line in .gitlab-ci.yml"]
    reviewed = dt.date.fromisoformat(match.group(1))
    out = []
    if (today - reviewed).days > MAX_REVIEW_AGE_DAYS:
        out.append(f"images last reviewed {reviewed}, more than {MAX_REVIEW_AGE_DAYS} days ago: re-check the digests and "
                   f"the end-of-life table in eol_image_problems, then update both dates")
    if reviewed < EOL_TABLE_DATE:
        out.append("ci_images_reviewed_on is older than the end-of-life table")
    if reviewed > today:
        out.append("ci_images_reviewed_on is in the future")
    return out


class TestCiImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ci = CI_YML.read_text(encoding="utf-8")

    def test_no_image_is_end_of_life_and_every_image_has_a_digest(self):
        self.assertEqual(eol_image_problems(self.ci), [])

    def test_the_review_date_is_present_and_fresh(self):
        self.assertEqual(review_problems(self.ci, dt.date.today()), [])

    def test_mutation_a_stale_missing_or_future_review_date_is_detected(self):
        # The date under test is the one in the file, so bumping it needs no edit here (T765).
        reviewed = dt.date.fromisoformat(re.search(r"^# ci_images_reviewed_on: (\S+)", self.ci, re.M).group(1))
        self.assertEqual(review_problems(self.ci, reviewed + dt.timedelta(days=120)), [])
        self.assertTrue(review_problems(self.ci, reviewed + dt.timedelta(days=121)))
        self.assertTrue(review_problems(self.ci.replace("ci_images_reviewed_on", "reviewed"), reviewed))
        self.assertTrue(review_problems(self.ci, reviewed - dt.timedelta(days=1)))
        self.assertTrue(review_problems(self.ci.replace(f"{reviewed}   (tests", "2026-01-01   (tests"), reviewed))

    def test_the_bases_are_the_two_supported_lines(self):
        names = {image.split("@")[0] for _, image in ci_images(self.ci)}
        self.assertEqual(names, {"node:24-alpine", "python:3.12-alpine"})

    def test_mutation_the_old_images_are_detected(self):
        bad = self.ci.replace("node:24-alpine", "node:20-alpine")
        self.assertTrue(any("Node 20" in p for p in eol_image_problems(bad)))
        bad = self.ci.replace("python:3.12-alpine@", "alpine:3.20@", 1)
        self.assertTrue(any("Alpine 3.20" in p for p in eol_image_problems(bad)))
        bad = self.ci.replace("node:24-alpine", "node:23-alpine")
        self.assertTrue(any("Node 23" in p for p in eol_image_problems(bad)))

    def test_mutation_an_image_without_digest_is_detected(self):
        bad = re.sub(r"(image: node:24-alpine)@sha256:[0-9a-f]{64}", r"\1", self.ci)
        self.assertTrue(any("no digest" in p for p in eol_image_problems(bad)))


if __name__ == "__main__":
    unittest.main()
