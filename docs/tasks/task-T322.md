# Task T322 — Check whether CWSO has actually published the images (STOP FIRST / WAIT-AND-CHECK)

**ID:** T322
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T321
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md

## Objective
Determine, with real evidence, whether CWSO's team has published all 4 images
(`orchestrator`, `git-shadow`, `merge-engine`, `rollout`) to
`registry.gitlab.com/em-age/emage.code.cwso/...` in response to T321's hand-off. This is a CHECK
that may be run at any point after T321 — including much later — and may be re-run any number of
times. Do NOT proceed to Wave 5 (T323+) on an assumption.

## Inputs
- `../CWSO`'s GitLab Container Registry (public, no auth required for reads)

## Expected outputs
- A READY / NOT READY verdict per image, with literal command output as evidence.

## Acceptance criteria
1. Run (adjust method if the bare curl approach returns 401 — use the `glab api` registry
   endpoints instead, whichever actually returns a real answer):
   ```
   curl -s -I https://registry.gitlab.com/v2/em-age/emage.code.cwso/orchestrator/manifests/latest
   curl -s -I https://registry.gitlab.com/v2/em-age/emage.code.cwso/git-shadow/manifests/latest
   curl -s -I https://registry.gitlab.com/v2/em-age/emage.code.cwso/merge-engine/manifests/latest
   curl -s -I https://registry.gitlab.com/v2/em-age/emage.code.cwso/rollout/manifests/latest
   ```
   or:
   ```
   glab api "projects/em-age%2Femage.code.cwso/registry/repositories"
   glab api "projects/em-age%2Femage.code.cwso/registry/repositories/<id>/tags"
   ```
2. If all 4 images exist with real tags: report READY. This unblocks T323.
3. If any are missing: report NOT READY, name exactly which image(s) are missing, and STOP. Do
   NOT mark this task done in a way that implies Wave 5 can proceed. Do NOT fabricate readiness.
4. Per R8, the literal check output (whichever method used) is pasted into Execution notes with
   an explicit READY/NOT READY verdict per image.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries. A "NOT
READY" result is not a blocker requiring escalation — it's an expected, valid outcome; simply
report it and stop.

## Execution notes

Executed: 2026-08-03

### Check method
`glab api "projects/em-age%2Femage.code.cwso/registry/repositories"`

### Literal output
```json
[
    {
        "id": 11642240,
        "name": "orchestrator",
        "path": "em-age/emage.code.cwso/orchestrator",
        "project_id": 82090928,
        "location": "registry.gitlab.com/em-age/emage.code.cwso/orchestrator",
        "created_at": "2026-06-09T20:14:42.009Z",
        "cleanup_policy_started_at": null,
        "status": null
    },
    {
        "id": 11642241,
        "name": "git-shadow",
        "path": "em-age/emage.code.cwso/git-shadow",
        "project_id": 82090928,
        "location": "registry.gitlab.com/em-age/emage.code.cwso/git-shadow",
        "created_at": "2026-06-09T20:14:47.584Z",
        "cleanup_policy_started_at": null,
        "status": null
    }
]
```

### Verdict per image
| Image | Status |
|-------|--------|
| orchestrator | PRESENT |
| git-shadow | PRESENT |
| merge-engine | **NOT PUBLISHED** |
| rollout | **NOT PUBLISHED** |

**OVERALL VERDICT: NOT READY**

Wave 5 (T323-T325) is blocked until CWSO's team acts on the T321 hand-off (T178/T179). This task
should be re-run after CWSO merges those tasks and a `main`-branch pipeline completes.

### Re-run (2026-08-03, after CWSO team completion)

Check method:
`glab api "projects/em-age%2Femage.code.cwso/registry/repositories?per_page=100"`

Literal output excerpt:
```json
[
    {"name":"orchestrator","id":11642240},
    {"name":"git-shadow","id":11642241},
    {"name":"merge-engine","id":12045010},
    {"name":"rollout","id":12045034}
]
```

Tag check output:
```
orchestrator: latest, v0.5.2
git-shadow: latest, v0.5.2
merge-engine: latest, v0.5.2
rollout: latest, v0.5.2
```

Re-run verdict per image:
| Image | Status |
|-------|--------|
| orchestrator | READY |
| git-shadow | READY |
| merge-engine | READY |
| rollout | READY |

**RE-RUN VERDICT: READY** — Wave 5 unblocked.
