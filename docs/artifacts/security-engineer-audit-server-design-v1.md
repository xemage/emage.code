# `@security-engineer` Audit-Command MCP Server Design (Option C completion) — v1

**Status:** Proposed (design-completion pass only — no `.mcp.json`/`servers.yaml`/agent `tools:`
change, no `sync.mjs` change, no live test, no server code written; all deferred, see §6).
**Owner:** solution-architect
**Task:** T496 (Track 2 of two independent follow-ups to T457's design pass)
**Based on:**
- `docs/artifacts/scoped-execution-primitive-v1.md` §2.3 (T457, "Option C — a third, more-capable-
  but-still-scoped mechanism: a dedicated audit-command MCP server") — the primary input this
  document extends. §2.3 sketched the shape of Option C and named exactly two things it deliberately
  left open: *"which exact commands make the fixed list"* and the injection-risk hazard every
  wrapped tool's parameter surface must be designed against (*"if `run_npm_audit`'s
  `package_json_dir` parameter were naively string-concatenated into a shell command rather than
  passed as a subprocess argument list element, this server would reintroduce exactly the injection
  risk it exists to close"*). This document resolves both, for Option C only — it does not revisit
  §2's own three-option trade-off (already decided by the user, "@security-engineer C", per
  `docs/tasks/active-tasks.md`'s T495/T496 dispatch note) or §1's `@context-retriever` track (T495,
  independent, not referenced further here).
- `implementation/knowledge/agents/security-engineer.md` (read in full this session) — the fixed
  command list below is grounded exclusively in this file's actual A01–A10 checklist text, quoted
  with line numbers, not in commands that merely sound plausible for a security audit.
- `docs/artifacts/mcp-header-url-templating-design-v1.md` (T483) — structural/rigor precedent this
  document mirrors: explicit per-item design, exact YAML/code-shaped sketches, an explicit "what this
  does not decide" section, concrete enough for a subsequent implementation task (T491, in T483's
  case) to build from directly.
- `implementation/knowledge/mcp/servers.yaml` (read-only reference this session — registry format
  and existing `stdio`-transport entry conventions only; not edited).
- `docs/artifacts/mcp-platform-contract-v1.md` (T420) — the per-platform MCP wire-shape contract any
  eventual `security-audit` server registration would need to conform to (§3.1's format table).
- `implementation/platforms/claude-code.json` (read in full this session) — confirms `execute` maps
  to `Bash` (`toolMap` line 20) and that an unmapped `mcp__<server>__<tool>` token passes through
  literally (§1.3–1.4 of the T457 document, independently re-confirmed against this file directly
  this session, not re-derived).
- `implementation/runtime/memory/context_retriever.py` (read in full this session) — the "data
  argument to a fixed call, never a shell string" pattern §2.3 points to by name; this document's
  `executor.py` sketch (§4.2) mirrors its single-choke-point-for-the-risky-operation structural
  argument (there, "no write method exists anywhere in the module"; here, "no function outside
  `executor.py` ever calls `subprocess.run`, and `executor.py` never accepts a shell string").
- `implementation/registry/summary.md` (read fresh this session) — the current real `stable`-tier
  component id list, used for §7's self-referential ledger-defect sweep.

**Consumers (once a future implementation task is authorized — not this one):** whichever agent is
assigned to build the server (the T457/T495 precedent used `backend-developer`); `qa-engineer` for
the live adversarial-injection test this document does not itself run.

---

## 0. Scope of this document

This is a design artifact only. It does **not**: edit `.mcp.json`, `servers.yaml`, any agent
`tools:` grant, `sync.mjs`, or any platform projection file; write, execute, or propose executing any
server code; dispatch or scope an implementation task (that is explicitly the orchestrator's job for
a future round); or re-open §2's own A/B/C trade-off, which the user already decided. It answers
`scoped-execution-primitive-v1.md` §2.3's two named open questions only, for Option C as already
chosen.

## 1. The fixed command list

**Method, stated up front:** every row below traces to a literal, quoted line in
`security-engineer.md`. Where the checklist names a workload but not a specific tool (full-text
content search), that gap is disclosed explicitly in the row itself, per this task's own grounding
rule — it is not silently filled in as if it were as directly sourced as the A06 row is.

| # | Tool name | Underlying command | `security-engineer.md` citation | Why a fixed/pre-approved shape is sufficient |
|---|---|---|---|---|
| 1 | `run_npm_audit(package_json_dir)` | `npm audit --json` | A06, line 50: *"Dependency audit (`npm audit`, `pip audit`, `dotnet list package --vulnerable`)"* | The checklist's need is binary per project — "does this dependency tree contain a known-vulnerable package" — and `npm audit`'s own `--json` flag is the one machine-parseable output shape a wrapper needs. There is no legitimate variant of this check that requires a different flag the model would need to choose at call time; the only real per-call variable is *which* project directory to audit. |
| 2 | `run_pip_audit(requirements_path)` | `pip-audit --format json -r <requirements_path>` | A06, line 50 (same line, "pip audit") | Same reasoning as row 1. **Naming discrepancy disclosed, not silently resolved:** `security-engineer.md` line 50 literally reads `pip audit` (a space, not a hyphen) — there is no `pip audit` subcommand built into `pip` itself; the real, installable CLI providing this capability is the separately-distributed `pip-audit` package's `pip-audit` executable. This document interprets line 50's "pip audit" as referring to that tool (consistent with `task-T496.md`'s own brief, which itself uses the hyphenated spelling when quoting `scoped-execution-primitive-v1.md` §2.3's open question) rather than inventing a different tool. Flagged here as an interpretive call, not a literal match. |
| 3 | `run_dotnet_list_vulnerable(project_or_solution_path)` | `dotnet list <path> package --vulnerable --format json` | A06, line 50 (same line, "`dotnet list package --vulnerable`") | Matches the checklist's literal quoted command almost verbatim; the only addition is `--format json` for machine-parseable output and the caller-supplied `<path>` naming which project/solution file to check — no other flag variation is needed for this workload. |
| 4 | `grep_content(pattern, path_glob, root_dir)` | `rg --json -e <pattern> --glob <path_glob> <root_dir>` | **Grounded across three lines, not one — disclosed as a different citation class than rows 1–3:** A02 line 29 *"Check for hardcoded secrets or API keys"*; A03 lines 33–36 *"SQL Injection: parameterized queries everywhere" / "Command Injection: never pass user input to shell" / "LDAP/NoSQL injection checks"*; A09 line 68 *"Log injection prevention"* (and line 67, *"Sensitive data NOT logged (passwords, tokens, PII)"*). None of these lines names a specific search tool — they describe checklist items that, in this repo's current practice, are performed via shell `grep`/`rg` through the `execute` grant (`scoped-execution-primitive-v1.md` §2.1's own characterization, not re-derived here). **This is the one row in this table where the *need* is checklist-grounded but the *tool choice* (`rg` specifically) is an inferred implementation decision, not a literal citation** — disclosed per the Blocker Protocol as `type: unclear_requirements`, `severity: minor`, with `rg` adopted as the best-justified choice (JSON output mode, already the pattern this repo's own evidence base references) rather than blocking on it. | The invocation *flags* are fixed (`--json -e ... --glob ... `, plus the safety flags in §2.4); `pattern`/`path_glob`/`root_dir` are three genuine data arguments the checklist's per-audit-item search legitimately varies. This is a narrower sense of "fixed" than rows 1–3 (which take exactly one data argument each) — stated honestly rather than glossed over, since the brief's own grounding rule asks for this per-tool, not just once. |

**What is deliberately excluded from this list, and why (closing §2.3's "smaller curated subset"
question explicitly):**

- **Per-language linters / static analysis.** `security-engineer.md`'s checklist never names a
  linter or static-analysis tool anywhere in its A01–A10 text (confirmed by the same full-file read
  this table is sourced from). `scoped-execution-primitive-v1.md` §2.1/§2.3 raise linting only as
  part of the *capability-loss* discussion under Option A, not as something the checklist itself
  calls for by name. **Not included in the fixed list.** If a genuine need surfaces later (e.g. a
  product decision that `@security-engineer` should run `eslint`/`bandit`/`semgrep` as part of A03
  coverage), that is a new checklist item requiring its own product-owner sign-off before a wrapped
  tool is designed for it — not silently added here.
- **Git-history inspection.** Named in `scoped-execution-primitive-v1.md` §2 (citing `plan-049` §2.2)
  as part of `@security-engineer`'s general legitimate workload, but not sourced to any specific line
  in `security-engineer.md`'s own checklist, and it is Option A's territory (`git_log`/`git_show` via
  the already-registered `git` server), not an "audit command" in Option C's fixed-command sense.
  **Not included here** — this is a scope boundary between Option A and Option C, not a gap.
- **Answer to §2.3's literal question:** a **smaller curated subset** (4 tools) — the three A06
  dependency-audit commands named verbatim on one line, plus one content-search tool whose need is
  checklist-grounded even though its specific underlying binary is an inferred, disclosed choice.
  Linters are explicitly out, on the grounds above.

## 2. Parameter surface and the injection-risk hazard, addressed individually per tool

**Shared framing, stated once here and then verified per-tool below (not treated as sufficient on
its own — see the brief's own requirement that each subsection restate it):** every wrapped tool's
underlying command is a Python list literal (`argv: list[str]`) constructed by this server's own
code, never a string. Caller-supplied parameters are substituted into specific *elements* of that
list (or passed as a separate `cwd` keyword argument, itself never concatenated into `argv`), and the
list is executed via `subprocess.run(argv, shell=False, ...)`. `shell=False` is Python's own default,
but this design sets it explicitly and in exactly one place (§4.2), specifically so that no caller
input is ever interpreted by a shell — a value like `"; rm -rf /"` passed as a `pattern` or a path
reaches the OS's `execve` as one literal argv element, not as shell syntax to be parsed.

### 2.1 `run_npm_audit(package_json_dir: str)`

| Parameter | Type | Required | Validation before use |
|---|---|---|---|
| `package_json_dir` | `str` (filesystem path) | yes | Resolved to an absolute path via `pathlib.Path(...).resolve()`, then checked to (a) exist, (b) be a directory, (c) contain a `package.json` file, (d) resolve to a location inside the server's configured allowed-root (§4.3) — rejecting `..`-traversal and absolute paths outside the workspace, mirroring the already-registered `filesystem` server's own "requires at least one allowed directory to operate" model (`scoped-execution-primitive-v1.md` §3.1, citing the official `filesystem` server README). |

**Code sketch (`commands.py`):**
```python
def build_npm_audit_argv(package_json_dir: str) -> tuple[list[str], str]:
    validated_dir = resolve_and_validate_path(package_json_dir, must_contain="package.json")
    argv = ["npm", "audit", "--json"]          # fixed literal — package_json_dir never enters argv
    return argv, str(validated_dir)             # returned separately, consumed only as `cwd`
```
**Injection-hazard statement (this tool specifically):** `package_json_dir` never appears inside
`argv` at all — it is passed to `subprocess.run(argv, cwd=validated_dir, shell=False, ...)` as the
`cwd` keyword argument, a distinct parameter from the command line itself. Even a maximally
adversarial value for this parameter can only ever change *which directory* `npm audit --json` runs
in (and only after passing the existence/containment checks above); it cannot alter the command being
run, append flags, or reach a shell, because the three-element `argv` list is a fixed literal with no
substitution points at all.

### 2.2 `run_pip_audit(requirements_path: str)`

| Parameter | Type | Required | Validation before use |
|---|---|---|---|
| `requirements_path` | `str` (filesystem path) | yes | Resolved and validated the same way as §2.1 (exists, is a file, filename matches `requirements*.txt` or is explicitly a `.txt`/`.in` file, resolves inside the allowed root). Directory-mode (`pip-audit --path <dir>`) is **not** designed here — out of scope, flagged in §6. |

**Code sketch (`commands.py`):**
```python
def build_pip_audit_argv(requirements_path: str) -> list[str]:
    validated_path = resolve_and_validate_path(requirements_path, must_be_file=True)
    return ["pip-audit", "--format", "json", "-r", str(validated_path)]
```
**Injection-hazard statement (this tool specifically):** `requirements_path` reaches the subprocess
call as the *fifth element* of a five-element `argv` list, after passing path validation. Because
`subprocess.run` with `shell=False` invokes the target executable directly (via `execve`-family
syscalls), the OS never re-parses this string for shell metacharacters (`;`, `|`, `` ` ``, `$(...)`,
etc.) — those characters, if somehow present after validation, would be passed to `pip-audit` as a
literal (and almost certainly rejected-as-not-a-real-path) filename, not executed.

### 2.3 `run_dotnet_list_vulnerable(project_or_solution_path: str)`

| Parameter | Type | Required | Validation before use |
|---|---|---|---|
| `project_or_solution_path` | `str` (filesystem path) | yes | Resolved and validated as in §2.1/§2.2 (exists, is a file, extension is `.csproj`, `.fsproj`, `.vbproj`, or `.sln`, resolves inside the allowed root). |

**Code sketch (`commands.py`):**
```python
def build_dotnet_list_vulnerable_argv(project_or_solution_path: str) -> list[str]:
    validated_path = resolve_and_validate_path(
        project_or_solution_path, allowed_suffixes={".csproj", ".fsproj", ".vbproj", ".sln"}
    )
    return ["dotnet", "list", str(validated_path), "package", "--vulnerable", "--format", "json"]
```
**Injection-hazard statement (this tool specifically):** `project_or_solution_path` occupies exactly
one element (index 2) of a seven-element fixed `argv` list. As with §2.1/§2.2, `shell=False` means
this string is delivered to the `dotnet` process as a single literal argument; it cannot inject
additional flags (e.g. a value like `foo.sln --exec calc` is passed whole, as one argument containing
a literal space and the substring `--exec calc`, not parsed as two separate flags — flag-splitting
only happens when a shell tokenizes a string, which never occurs here) or escape into a second
command.

### 2.4 `grep_content(pattern: str, path_glob: str, root_dir: str = ".")`

This is the tool with the largest parameter surface and the one the T457 hazard example named
directly, so it gets the most detailed treatment.

| Parameter | Type | Required | Validation before use |
|---|---|---|---|
| `pattern` | `str` (ripgrep-syntax regex) | yes | Length-capped (recommended default: 512 characters — an implementation-detail number, not load-bearing for the injection defense itself, flagged in §6) to bound regex-DoS (`ReDoS`) risk; otherwise passed through unvalidated as *content*, never as *shell syntax* (see hazard statement below — this is the load-bearing distinction). |
| `path_glob` | `str` (glob pattern, e.g. `"*.py"`) | yes | Length-capped similarly; passed as the value of `rg`'s own `--glob` flag, a distinct argv element. |
| `root_dir` | `str` (filesystem path) | no, default `"."` | Resolved and validated as in §2.1 (must exist, must be a directory, must resolve inside the allowed root) — this is the one parameter here with a real path-traversal concern, handled identically to the other three tools' path parameters. |

**Code sketch (`commands.py`):**
```python
MAX_PATTERN_LENGTH = 512
MAX_GLOB_LENGTH = 256

def build_grep_content_argv(pattern: str, path_glob: str, root_dir: str = ".") -> tuple[list[str], str]:
    if len(pattern) > MAX_PATTERN_LENGTH:
        raise ValueError("pattern exceeds maximum length")
    if len(path_glob) > MAX_GLOB_LENGTH:
        raise ValueError("path_glob exceeds maximum length")
    validated_dir = resolve_and_validate_path(root_dir, must_exist=True, must_be_dir=True)
    argv = [
        "rg", "--json", "--no-follow", "--max-filesize", "5M",
        "-e", pattern,
        "--glob", path_glob,
        str(validated_dir),
    ]
    return argv, str(validated_dir)
```
**Injection-hazard statement (this tool specifically — the one §2.3 named by example):**
`pattern` and `path_glob` each occupy exactly one `argv` element (following the `-e` and `--glob`
flags respectively), and `root_dir` is validated the same way `package_json_dir` is in §2.1. This is
precisely the case `scoped-execution-primitive-v1.md` §2.3 warned about by name — *"if
`run_npm_audit`'s `package_json_dir` parameter were naively string-concatenated into a shell command
... this server would reintroduce exactly the injection risk it exists to close"* — generalized to
`grep_content`'s three parameters: none of them is ever concatenated into a string that is later
handed to a shell; each is one distinct element of a list handed directly to `execve`. A value like
`pattern = "foo; rm -rf /"` is passed to `rg` as a single literal regex to search *for* (rg will
either match that literal text or, if it isn't valid regex syntax, error out) — it is never
interpreted as a second shell command, because no shell is ever invoked to parse it.

**Residual risk, disclosed, distinct from command injection:** `pattern` is caller-controlled regex
*content*, and command injection is not the only risk class a regex engine exposes — a pathological
pattern (e.g. deeply nested quantifiers) could cause `rg`'s regex engine to spend excessive CPU time
against large inputs (a `ReDoS`-style resource-exhaustion risk, not a code-execution risk). This
design's mitigations are the `MAX_PATTERN_LENGTH` cap above and the `--max-filesize 5M`/timeout
(§4.2) already present in the sketch; a more rigorous mitigation (e.g. validating `pattern` against a
regex-complexity heuristic, or using `rg`'s own `-U`/timeout flags if available) is **not** further
designed here — flagged in §6 as a real, disclosed, non-injection risk this document does not fully
close.

## 3. `servers.yaml` entry design

Mirrors the existing `stdio`-transport entry shape already used by `gitlab`/`playwright`/`fetch`
(`servers.yaml` lines 17–36) and the `command: python3, args: [-m, ...]` shape
`scoped-execution-primitive-v1.md` §1.4 already specified for `@context-retriever`'s sibling server:

```yaml
  security-audit:
    tags: [extended]
    transport: stdio
    command: python3
    args: ["-m", "implementation.runtime.security.audit_server"]
```

**Tag: `extended`, not `core`** — same reasoning class as `filesystem`/`git`/`docker`/`postgresql`:
this is opt-in, role-specific infrastructure (only `@security-engineer` would ever be granted its
tools), not a universal capability every agent/platform needs by default, parallel to
`mcp-header-url-templating-design-v1.md` §2(b)'s `cwso` audience-fit reasoning.

**No `env:` block** — unlike `gitlab`/`brave`, none of this server's four tools needs a secret or
external credential; every underlying command (`npm`, `pip-audit`, `dotnet`, `rg`) is a local CLI
invocation against the calling agent's own workspace, with no network call and no API key.

**Illustrative future Claude Code grant (not applied by this document — a future implementation task
would write this into `security-engineer.md`'s frontmatter, replacing `execute`):**
```
tools: [read, search, mcp__security-audit__run_npm_audit, mcp__security-audit__run_pip_audit,
mcp__security-audit__run_dotnet_list_vulnerable, mcp__security-audit__grep_content, web, mcp__fetch]
```
This follows the exact-MCP-tool-name delivery mechanism `scoped-execution-primitive-v1.md` §1.3–1.4
already established and re-confirmed this session against `claude-code.json`'s `toolMap` directly
(unmapped tokens, including `mcp__<server>__<tool>`, pass through literally — `sync.mjs` lines
267–276, cited by the T457 document and not re-verified byte-for-byte a second time in this
design-only session, since no code changes are being made here). Per-platform grant format for the
other 6 platforms is **not** resolved here — it inherits exactly the same open, disclosed gap
`scoped-execution-primitive-v1.md` §4 already left open for `@security-engineer`'s Option A grant,
now equally applicable to Option C's grant (see §6).

## 4. Server module structure sketch

### 4.1 File layout

```
implementation/runtime/security/            # new subpackage — does not exist today, disclosed in §6
├── __init__.py
├── audit_server.py      # stdio MCP entrypoint; registers exactly the 4 tools, no others
├── commands.py           # build_*_argv() — pure functions, validated data in, (argv, cwd?) out
├── executor.py           # the ONLY module in this package that calls subprocess.run
└── validation.py         # resolve_and_validate_path(), length caps, allowed-root enforcement
```

**Deliberate structural choke point, mirroring `context_retriever.py`'s own "no write method exists"
argument (cited in "Based on" above):** exactly one function in this entire package —
`executor.run_fixed_argv()` — ever calls `subprocess.run`. `commands.py` only builds Python list
literals and validated path strings; it performs no I/O. `audit_server.py`'s four tool handlers do
nothing but accept MCP-typed parameters, call one `commands.build_*_argv()` function, then call
`executor.run_fixed_argv()`, then shape the result. This means an adversarial parameter value can
only ever influence the *value* of one pre-determined `argv` element (per §2's per-tool tables) — it
can never influence `argv`'s length, order, the command name at `argv[0]`, or whether `shell=True` is
used, because those are fixed at every call site in `commands.py` and `shell=False` is set in exactly
one place, `executor.py`, and nowhere else in the package.

### 4.2 `executor.py` (the sole subprocess choke point)

```python
import subprocess

DEFAULT_TIMEOUT_SECONDS = 30      # implementation-detail default, not load-bearing for the
                                    # injection defense itself — see §6

def run_fixed_argv(
    argv: list[str],
    cwd: str | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict:
    """The only call to subprocess.run anywhere in this package. `shell` is never a parameter
    here — it is hardcoded False, permanently, so no caller (even a future maintainer editing
    this file) can accidentally flip it per-call."""
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,   # non-zero exit is expected/informational for audit tools
                            # (e.g. `npm audit` exits non-zero when vulnerabilities ARE found —
                            # that is a successful audit result, not a subprocess failure)
        )
    except subprocess.TimeoutExpired:
        return {"timed_out": True, "argv": argv}
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,      # truncation policy: see §6, not fully pinned here
        "stderr": result.stderr,
        "timed_out": False,
    }
```

**Correctness note carried into the design deliberately:** `check=False` is required, not optional —
`npm audit`, `pip-audit`, and `dotnet list ... --vulnerable` all use a non-zero exit code to signal
"vulnerabilities were found," which is the expected, successful-audit outcome, not an execution
error. A design that used `check=True` (raising on non-zero exit) would misreport every finding as a
tool failure.

### 4.3 `validation.py` (allowed-root enforcement, shared by all four tools' path parameters)

```python
from pathlib import Path

class PathValidationError(ValueError):
    pass

def resolve_and_validate_path(
    candidate: str,
    *,
    allowed_root: Path,          # server-startup configuration — see note below
    must_exist: bool = True,
    must_be_dir: bool = False,
    must_be_file: bool = False,
    must_contain: str | None = None,      # e.g. "package.json"
    allowed_suffixes: set[str] | None = None,
) -> Path:
    resolved = Path(candidate).resolve()
    try:
        resolved.relative_to(allowed_root.resolve())
    except ValueError as exc:
        raise PathValidationError(
            f"{candidate!r} resolves outside the allowed root"
        ) from exc
    if must_exist and not resolved.exists():
        raise PathValidationError(f"{candidate!r} does not exist")
    if must_be_dir and not resolved.is_dir():
        raise PathValidationError(f"{candidate!r} is not a directory")
    if must_be_file and not resolved.is_file():
        raise PathValidationError(f"{candidate!r} is not a file")
    if must_contain and not (resolved / must_contain).exists():
        raise PathValidationError(f"{candidate!r} does not contain {must_contain}")
    if allowed_suffixes and resolved.suffix not in allowed_suffixes:
        raise PathValidationError(f"{candidate!r} has an unsupported extension")
    return resolved
```

`allowed_root` is not a per-call parameter — it is fixed once at server startup (e.g. from the
workspace root the `stdio` server process is launched in, mirroring `context_retriever.py`'s own
`derive_project_id()`/`resolve_platform()` pattern of taking trusted, build-time/launch-time
configuration rather than caller-editable input for anything that establishes a trust boundary). This
means even a successfully-injection-free path parameter cannot be used to point any of the four tools
at a directory outside the agent's own workspace.

### 4.4 `audit_server.py` (tool registration sketch — MCP SDK wiring, not fully written)

```python
# Sketch only — exact MCP SDK call shapes (stdio_server(), Server(), tool decorators) are
# implementation-phase work, not re-derived here; scoped-execution-primitive-v1.md §1.4 made the
# same disclosure for @context-retriever's sibling server ("probably using the official mcp Python
# SDK's stdio_server helper, not investigated in detail here since that is implementation-phase
# work").

from implementation.runtime.security import commands, executor

async def run_npm_audit(package_json_dir: str) -> dict:
    argv, cwd = commands.build_npm_audit_argv(package_json_dir)
    return executor.run_fixed_argv(argv, cwd=cwd)

async def run_pip_audit(requirements_path: str) -> dict:
    argv = commands.build_pip_audit_argv(requirements_path)
    return executor.run_fixed_argv(argv)

async def run_dotnet_list_vulnerable(project_or_solution_path: str) -> dict:
    argv = commands.build_dotnet_list_vulnerable_argv(project_or_solution_path)
    return executor.run_fixed_argv(argv)

async def grep_content(pattern: str, path_glob: str, root_dir: str = ".") -> dict:
    argv, cwd = commands.build_grep_content_argv(pattern, path_glob, root_dir)
    return executor.run_fixed_argv(argv, cwd=cwd)

def main() -> None:
    """Registers exactly the four functions above as MCP tools and nothing else — no
    free-form 'run_command' or 'execute' tool is ever exposed by this server."""
    ...
```

## 5. Design decisions summary table

| Decision | This document's answer |
|---|---|
| Fixed command count | 4 (`run_npm_audit`, `run_pip_audit`, `run_dotnet_list_vulnerable`, `grep_content`) — a curated subset, not "every plausible audit command" |
| Linters/static analysis | Excluded — not named anywhere in `security-engineer.md`'s checklist; flagged as a future gap-fill candidate needing product-owner sign-off, not decided here |
| Git-history inspection | Excluded from this server — Option A's territory (already-registered `git` server), not an Option C "fixed audit command" |
| Parameter delivery | `subprocess.run(argv: list[str], shell=False, ...)` exclusively; exactly one module (`executor.py`) ever calls it |
| Path parameters | Validated against a server-configured `allowed_root`, mirroring the `filesystem` server's own allowed-directory model |
| `servers.yaml` tag | `extended` (opt-in, role-specific — parallel to `filesystem`/`git`/`docker`) |
| Secrets | None needed — every tool is a local CLI subprocess call, no `env:` block |

## 6. What this document does NOT decide

1. **Whether Option C should actually be built now.** The A/B/C trade-off itself was already decided
   by the user ("@security-engineer C"); this document only completes Option C's scope. Whether and
   when an implementation task is dispatched is explicitly the orchestrator's call, not made here.
2. **Implementation task ID, owner, or dispatch timing.** Not created or assigned by this document,
   per this task's own explicit constraint.
3. **Exact timeout/output-truncation limits.** `DEFAULT_TIMEOUT_SECONDS = 30`, `MAX_PATTERN_LENGTH =
   512`, `MAX_GLOB_LENGTH = 256`, and the `--max-filesize 5M` flag are this document's proposed
   defaults, not verified against any real workload — an implementer should treat these as a
   starting point, not a specification to build byte-for-byte the way T483 §5's parser code was.
   `stdout`/`stderr` truncation policy (recommended: cap and flag `truncated: true`, never silently
   drop) is named but not fully specified.
4. **Whether `rg` (ripgrep) is guaranteed present in every execution environment this server would
   run in.** Not verified live (no `execute`/`Bash` tool in this session, consistent with this task's
   design-only constraint) — flagged as a dependency assumption for whoever implements this.
   Likewise, `npm`, `pip-audit`, and the `dotnet` SDK's own availability in the agent's runtime
   environment is assumed, not verified.
5. **The `pip audit` vs. `pip-audit` naming interpretation (§1, row 2).** Disclosed as an
   interpretive call, not independently confirmed against the user's or `security-engineer.md`
   author's actual intent.
6. **`grep_content`'s regex-complexity (`ReDoS`) mitigation, beyond a length cap.** A real, disclosed,
   non-injection risk (§2.4) that this document's length-cap mitigation only partially addresses — a
   more rigorous mitigation (complexity heuristics, engine-level timeout flags) is not designed here.
7. **Per-platform (non-Claude-Code) grant syntax for this server's tools.** Inherits, unresolved, the
   same open gap `scoped-execution-primitive-v1.md` §4 already left open for `@security-engineer`'s
   Option A grant — `github`/`opencode`/`gemini`/`cursor`/`pi`/`cline`'s exact per-tool grant
   mechanisms (or absence thereof) were investigated there for Option A specifically and are not
   re-investigated here for Option C; the same per-platform table applies by extension but was not
   independently re-verified this session.
8. **Whether a dedicated ADR should be written for this design.** Not created this session, mirroring
   `mcp-header-url-templating-design-v1.md` §10's own disclosed reason (no directory-listing tool
   available in this session's grant to safely determine the next unused ADR number without risking a
   collision) — not required by this task's own Expected Outputs, so not treated as a blocker, only
   disclosed.
9. **Implementation itself.** Explicitly out of scope for this task and remains a separate, future,
   not-yet-dispatched task, per this task's own Constraints and Objective sections.

## 7. Self-referential ledger-defect sweep

Per this task's Acceptance Criterion 5: this document, and `docs/tasks/task-T496.md` (read in full at
the start of this session, unmodified by this task), were checked against the current real
`stable`-tier component id list, re-derived fresh this session from
`implementation/registry/summary.md` (31 ids: 20 agents, 4 instructions, 7 skills —
`data-mockup-agent`, `database-engineer`, `demo-agent`, `feasibility-agent`, `frontend-developer`,
`integration-agent`, `poc-devops-engineer`, `poc-orchestrator`, `poc-qa-engineer`,
`poc-security-engineer`, `poc-technical-writer`, `product-owner`, `qa-engineer`, `release-manager`,
`scaffolding-agent`, `scrum-master`, `technical-debt-narrator`, `technical-writer`,
`technology-scout`, `ux-designer`, `coding-standards`, `git-workflow`, `poc-guidelines`,
`security-guidelines`, `checkpoint-protocol`, `code-review`, `receiving-code-review`,
`systematic-debugging`, `testing-strategy`, `validation-gates`, `verification-before-completion`).

**Result: zero hits.** Neither this document nor `task-T496.md` names any of the 31 ids above as a
bare token anywhere in their text. The two agent ids this document and its brief do discuss by name —
`security-engineer` and `solution-architect` — are both currently `experimental`, not `stable` (the
former precisely because `T457`'s own open gap, which this task deepens rather than closes, excludes
it), so neither is at risk of the false-promotion regression this sweep exists to catch. No blocker to
report for this criterion.

**Caveat on evidentiary class, disclosed rather than overstated:** this session has no `execute`
tool, so this sweep was performed by direct text comparison against `implementation/registry/
summary.md`'s current content (itself read fresh this session, not assumed from a prior artifact's
count), not by running `check-maturity.py --verbose` live. This is the same evidentiary limitation
`mcp-platform-contract-v1.md` and `mcp-header-url-templating-design-v1.md` both disclosed for their
own no-`execute`-tool sessions — a manual, direct-read-based check, not a command transcript.

## 8. Blockers

None, in the blocking sense. Two items were genuinely underdetermined by `security-engineer.md`'s
literal text and are reported per this task's own Blocker Protocol guidance (report
`unclear_requirements`/`minor` and propose a best-justified choice rather than halting):

- **`type: unclear_requirements`, `severity: minor`** — `grep_content`'s underlying tool choice
  (`rg` vs. `grep`) is not named by any line in `security-engineer.md`; only the *need* for
  content-level search is checklist-grounded (§1, row 4). Resolved by proposing `rg` as the
  best-justified choice (JSON output support, already referenced in this repo's own evidence base),
  disclosed rather than silently asserted as directly sourced.
- **`type: unclear_requirements`, `severity: minor`** — line 50's literal "pip audit" (space) vs. the
  real `pip-audit` (hyphenated) CLI package name (§1, row 2). Resolved by adopting the hyphenated
  tool as the intended referent, disclosed as an interpretive call rather than a literal match.

Neither blocked this document's completion; both are resolved with a stated, justified choice, per
this task's own explicit instruction that this mirrors how `plan-049`/`scoped-execution-primitive-v1.md`
itself handled genuinely unresolved per-platform questions.
