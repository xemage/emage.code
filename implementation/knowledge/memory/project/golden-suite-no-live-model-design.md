---
scope: project
project_id: em-age/emage.code
title: "The golden suite deliberately never invokes a live, sampling model completion"
tags: [golden-suite, evaluation-design]
---

## The tension this design resolves

This project's roadmap sets two hard constraints in tension: a golden case's checker must return
binary pass/fail with no LLM-judged scoring, and re-running the suite on an unchanged tree must
produce an identical scorecard (deterministic). A checker that invokes a live agent or model
completion in-process is not run-to-run deterministic — model sampling, latency, and transient
infrastructure failures all vary — and is too slow and costly to run repeatedly at suite scale.

## The resolution

Each case's checker performs deterministic, scripted validation of a given end state and never
itself invokes a live, sampling model completion. A case's brief documents intent and may separately
be reused as literal input to a real live agent run in a different system as an authoring aid, but
the checker that actually grades pass/fail stays pure, offline, and repeatable. Source:
`docs/artifacts/golden-suite-format-v1.md` §2.
