---
scope: general
title: "Before dispatching a nested Agent-tool call, check the assignee actually has the Agent tool"
tags: [agent-dispatch, tool-grants]
---

## The gap this guards against

Most specialist agent roles in this harness do not carry the tool that lets one dispatched session
launch another (an in-process nested agent dispatch) — only orchestrator-shaped roles do by
default. A task whose objective requires that capability cannot simply be handed to a specialist
role and assumed to work; the assignee's own declared tool grant has to be checked explicitly
first, not inferred from the role's general competence at the task's subject matter.

## What to do when the gap is real

Do not silently widen a role's tool grant to route around a missing capability for one task — that
is a standing, cross-task change to a role's permissions being made to solve a local problem.
Instead, reassign the specific slice that needs the capability to a role that already has it, or
have the orchestrating role execute that bounded slice directly, and record which of the two was
chosen and why.
