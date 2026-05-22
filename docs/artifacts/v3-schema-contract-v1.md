# v3 Schema Contract v1

Status: Draft for implementation (Execution Wave 1, P0)
Based on: [docs/checkpoints/checkpoint-005-v3-planning-approved.md](../checkpoints/checkpoint-005-v3-planning-approved.md), [docs/plans/plan-002-emage-code-v3-roadmap.md](../plans/plan-002-emage-code-v3-roadmap.md)
Primary consumers: T010, T011, T012

## 1) Purpose and scope

This artifact defines the versioned schema contracts for emage.code v3 knowledge and runtime metadata so that tooling can:
- validate canonical knowledge objects before projection,
- project consistently to Copilot (.github), Gemini (.gemini), Opencode (.opencode), and Cursor (.cursor),
- support managed agent cookbook deployment descriptors,
- enforce secure, fail-closed handoff payload contracts,
- preserve v2 compatibility during phased migration.

In scope:
- canonical object schemas (agents, commands, instructions, skills),
- projection manifest schema,
- registry schema,
- managed cookbook schema,
- handoff payload schema and validation rules,
- compatibility and CI gate mapping.

Out of scope:
- runtime control plane implementation details,
- vendor SDK-specific transport internals.

## 2) Versioning model

### 2.1 Contract identifiers

Each schema-governed object MUST declare:
- schema: string URI or local path to authoritative JSON Schema
- schemaVersion: semantic version string, format MAJOR.MINOR.PATCH

Rules:
- MAJOR: breaking change to required fields, types, enum narrowing, or behavior.
- MINOR: backward-compatible field additions, enum expansion, optional sections.
- PATCH: clarifications, metadata-only changes, typo fixes, no validation impact.

### 2.2 Stability channel and support window

Objects MAY include stability with values: experimental, stable, deprecated.

Support policy:
- Current major (N): full support.
- Previous major (N-1): read + project support only during migration window.
- Older than N-1: unsupported.

For v3 rollout:
- v2 knowledge remains accepted and projectable.
- v3 is introduced behind validators and projection feature flags.

### 2.3 Deprecation policy

Deprecation lifecycle is mandatory:
1. Introduce successor field/behavior in MINOR release.
2. Mark old field as deprecated in schema docs and validators.
3. Emit CI warning for at least one MINOR cycle.
4. Remove only in next MAJOR release.

Non-breaking change policy:
- Adding optional fields is allowed.
- Tightening constraints on existing valid values is not allowed in MINOR/PATCH.
- Renaming fields requires alias support until next MAJOR.

## 3) Canonical object schemas (agents, commands, instructions, skills)

Canonical source root: v3/implementation/knowledge
Serialization format: markdown body + YAML frontmatter
Validation mode: frontmatter schema validation + cross-reference checks

### 3.1 Shared frontmatter fields (all object kinds)

Required fields:
- schema: string, required, non-empty
- schemaVersion: string, required, semver
- id: string, required, pattern ^[a-z0-9][a-z0-9-]{1,63}$
- name: string, required, minLength 1
- description: string, required, minLength 10
- owners: array[string], required, minItems 1
- stability: enum, optional, one of experimental|stable|deprecated, default stable
- tags: array[string], optional, unique

Testable rules:
- additionalProperties MUST be false at object-specific schema level unless explicitly declared.
- id MUST be unique within object kind.

### 3.2 Agent schema

File location: v3/implementation/knowledge/agents/<slug>.md

Required fields:
- kind: literal agent
- role: enum orchestrator|worker
- tools: array[string], required for canonical form, unique
- subagents: array[string], optional, references agent ids
- userInvocable: boolean, required
- modelHints: object, optional
- permissions: object, required

permissions object required fields:
- mode: enum read-only|write-scoped|write-full
- allowedPaths: array[string], optional glob allowlist
- forbiddenOperations: array[string], optional

Agent-specific rules:
- role=orchestrator implies userInvocable=true.
- role=worker implies userInvocable=false unless explicitly allowlisted.
- subagents values MUST resolve to existing agent ids.
- tools MUST map to known tool registry names during validation.

Agent example (canonical):

    ---
    schema: ./schemas/agent.schema.json
    schemaVersion: 3.0.0
    kind: agent
    id: orchestrator
    name: Orchestrator
    description: Coordinates planning, delegation, and validation across specialist agents.
    owners: [platform]
    role: orchestrator
    tools: [read_file, apply_patch, run_in_terminal]
    subagents: [solution-architect, backend-engineer, qa-engineer]
    userInvocable: true
    permissions:
      mode: write-scoped
      allowedPaths: [docs/**, v3/**, tests/**]
      forbiddenOperations: [git-reset-hard]
    tags: [core, orchestration]
    ---

### 3.3 Command schema

File location: v3/implementation/knowledge/commands/<slug>.md

Required fields:
- kind: literal command
- agent: string, required, references agent id
- argumentHint: string, optional
- inputSchemaRef: string, optional
- outputContractRef: string, optional

Rules:
- agent MUST resolve to existing agent id.
- If inputSchemaRef is set, referenced schema file MUST exist.

### 3.4 Instruction schema

File location: v3/implementation/knowledge/instructions/<slug>.md

Required fields:
- kind: literal instruction
- applyTo: string, required glob pattern

Optional fields:
- priority: integer, default 100
- conflictsWith: array[string]

Rules:
- applyTo MUST be valid glob syntax.
- conflictsWith references MUST resolve to instruction ids.

### 3.5 Skill schema

File location: v3/implementation/knowledge/skills/<skill>/SKILL.md

Required fields:
- kind: literal skill
- summary: string, required, minLength 20
- entrypoint: string, required path within skill folder

Optional fields:
- dependencies: array[string]
- maturity: enum draft|beta|ga|deprecated

Rules:
- entrypoint MUST exist.
- dependencies MUST resolve to skill ids.

## 4) Projection manifest schema

File location: v3/implementation/platforms/<platform>.json
Supported platform ids: github, gemini, opencode, cursor

Required manifest fields:
- schema: string
- schemaVersion: semver string
- platform: enum github|gemini|opencode|cursor
- displayName: string
- outputDir: string
- fileMap: object with required keys agents|commands|instructions|skills
- frontmatter: object with required keys agents|commands|instructions|skills
- projectionMode: enum strict|compat

fileMap.<kind> required:
- dir: string
- ext: string for non-tree kinds
- preserveTree: boolean for skills

frontmatter.<kind> required:
- keepKeys: array[string]

Optional:
- renameKeys: object<string,string>
- transformRules: object
- addToOrchestrators: object
- orchestratorNames: array[string]
- mcp: object
- extras: array[object]

Platform-specific compatibility requirements:
- github: commands extension .prompt.md, agents extension .agent.md.
- gemini: agent tools removed in projection output.
- opencode: agent tools transformed to object map with true values; orchestrators include user-invocable=true.
- cursor: instructions.applyTo renamed to globs in projected frontmatter.

Projection integrity requirements:
- body content MUST remain byte-equivalent between source and projection.
- generated manifest file list MUST include all expected outputs.

## 5) Registry schema

File location: v3/implementation/registry/registry.json
Purpose: machine-readable inventory of all canonical objects and projection compatibility metadata.

Required top-level fields:
- schema
- schemaVersion
- generatedAt (RFC3339 UTC)
- sourceCommit (git SHA)
- entries (array, minItems 1)

Each registry entry required fields:
- id
- kind: agent|command|instruction|skill|cookbook
- name
- version: semver
- path: workspace-relative path
- checksum: sha256 hex
- owners: array[string]
- maturity: draft|beta|ga|deprecated
- compatibility: object

compatibility required fields:
- minCoreVersion
- supportedPlatforms: array containing one or more of github|gemini|opencode|cursor
- projectionStatus: map platform -> pass|warn|fail

Rules:
- path MUST exist.
- checksum MUST match file content at generation time.
- entries.id MUST be globally unique across kinds.

## 6) Managed cookbook schema (agent.yaml and subagent references)

Root location: v3/implementation/cookbooks/<cookbook-id>/
Primary manifest: agent.yaml

### 6.1 agent.yaml required fields

- schema
- schemaVersion
- cookbookId: pattern ^[a-z0-9][a-z0-9-]{1,63}$
- name
- version: semver
- description
- orchestrator: object
- workers: array[minItems 1]
- handoffPolicy: object
- security: object

orchestrator required fields:
- ref: string, registry id of orchestrator agent
- instructions: array[path]
- skills: array[path]

workers item required fields:
- ref: string, registry id of worker agent
- skills: array[path]
- maxConcurrency: integer >= 1

handoffPolicy required fields:
- allowRoutes: array of from->to pairs
- defaultAction: deny|ask|allow

security required fields:
- redactFields: array[string]
- allowSecretsInPayload: boolean (MUST be false)
- requireSchemaValidation: boolean (MUST be true)

### 6.2 Subagent references

A cookbook MUST reference subagents by stable registry id (not file path).

Rules:
- All refs MUST resolve in registry at validation time.
- Role checks: orchestrator ref MUST point to role=orchestrator agent; worker refs MUST point to role=worker agents.
- Duplicate worker refs are invalid unless variant key differs.

Cookbook example (agent.yaml):

    schema: ../schemas/cookbook.schema.json
    schemaVersion: 3.0.0
    cookbookId: core-delivery
    name: Core Delivery Cookbook
    version: 1.0.0
    description: Baseline orchestrated delivery workflow with architecture, implementation, and QA workers.
    orchestrator:
      ref: orchestrator
      instructions:
        - ../../knowledge/instructions/coding-standards.md
        - ../../knowledge/instructions/security-guidelines.md
      skills:
        - ../../knowledge/skills/task-management/SKILL.md
    workers:
      - ref: solution-architect
        skills:
          - ../../knowledge/skills/dependency-graphing/SKILL.md
        maxConcurrency: 1
      - ref: backend-engineer
        skills:
          - ../../knowledge/skills/rapid-prototyping/SKILL.md
        maxConcurrency: 2
    handoffPolicy:
      allowRoutes:
        - from: orchestrator
          to: solution-architect
        - from: orchestrator
          to: backend-engineer
      defaultAction: deny
    security:
      redactFields: [apiKey, token, password, authorization]
      allowSecretsInPayload: false
      requireSchemaValidation: true

## 7) Handoff payload schema and validation rules

Purpose: secure inter-agent payload exchange with strict routing and fail-closed validation.

### 7.1 Handoff payload required fields

- schema
- schemaVersion
- handoffId: UUID
- timestamp: RFC3339 UTC
- fromAgent: agent id
- toAgent: agent id
- taskId: string
- intent: string enum delegate|request-review|request-data|escalate
- payload: object
- constraints: object
- trace: object

constraints required fields:
- maxToolCalls: integer >= 0
- writablePaths: array[string]
- forbiddenActions: array[string]
- deadlineUtc: RFC3339 UTC

trace required fields:
- correlationId: UUID
- parentStepId: string
- checkpointRef: path

### 7.2 Security validation rules

Mandatory rules:
- Route allowlist: fromAgent->toAgent MUST be allowed by cookbook or runtime policy.
- Schema validation: payload MUST validate against handoff schema before delivery.
- Fail closed: invalid payload, unknown fields, unknown route, or schema mismatch MUST reject handoff.
- Secret protection: payload MUST NOT contain secrets, credentials, tokens, private keys, or raw auth headers.
- Redaction: fields listed in cookbook security.redactFields MUST be masked in logs.
- Size limits: serialized payload size MUST be <= configured max (default 64 KB).
- Integrity: handoffId MUST be unique within run; duplicate ids are rejected.

Recommended rules:
- Optional payload signature for integrity attestation.
- Optional replay nonce store for anti-replay in distributed runtimes.

## 8) Compatibility matrix (v2 -> v3)

| Area | v2 behavior | v3 contract | Compatibility mode |
|---|---|---|---|
| Canonical metadata | Minimal frontmatter (name/description + kind-specific fields) | Adds schema, schemaVersion, id, owners, stability | v3 validators accept v2 with inferred defaults in compat mode |
| Agent tools projection | Platform-specific transforms (drop/object/array) | Same transforms retained, now explicitly contracted | Non-breaking |
| Instruction targeting | applyTo in canonical, cursor projection renames to globs | Same behavior retained | Non-breaking |
| Generated manifest | .generated-manifest.json file presence enforced by tests | Same plus schemaVersion and checksum policy | Non-breaking with stricter checks |
| MCP projection | Platform mcp blocks + output formats | Same plus schema validation on manifest and output payload shape | Non-breaking |
| Registry | Not formalized in v2 | New required v3 artifact | Additive |
| Cookbooks | Not formalized in v2 | New agent.yaml contract with refs and handoff policy | Additive |
| Handoff payload | Implicit/implementation-defined | Strict versioned schema with fail-closed validation | Additive but security-enforced |

Migration notes:
- Phase 1: Introduce v3 schema files and compat validator reading existing v2 frontmatter.
- Phase 2: Backfill missing v3 fields in canonical knowledge objects.
- Phase 3: Enable strict mode for changed files while retaining compat mode for untouched v2 files.
- Phase 4: Remove compat mode only after migration guide completion and adoption gate sign-off.

## 9) Validation gates and CI enforcement points

Gate ownership and execution points for T010/T011/T012:

1. Contract schema validation (T010)
- Command: check-v3 --schemas
- Enforces: all canonical objects validate against declared schema and schemaVersion rules.
- Fails on: missing required field, wrong type, additional properties, semver violations.

2. Projection drift + integrity (T010)
- Command: check-v3 --projection
- Enforces: expected generated files, generated manifest coverage, frontmatter key contract, body equivalence.
- Mirrors existing projection integrity expectations from functional tests.

3. Cookbook contract validation (T011)
- Command: check-v3 --cookbooks
- Enforces: agent.yaml required fields, ref resolution, role constraints, handoff policy completeness.

4. Registry generation and verification (T010/T012)
- Command: check-v3 --registry
- Enforces: unique ids, existing paths, checksum validity, platform compatibility metadata completeness.

5. Handoff security gate (T012 + T013 handoff)
- Command: check-v3 --handoff-security
- Enforces: route allowlists, fail-closed schema validation, secret scan, payload size limits, redaction rule coverage.

6. CI policy
- Pull request gate MUST fail on any error-level contract violation.
- Deprecated field use is warning-level until next major cutoff date, then error-level.
- All four target platforms MUST pass projection checks in the same pipeline run.

## 10) Open questions

1. Should schema registry URIs be local-only paths, or also support remote immutable URIs for released packs?
2. What is the exact migration window length for v2 compat mode (for example, 2 minor releases vs date-based cutoff)?
3. Should cookbook workers support per-worker modelHints overrides, or remain centrally controlled by orchestrator policy?
4. Should handoff payload integrity use mandatory signatures in Wave 1, or stay optional until distributed runtime rollout?
5. Which fields should be mandatory in registry compatibility beyond supportedPlatforms (for example, testedOnVersions)?
6. Do we require deterministic key ordering and normalized YAML formatting as part of checksum generation rules?
