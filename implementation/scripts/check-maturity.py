#!/usr/bin/env python3
"""Mechanically verify that a component's declared `maturity` value is earned.

Location choice (documented per task-T432 "your call, document it"): this script
lives in `implementation/scripts/`, next to `generate-registry.py` (whose
`_collect_entries()`/`_determine_source()`/`_detect_platforms()` it imports and
reuses directly, rather than re-walking `implementation/knowledge/**` with a
second, possibly-drifting definition of "the 77 registry-eligible components")
and `check.py` (whose CI gate set it is wired into via a new `--maturity`
flag). `scripts/` (top-level) holds repo-tooling scripts unrelated to the
knowledge/registry pipeline (release, CI-drift, wiki-sync, ...); this script
is registry/knowledge-pipeline-adjacent, so it follows `generate-registry.py`'s
convention, not `scripts/`'s.

For every category/transition criterion, see `docs/artifacts/
maturity-promotion-criteria-v1.md` (T431) -- this file implements each one as a
real, non-subjective check, not a re-derivation of the criteria themselves.

Interpretation notes (T431 leaves these as "your call" per its own text):
- A component claiming `stable` must still satisfy the `experimental->beta`
  bar (T431 section 3's "ALL of the above, still holding"). Criterion 1 of
  that bar ("maturity: beta set; ... passes ... test_schemas.py") is read here
  as "the component's *current* declared maturity value is schema-valid for
  its category" -- i.e. the general form of the criterion (a well-formed,
  schema-valid declaration) rather than literally requiring the string
  "beta" once a component has since been promoted past it.
- "Documented ... with >=40 non-whitespace characters of real description,
  not an incidental substring match" (criterion d for every category) is
  checked mechanically as: a line in a `docs/wiki/**/*.md` file that contains
  the component's id (or name) as a whole word, where the remainder of that
  same line (once the matched identifier itself is removed) both (a) has
  >=40 non-whitespace characters and (b) *looks like real prose*, not raw
  character padding -- see `_looks_like_real_description()` for the exact,
  dependency-free heuristic and the padding attack it was added to close
  (T432 adversarial review: a wiki line like `<id> xxxxxxxx...xxxx` with 40+
  repeated filler characters used to satisfy criterion (a) alone).
- Agent criterion (a)(iii)'s "resolves to a real, existing file/MR reference"
  is checked without any network/GitLab API call (this script must run
  offline in CI): a backtick-quoted path is verified to exist on disk; an
  MR reference matching `!<digits>` is accepted at face value.
- Deprecation Notice's `**Replacement**:` value is resolved against the set
  of all 77 real component ids (any category), since T431's wording ("id of
  the component that replaces it") does not restrict it to the same category.

Usage (from repository root):
    python3 implementation/scripts/check-maturity.py --root implementation
    python3 implementation/scripts/check-maturity.py --root implementation --verbose
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml


# ---------------------------------------------------------------------------
# Repo / registry-pipeline wiring
# ---------------------------------------------------------------------------

def _repo_root(implementation_root: Path) -> Path:
    root = implementation_root.resolve()
    for candidate in (root, *root.parents):
        if (candidate / ".gitlab-ci.yml").is_file():
            return candidate
    return root.parent


def _load_generate_registry(scripts_dir: Path):
    module_path = scripts_dir / "generate-registry.py"
    spec = importlib.util.spec_from_file_location("check_maturity_registry_gen", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load generate-registry module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def _read_frontmatter_and_body(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    frontmatter = yaml.safe_load(match.group(1)) or {}
    if not isinstance(frontmatter, dict):
        frontmatter = {}
    return frontmatter, text[match.end():]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Component:
    category: str
    id: str
    name: str
    path: Path
    maturity: str
    frontmatter: dict
    body: str


@dataclass
class Context:
    repo_root: Path
    source_root: Path
    schemas_dir: Path
    entries: list[dict]
    command_agent: dict
    agent_commands: dict
    agent_ids: set
    command_ids: set
    all_ids: set
    golden_cases: list
    active_rows: list
    completed_rows: list
    wiki_files: list
    agents_md_text: str
    other_agent_files: dict
    other_command_files: dict
    functional_test_files: list
    golden_expect_files: list


# ---------------------------------------------------------------------------
# Generic text helpers
# ---------------------------------------------------------------------------

def _mentions(text: str, ident: str) -> bool:
    pattern = r"(?<![\w-])" + re.escape(ident) + r"(?![\w-])"
    return re.search(pattern, text) is not None


_WORD_TOKEN_RE = re.compile(r"[A-Za-z0-9']+")
_REPEATED_CHAR_RUN_RE = re.compile(r"^(.)\1{2,}$")
_VOWEL_RE = re.compile(r"[aeiouAEIOU]")
_DIGITS_ONLY_RE = re.compile(r"^[0-9]+$")

_DOC_MIN_CHARS = 40      # T431's own stated floor: raw non-whitespace length
_DOC_MIN_WORDS = 6       # minimum count of word-shaped, non-degenerate tokens
_DOC_MIN_DISTINCT_WORDS = 4  # minimum count of *distinct* such tokens


def _is_real_word_token(token: str) -> bool:
    """A token counts as a "real" word toward the documentation bar if it is
    at least 2 characters (a lone letter isn't a word), is not a run of one
    character repeated three-plus times (`xxxx`, `aaaa`, ...) -- the exact
    shape of the padding attack this guards against -- and either is purely
    numeric (version numbers, counts, etc. are legitimate content) or
    contains a vowel (a cheap, dependency-free proxy for "plausibly an
    English word" that rejects consonant-mashed filler like `xqzwky`).
    """
    if len(token) < 2:
        return False
    if _REPEATED_CHAR_RUN_RE.match(token):
        return False
    if _DIGITS_ONLY_RE.match(token):
        return True
    return bool(_VOWEL_RE.search(token))


def _looks_like_real_description(remainder: str) -> bool:
    """Decide whether `remainder` (a wiki line with the matched component
    identifier stripped out) is real descriptive prose rather than padding
    engineered to clear a raw character-count threshold.

    Chosen heuristic (T432 adversarial-review follow-up): the original
    check only required >=40 non-whitespace characters on the line, with no
    check on their *shape*. That is trivially gamed by appending a single
    padded/repeated-character line to any real wiki file, e.g.
    `<component-id> xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` -- 40+ raw
    characters, zero real content, and it passed. Character-count alone
    cannot distinguish "real sentence" from "junk padding", so this adds two
    independent, still O(line-length), still dependency-free/offline gates
    on top of (not instead of) the original length floor:

    1. At least `_DOC_MIN_WORDS` word-shaped tokens (see
       `_is_real_word_token`) -- defeats a single long padded token (one
       giant "word") and defeats a single repeated-character run, since
       neither produces multiple qualifying tokens.
    2. At least `_DOC_MIN_DISTINCT_WORDS` *distinct* (case-insensitive)
       tokens among those -- defeats padding built from one word repeated
       many times (`blah blah blah blah blah blah`), which would otherwise
       satisfy gate 1 alone.

    This is intentionally a heuristic, not a semantic/dictionary check (no
    network calls or NLP dependencies are allowed in this CI-time script):
    a sufficiently deliberate adversary could still hand-craft several
    distinct, vowel-containing pseudo-words to clear both gates. That
    residual risk is accepted as out of scope for a fast, offline,
    mechanically-checkable heuristic; the bar raised here is against casual
    or single-line-padding gaming, not a determined adversary willing to
    fabricate plausible-looking prose by hand -- which starts to shade into
    "actually wrote a real description".
    """
    if len(re.sub(r"\s", "", remainder)) < _DOC_MIN_CHARS:
        return False
    tokens = _WORD_TOKEN_RE.findall(remainder)
    real_words = [t for t in tokens if _is_real_word_token(t)]
    if len(real_words) < _DOC_MIN_WORDS:
        return False
    distinct = {t.lower() for t in real_words}
    return len(distinct) >= _DOC_MIN_DISTINCT_WORDS


def _documented_in_wiki(ident: str, wiki_files: list[Path]) -> bool:
    pattern = re.compile(r"(?<![\w-])" + re.escape(ident) + r"(?![\w-])", re.IGNORECASE)
    for wiki_file in wiki_files:
        for line in wiki_file.read_text(encoding="utf-8").splitlines():
            match = pattern.search(line)
            if not match:
                continue
            remainder = line[: match.start()] + line[match.end():]
            if _looks_like_real_description(remainder):
                return True
    return False


def _agents_md_section(text: str, heading_contains: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and heading_contains in line:
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])


def _has_evidence_tag(category: str, ident: str, ctx: Context) -> bool:
    needle = f"# maturity-evidence: {category}/{ident}"
    for path in ctx.functional_test_files + ctx.golden_expect_files:
        if needle in path.read_text(encoding="utf-8"):
            return True
    return False


def _referenced_in_agents_or_commands(ident: str, ctx: Context, literal: str | None = None) -> bool:
    needle = literal or ident
    for path in list(ctx.other_agent_files.values()) + list(ctx.other_command_files.values()):
        text = path.read_text(encoding="utf-8")
        if literal is not None:
            if needle in text:
                return True
        elif _mentions(text, needle):
            return True
    return False


# ---------------------------------------------------------------------------
# `## Rails` (criterion b, all categories, all tiers from beta up)
# ---------------------------------------------------------------------------

RAILS_HEADING_RE = re.compile(r"^(#{2,3})\s*Rails\s*$", re.MULTILINE)
RAILS_LABELS = ("Inputs", "Out of scope", "Failure mode")


def _find_labeled_section(body: str, heading_re: re.Pattern) -> str | None:
    match = heading_re.search(body)
    if not match:
        return None
    level = len(match.group(1))
    next_heading = re.compile(rf"^#{{1,{level}}}\s+\S", re.MULTILINE)
    next_match = next_heading.search(body, match.end())
    end = next_match.start() if next_match else len(body)
    return body[match.end():end]


LABEL_LINE_RE = re.compile(r"^\*\*[^*]+\*\*:")


def _label_has_content(section: str, label: str) -> bool:
    pattern = re.compile(rf"\*\*{re.escape(label)}\*\*:[ \t]*(.*)")
    match = pattern.search(section)
    if not match:
        return False
    if match.group(1).strip():
        return True
    rest_lines = section[match.end():].splitlines()
    if not rest_lines:
        return False
    next_line = rest_lines[0].strip()
    return bool(next_line) and not LABEL_LINE_RE.match(next_line)


def _rails_check(body: str) -> str | None:
    section = _find_labeled_section(body, RAILS_HEADING_RE)
    if section is None:
        return "missing a `## Rails` (or `### Rails`) heading"
    missing = [label for label in RAILS_LABELS if not _label_has_content(section, label)]
    if missing:
        joined = ", ".join(f"**{m}**:" for m in missing)
        return f"`## Rails` section missing non-empty label(s): {joined}"
    return None


# ---------------------------------------------------------------------------
# `## Deprecation Notice` (section 4, universal, all categories)
# ---------------------------------------------------------------------------

DEPRECATION_HEADING_RE = re.compile(r"^(#{2,3})\s*Deprecation Notice\s*$", re.MULTILINE)
VERSION_RE = re.compile(r"v?\d+\.\d+\.\d+")


def _first_token(text: str) -> str:
    parts = text.strip().split()
    if not parts:
        return ""
    return parts[0].strip("`,.()")


def _deprecation_check(maturity: str, body: str, known_ids: set) -> str | None:
    section = _find_labeled_section(body, DEPRECATION_HEADING_RE)
    if maturity != "deprecated":
        if section is not None:
            return "has a `## Deprecation Notice` section but maturity is not `deprecated`"
        return None
    if section is None:
        return "maturity: deprecated but no `## Deprecation Notice` section is present"
    if not _label_has_content(section, "Reason"):
        return "`## Deprecation Notice` is missing a non-empty **Reason**:"
    replacement = re.search(r"\*\*Replacement\*\*:[ \t]*(\S.*)", section)
    removal = re.search(r"\*\*Removal target\*\*:[ \t]*(\S.*)", section)
    if replacement and _first_token(replacement.group(1)) in known_ids:
        return None
    if removal and VERSION_RE.search(removal.group(1)):
        return None
    return (
        "`## Deprecation Notice` needs a **Replacement**: that resolves to a real "
        "component id, or a version-shaped **Removal target**:"
    )


# ---------------------------------------------------------------------------
# Schema validity (criterion 1, all categories)
# ---------------------------------------------------------------------------

def _schema_check(category: str, frontmatter: dict, schemas_dir: Path) -> str | None:
    schema_path = schemas_dir / f"{category}.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(frontmatter, schema)
    except jsonschema.ValidationError as exc:
        return f"frontmatter fails {schema_path.name}: {exc.message}"
    return None


# ---------------------------------------------------------------------------
# Shared defect-check definition (section 3.5)
# ---------------------------------------------------------------------------

def _ledger_defect(ident: str, priorities: set, ctx: Context) -> str | None:
    for row in ctx.active_rows:
        if row["priority"] not in priorities:
            continue
        if row["status"] in ("done", "cancelled"):
            continue
        if _mentions(row["title"], ident):
            return f"open {row['priority']} task {row['id']} names it in its Title"
        brief = ctx.repo_root / "docs" / "tasks" / f"task-{row['id']}.md"
        if brief.is_file() and _mentions(brief.read_text(encoding="utf-8"), ident):
            return f"open {row['priority']} task {row['id']} names it in its brief"
    return None


def _golden_tracked_defect(owned_commands: list, ctx: Context) -> str | None:
    for case in ctx.golden_cases:
        if case.get("status") != "known_failing":
            continue
        if case.get("known_failing_category") != "tracked_defect":
            continue
        command = str(case.get("command", "")).lstrip("/")
        if command in owned_commands:
            return f"golden case {case.get('id')} is a known_failing tracked_defect for /{command}"
    return None


def _open_defect(category: str, ident: str, ctx: Context, include_p1: bool) -> str | None:
    priorities = {"P0", "P1"} if include_p1 else {"P0"}
    ledger_hit = _ledger_defect(ident, priorities, ctx)
    if ledger_hit:
        return ledger_hit
    owned_commands: list = []
    if category == "command":
        owned_commands = [ident]
    elif category == "agent":
        owned_commands = ctx.agent_commands.get(ident, [])
    if owned_commands:
        return _golden_tracked_defect(owned_commands, ctx)
    return None


# ---------------------------------------------------------------------------
# Generic beta-tier checkers (component, ctx) -> str | None
# ---------------------------------------------------------------------------

def _check_schema(component: Component, ctx: Context) -> str | None:
    return _schema_check(component.category, component.frontmatter, ctx.schemas_dir)


def _check_rails(component: Component, ctx: Context) -> str | None:
    return _rails_check(component.body)


def _check_no_p0_defect(component: Component, ctx: Context) -> str | None:
    return _open_defect(component.category, component.id, ctx, False)


def _check_no_p0_p1_defect(component: Component, ctx: Context) -> str | None:
    return _open_defect(component.category, component.id, ctx, True)


BETA_CRITERIA = (
    ("1", "maturity value is schema-valid for its category", _check_schema),
    ("2", "`## Rails` present with Inputs/Out of scope/Failure mode", _check_rails),
    ("3", "no open P0 defect", _check_no_p0_defect),
)


# ---------------------------------------------------------------------------
# Documented-in-wiki (criterion d, all categories, shared shape)
# ---------------------------------------------------------------------------

DOC_SECTION = {"agent": "3.1.6", "command": "3.2.6", "instruction": "3.3.6", "skill": "3.4.6"}


def _documented_check(category: str, ident: str, name: str, ctx: Context) -> str | None:
    if _documented_in_wiki(ident, ctx.wiki_files):
        return None
    if name and name != ident and _documented_in_wiki(name, ctx.wiki_files):
        return None
    section = DOC_SECTION[category]
    return f"not documented in docs/wiki/** with >=40 non-whitespace chars of real description (S{section})"


# ---------------------------------------------------------------------------
# `agent` stable-tier checkers (section 3.1)
# ---------------------------------------------------------------------------

ARTIFACT_PATH_RE = re.compile(r"`([^`]+)`")
MR_REF_RE = re.compile(r"!\d+")


def _resolves_to_artifact(outcome: str, repo_root: Path) -> bool:
    for candidate in ARTIFACT_PATH_RE.findall(outcome):
        if (repo_root / candidate).exists():
            return True
    return bool(MR_REF_RE.search(outcome))


def _agent_evidence_check(component: Component, ctx: Context) -> str | None:
    ident = component.id
    owned = ctx.agent_commands.get(ident, [])
    for case in ctx.golden_cases:
        if str(case.get("command", "")).lstrip("/") in owned:
            return None
    if _has_evidence_tag("agent", ident, ctx):
        return None
    for row in ctx.completed_rows:
        if row["owner"] == ident and _resolves_to_artifact(row["outcome"], ctx.repo_root):
            return None
    return (
        f"no beta->stable evidence: no golden case via an owned command, no "
        f"`# maturity-evidence: agent/{ident}` tag, and no completed-tasks.md row for "
        f"Owner={ident} with a resolvable Outcome/artifact"
    )


def _agent_cross_ref_check(component: Component, ctx: Context) -> str | None:
    ident = component.id
    if ident in ctx.command_agent.values():
        return None
    at_mention = f"@{ident}"
    for other_id, path in ctx.other_agent_files.items():
        if other_id != ident and _mentions(path.read_text(encoding="utf-8"), at_mention):
            return None
    for path in ctx.other_command_files.values():
        if _mentions(path.read_text(encoding="utf-8"), at_mention):
            return None
    overview = ctx.repo_root / "docs" / "wiki" / "agents-overview.md"
    if overview.is_file() and _mentions(overview.read_text(encoding="utf-8"), at_mention):
        return None
    return f"not cross-referenced: no command declares `agent: {ident}`, no `@{ident}` mention elsewhere"


def _agent_documented_check(component: Component, ctx: Context) -> str | None:
    return _documented_check("agent", component.id, component.name, ctx)


AGENT_STABLE_CRITERIA = (
    ("4", "beta->stable evidence (golden/tag/ledger)", _agent_evidence_check),
    ("5", "cross-referenced by a command or another agent", _agent_cross_ref_check),
    ("6", "documented in docs/wiki/**", _agent_documented_check),
    ("7", "no open P0 or P1 defect", _check_no_p0_p1_defect),
)


# ---------------------------------------------------------------------------
# `command` stable-tier checkers (section 3.2)
# ---------------------------------------------------------------------------

def _command_golden_evidence(component: Component, ctx: Context) -> str | None:
    ident = component.id
    for case in ctx.golden_cases:
        if str(case.get("command", "")).lstrip("/") == ident:
            return None
    return f"no golden case (open/ or held-out/) with command: /{ident}"


def _command_agent_resolves(component: Component, ctx: Context) -> str | None:
    agent_id = component.frontmatter.get("agent")
    if not agent_id:
        return "no `agent:` frontmatter value set"
    agent_id = str(agent_id).strip()
    if agent_id in ctx.agent_ids:
        return None
    return f"`agent: {agent_id}` does not resolve to a real agent id in the registry"


def _command_documented_check(component: Component, ctx: Context) -> str | None:
    return _documented_check("command", component.id, "", ctx)


COMMAND_STABLE_CRITERIA = (
    ("4", "golden case for this command", _command_golden_evidence),
    ("5", "`agent:` resolves to a real, existing agent id", _command_agent_resolves),
    ("6", "documented in docs/wiki/**", _command_documented_check),
    ("7", "no open P0 or P1 defect", _check_no_p0_p1_defect),
)


# ---------------------------------------------------------------------------
# `instruction` stable-tier checkers (section 3.3)
# ---------------------------------------------------------------------------

def _instruction_evidence_check(component: Component, ctx: Context) -> str | None:
    ident = component.id
    if _has_evidence_tag("instruction", ident, ctx):
        return None
    return (
        f"no `# maturity-evidence: instruction/{ident}` tag in tests/functional/**/*.py "
        f"or a golden case's expect.py"
    )


def _instruction_referenced_check(component: Component, ctx: Context) -> str | None:
    ident = component.id
    if _referenced_in_agents_or_commands(ident, ctx):
        return None
    section = _agents_md_section(ctx.agents_md_text, "Code Standards") + _agents_md_section(
        ctx.agents_md_text, "Security"
    )
    if _mentions(section, ident):
        return None
    return (
        f"not named in any agents/*.md or commands/*.md body, nor in AGENTS.md's "
        f"Code Standards/Security sections"
    )


def _instruction_documented_check(component: Component, ctx: Context) -> str | None:
    return _documented_check("instruction", component.id, "", ctx)


INSTRUCTION_STABLE_CRITERIA = (
    ("4", "`# maturity-evidence: instruction/<id>` tag", _instruction_evidence_check),
    ("5", "referenced in agents/commands or AGENTS.md routing tables", _instruction_referenced_check),
    ("6", "documented in docs/wiki/**", _instruction_documented_check),
    ("7", "no open P0 or P1 defect", _check_no_p0_p1_defect),
)


# ---------------------------------------------------------------------------
# `skill` stable-tier checkers (section 3.4)
# ---------------------------------------------------------------------------

def _skill_evidence_check(component: Component, ctx: Context) -> str | None:
    ident = component.id
    if _has_evidence_tag("skill", ident, ctx):
        return None
    return (
        f"no `# maturity-evidence: skill/{ident}` tag in tests/functional/**/*.py "
        f"or a golden case's expect.py"
    )


def _skill_referenced_check(component: Component, ctx: Context) -> str | None:
    ident = component.id
    skill_table = _agents_md_section(ctx.agents_md_text, "Skill Workflow")
    if f"`{ident}`" in skill_table:
        return None
    if _referenced_in_agents_or_commands(ident, ctx, literal=f"skill `{ident}`"):
        return None
    return (
        f"not in AGENTS.md's mandatory-skill workflow table, nor referenced as "
        f"`skill `{ident}`` in any agents/*.md or commands/*.md"
    )


def _skill_documented_check(component: Component, ctx: Context) -> str | None:
    return _documented_check("skill", component.id, "", ctx)


SKILL_STABLE_CRITERIA = (
    ("4", "`# maturity-evidence: skill/<id>` tag", _skill_evidence_check),
    ("5", "referenced in AGENTS.md skill table or agents/commands", _skill_referenced_check),
    ("6", "documented in docs/wiki/**", _skill_documented_check),
    ("7", "no open P0 or P1 defect", _check_no_p0_p1_defect),
)


STABLE_CRITERIA = {
    "agent": AGENT_STABLE_CRITERIA,
    "command": COMMAND_STABLE_CRITERIA,
    "instruction": INSTRUCTION_STABLE_CRITERIA,
    "skill": SKILL_STABLE_CRITERIA,
}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def check_component(component: Component, ctx: Context) -> list:
    failures = []
    dep_reason = _deprecation_check(component.maturity, component.body, ctx.all_ids)
    if dep_reason:
        failures.append(f"S4 (deprecation mutual exclusivity): {dep_reason}")
    if component.maturity in ("deprecated", "experimental"):
        return failures
    for criterion_id, description, checker in BETA_CRITERIA:
        reason = checker(component, ctx)
        if reason:
            failures.append(f"experimental->beta #{criterion_id} ({description}): {reason}")
    if component.maturity == "stable":
        for criterion_id, description, checker in STABLE_CRITERIA[component.category]:
            reason = checker(component, ctx)
            if reason:
                failures.append(f"beta->stable #{criterion_id} ({description}): {reason}")
    return failures


# ---------------------------------------------------------------------------
# Context construction
# ---------------------------------------------------------------------------

def _collect_command_ownership(entries: list, source_root: Path) -> tuple:
    command_agent: dict = {}
    agent_commands: dict = {}
    for entry in entries:
        if entry["category"] != "command":
            continue
        frontmatter, _ = _read_frontmatter_and_body(source_root / entry["path"])
        agent_id = frontmatter.get("agent")
        if not agent_id:
            continue
        agent_id = str(agent_id).strip()
        command_agent[entry["id"]] = agent_id
        agent_commands.setdefault(agent_id, []).append(entry["id"])
    return command_agent, agent_commands


def _collect_golden_cases(repo_root: Path) -> list:
    golden_dir = repo_root / "tests" / "golden"
    cases = []
    for bucket in ("open", "held-out"):
        base = golden_dir / bucket
        if not base.is_dir():
            continue
        for case_yaml in sorted(base.glob("*/case.yaml")):
            data = yaml.safe_load(case_yaml.read_text(encoding="utf-8")) or {}
            if isinstance(data, dict):
                cases.append(data)
    return cases


def _parse_pipe_table(path: Path) -> list:
    if not path.is_file():
        return []
    rows = []
    header_seen = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not header_seen:
            header_seen = True
            continue
        if set("".join(cells)) <= {"-", ":", ""}:
            continue
        rows.append(cells)
    return rows


def _load_active_tasks(repo_root: Path) -> list:
    rows = _parse_pipe_table(repo_root / "docs" / "tasks" / "active-tasks.md")
    return [
        {"id": c[0], "title": c[1], "owner": c[2], "status": c[3], "priority": c[4]}
        for c in rows
        if len(c) >= 5
    ]


def _load_completed_tasks(repo_root: Path) -> list:
    rows = _parse_pipe_table(repo_root / "docs" / "tasks" / "completed-tasks.md")
    return [
        {"id": c[0], "title": c[1], "owner": c[2], "done_on": c[3], "outcome": c[4]}
        for c in rows
        if len(c) >= 5
    ]


def build_context(root: Path) -> Context:
    repo_root = _repo_root(root)
    reg = _load_generate_registry(root / "scripts")
    source_root = reg._determine_source(root, "")
    platforms = reg._detect_platforms(repo_root)
    entries = reg._collect_entries(source_root, platforms)
    command_agent, agent_commands = _collect_command_ownership(entries, source_root)
    return Context(
        repo_root=repo_root,
        source_root=source_root,
        schemas_dir=source_root / "schemas",
        entries=entries,
        command_agent=command_agent,
        agent_commands=agent_commands,
        agent_ids={e["id"] for e in entries if e["category"] == "agent"},
        command_ids={e["id"] for e in entries if e["category"] == "command"},
        all_ids={e["id"] for e in entries},
        golden_cases=_collect_golden_cases(repo_root),
        active_rows=_load_active_tasks(repo_root),
        completed_rows=_load_completed_tasks(repo_root),
        wiki_files=sorted((repo_root / "docs" / "wiki").rglob("*.md")),
        agents_md_text=(repo_root / "AGENTS.md").read_text(encoding="utf-8"),
        other_agent_files={e["id"]: source_root / e["path"] for e in entries if e["category"] == "agent"},
        other_command_files={e["id"]: source_root / e["path"] for e in entries if e["category"] == "command"},
        functional_test_files=sorted((repo_root / "tests" / "functional").rglob("*.py")),
        golden_expect_files=sorted((repo_root / "tests" / "golden").glob("*/*/expect.py")),
    )


def _build_component(entry: dict, source_root: Path) -> Component:
    path = source_root / entry["path"]
    frontmatter, body = _read_frontmatter_and_body(path)
    return Component(
        category=entry["category"],
        id=entry["id"],
        name=entry.get("name", entry["id"]),
        path=path,
        maturity=entry["maturity"],
        frontmatter=frontmatter,
        body=body,
    )


# ---------------------------------------------------------------------------
# Reporting / CLI
# ---------------------------------------------------------------------------

def _format_report(results: list, verbose: bool) -> tuple:
    lines = []
    by_level: dict = {}
    failing = 0
    for component, failures in results:
        key = (component.category, component.maturity)
        bucket = by_level.setdefault(key, [0, 0])
        if failures:
            bucket[1] += 1
            failing += 1
            lines.append(f"FAIL {component.category}/{component.id} claims {component.maturity}:")
            lines.extend(f"  - {reason}" for reason in failures)
        else:
            bucket[0] += 1
            if verbose:
                lines.append(f"PASS {component.category}/{component.id} ({component.maturity})")
    lines.append("")
    lines.append(f"Summary: {len(results)} components checked, {failing} failing their claimed level.")
    for (category, level), (passed, failed) in sorted(by_level.items()):
        lines.append(f"  {category}/{level}: {passed} pass, {failed} fail")
    return "\n".join(lines), failing == 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--verbose", action="store_true", help="also print PASS lines")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    ctx = build_context(root)
    components = [_build_component(entry, ctx.source_root) for entry in ctx.entries]
    results = [(component, check_component(component, ctx)) for component in components]
    report, ok = _format_report(results, args.verbose)
    print(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
