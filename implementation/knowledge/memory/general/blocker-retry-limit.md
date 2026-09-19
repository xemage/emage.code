---
scope: general
title: "This harness's own blocker escalation limit: two retries, then escalate"
tags: [blocker-protocol, agent-behavior]
---

## The rule

Per this harness's own standing agent conventions, a blocker is classified by type (technical,
dependency, unclear-requirements, or external) and by severity, and an agent working a blocker
retries it at most twice before treating it as escalation-worthy rather than continuing to retry
silently. This applies to every agent role and every project this harness is deployed against — it
is not a convention any one project's own codebase defines for itself.

## Why a hard number, not a judgment call

A fixed retry ceiling exists so that "still trying" cannot silently substitute for "actually stuck."
An agent that has retried twice and still failed is expected to report the blocker upward — with its
type, severity, and what was already tried — rather than either giving up silently or looping
indefinitely on the same failing approach.
