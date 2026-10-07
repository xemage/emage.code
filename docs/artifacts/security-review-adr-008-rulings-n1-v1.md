# Artifact: security-review-adr-008-rulings-n1-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; recorded by the orchestrator from the reviewer's report, because the
  agent has no write tool)
- **Task**: T584 (plan-102), Security Engineer phrase check of note N1
- **Date**: 2026-10-07
- **Based on**: `docs/artifacts/adr-008-rulings-p40-p43-v2.md` §3 (N1, N2, N3 as carried from v1 §9);
  `docs/artifacts/adr-008-rulings-p40-p43-v1.md` §10; `implementation/knowledge/skills/validation-gates/SKILL.md`
  `:15–104`; `implementation/knowledge/instructions/security-guidelines.md` (Rails, Immutable Security Constraints,
  Security Review Workflow); `docs/artifacts/conditional-pass-semantics-v4.md` §1.5.

## Verdict

**PASS.**
- No phrase in N1 relaxes or reorders a security criterion.
- No phrase lets another document's criteria admit a security finding as a CONDITIONAL_PASS condition when
  `validation-gates` § Verdict Rules or `security-guidelines.md` excludes it.
- N1 only ever moves a verdict toward the stricter value.

The reviewer could not construct a reading under which the "documented mitigations" route, or another document's
CONDITIONAL_PASS row, admits an excluded security finding.

## Findings (all `SECURITY:LOW`, optional; all adopted in v3)

| # | Phrase | Issue | Change adopted in `adr-008-rulings-p40-p43-v3.md` |
|---|---|---|---|
| F1 | N1: "every applicable set of criteria admits PASS"; "None of them makes another less strict." | "them" and "every applicable set" could be read as leaving out `validation-gates`' own rules. A security high at the Integration gate might then appear to reach PASS. The reading has to ignore the sentence before it and `:70` | "…every applicable set of criteria, the rules above included, admits PASS…"; "No set of criteria, the rules above included, makes another less strict." |
| F2 | N1: "Other documents also state verdict criteria for two of the gates:" | Reads as an exhaustive list and omits the Security gate's own criteria (`security-engineer.md:151–153`, `/security-audit:67`). That gate is owned by FU-6; S4 is jointly satisfiable | "Other documents also state verdict criteria; this note covers two of the gates:" |
| N2 | N2: "for a high finding with a documented mitigation" | The paraphrase leaves out that `validation-gates:70` forbids a mitigated security high. The outcome stays FAIL anyway (Must Fix, plus most-restrictive) | "for a high finding outside the security category with a documented mitigation" |

**N3** does not touch security criteria. It can only tighten a verdict, and the existing "security test failures"
FAIL trigger in `testing-strategy` is untouched.

The flagged "§ Criteria from the executor's own documents" citation has no security effect. The architect resolved it
in v3 by citing it as a paragraph.

## Orchestrator verification of the reviewer's unverified items

The orchestrator checked these at `develop` `c0138a7`, where `implementation/` is identical to `a54bbba`:
- `### Severity Definitions` occurs once in `validation-gates/SKILL.md`, at `:72`.
- The headings N1 cites exist: `code-review/SKILL.md:112`; `testing-strategy/SKILL.md:221` and `:231`;
  `qa-engineer.md:112`.
- `security-engineer.md:151–153` and `/security-audit.md:67` match the text F2 relies on.
- The v2→v3 diff of the edit blocks contains exactly F1 (two phrases), F2, the N2 point and the citation fix.
  P1–P3 are byte-identical.
