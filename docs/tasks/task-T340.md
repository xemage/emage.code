# Task T340 — Investigate GitLab merge-API phantom-ancestry on `release/* → main` merges

**ID:** T340
**Owner:** orchestrator, devops-engineer
**Status:** done
**Completed:** 2026-08-07
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-07
**Based on:** `docs/tasks/task-T331.md`, `docs/tasks/task-T339.md` (both incidents),
`docs/plans/plan-019-main-develop-drift-detection.md` (precedent: T331's own recommendation was
documented, not immediately executed, then picked up as a dedicated plan in a later session — this
task gives the same treatment to T339's flagged follow-up)

## Objective
Determine the actual root cause, inside GitLab's merge-request merge API, of why
`release/vX.Y.Z → main` merges have twice (T331 on MR !103, T339 on MR !109) produced a `main`-side
merge commit whose second parent is a GitLab-materialized commit — content/tree-identical to the
real `develop`/`release` branch tip, but NOT the same commit object and NOT a genuine git-ancestry
descendant of it. Produce a set of concrete, evaluated remediation options with a recommendation,
so this stops recurring on every future `release/* → main` sync regardless of the content-drift
gate plan-019 already shipped (which detects drift but does not address this ancestry mechanism).

## Context
- Phase: Investigation (read-only; no code, CI, or branch changes in scope for this task)
- Latest relevant checkpoint: `docs/checkpoints/checkpoint-release-v6.6.0.md`
- This is explicitly a "worth a dedicated investigation" follow-up flagged twice now: once in
  T331's outcome note (which became plan-019 — but plan-019 addressed *detecting* main/develop
  content drift, not this specific *ancestry* mechanism), and again verbatim in T339's "Flagged
  follow-up" section.
- Known facts already independently verified (do not re-derive, cite and build on them):
  - MR !103 (T331): `main` tip `5d5fd00` has parents `febd85a` (old `main` tip) and `6b2d680`
    (GitLab-materialized; tree-identical to `develop`'s `f75335c`, but `f75335c` is not its
    ancestor).
  - MR !109 (T339): because of the above, `git merge-base(origin/main, origin/develop)` resolved to
    the pre-T331 divergence point `363aeb8` (v6.0.3-era) instead of the true v6.5.0 reconciliation
    point, re-surfacing stale 3-way-merge conflicts on 5 files that were not actually in conflict
    (`main` and `develop` were content-identical going in).
  - Both times, the GitLab API's own `squash` field in the merge response was misleading (read
    `True` even when `squash=false` was explicitly passed and the resulting commit demonstrably has
    2 real parents) — this may or may not be related to the same underlying mechanism; determine if
    it is.
  - Project settings: `merge_method: merge`, `squash_option: default_on`, `main` protected
    (push=[No one], merge=[Maintainers]), merges performed via `glab api -X PUT
    projects/:id/merge_requests/:iid/merge` with `squash: false` explicit in the request body both
    times.

## Inputs
- `docs/tasks/task-T331.md`, `docs/tasks/task-T339.md` — full incident narratives, exact SHAs
- `docs/plans/plan-019-main-develop-drift-detection.md` — what is already mitigated (content drift
  detection) vs what is NOT (this ancestry mechanism itself)
- Live repo history: `febd85a`, `6b2d680`, `5d5fd00`, `f75335c`, `c14bf79`, `b866a77` (use
  `git cat-file -p <sha>`, `git log --parents`, `git show <sha>:<path>` as needed — read-only)
- GitLab project `em-age/emage.code` via `mcp__gitlab`/`glab api`: MR !103 and MR !109 full merge
  metadata (`GET projects/:id/merge_requests/:iid`, `.../merge_ref`, `.../commits`), project
  settings (`GET projects/:id` for `merge_method`, `squash_option`, `merge_commit_template`,
  `squash_commit_template` if present)
- GitLab's own documentation on merge methods (`merge`, `rebase_merge`, `ff`) and the semantics of
  the `/merge` API endpoint, `merge_commit_template`, and `merge_ref` — fetch via `mcp__fetch` or
  `WebFetch` against GitLab's official docs (read-only, no auth required for public docs)

## Constraints
- **Read-only investigation.** No git push, no MR actions, no branch creation on the real
  `main`/`develop`, no `.gitlab-ci.yml`/script changes. If a fix ultimately requires code/config
  changes, propose it as a follow-up task — do not implement it inside this task.
- Run inside an isolated git worktree (already provided by the orchestrator's dispatch) — do not
  touch the shared checkout.
- Token budget: ≤ 80k (Architecture-tier budget per `AGENTS.md` Token Governance — this is
  analysis, not implementation).
- Cite evidence for every claim (exact commands run and their output, or exact doc URLs quoted) —
  do not assert GitLab's internal behavior without either reproducing it against this repo's real
  data or citing GitLab's own documentation. If something cannot be verified, say so explicitly
  rather than guessing.

## Expected Outputs
- This task file (`task-T340.md`), with a completed "Findings" section (added by the agent) and an
  "Outcome" section (finalized by the orchestrator) containing:
  1. The precise mechanism (which GitLab merge-API code path / setting / behavior produces the
     materialized non-ancestor commit)
  2. Why it happens specifically on `merge_method: merge` with an explicit `squash: false` override,
     and whether `squash_option: default_on` at the project level is implicated
  3. A list of concrete remediation options (e.g.: change `merge_method` to `ff`-only for this
     branch pattern; merge `release/* → main` via local `git merge --no-ff` + direct push instead of
     the API `/merge` endpoint; accept the phantom-ancestry as permanent and rely solely on
     plan-019's content-based drift gate; use `merge_ref` first and fast-forward main onto it;
     something else found during research), each with a one-line tradeoff
  4. A clear recommendation (or an explicit "insufficient evidence to recommend one option" if that
     is the honest conclusion)
- If the recommendation implies a concrete follow-up implementation, a **new pending task row**
  proposed for `active-tasks.md` (not created yet — proposed only, for orchestrator/user approval),
  following the same Plan-Approve-Execute pattern plan-019 used.

## Acceptance Criteria
- [ ] Root-cause mechanism stated with cited evidence (repo command output and/or GitLab doc
      quotes), not speculation
- [ ] Confirms or refutes whether the misleading `squash` API response field (noted in both prior
      incidents) shares the same root cause as the phantom-ancestry commit, or is unrelated
- [ ] At least 3 remediation options evaluated with tradeoffs
- [ ] One clear recommendation, or an explicit statement that evidence is insufficient
- [ ] No destructive or state-changing git/GitLab operations performed during the investigation
- [ ] No new tags, branches (beyond the disposable investigation worktree), or MRs created against
      the real repo

## Blocker Protocol
Report blockers per `AGENTS.md`: type (`technical` | `dependency` | `unclear_requirements` |
`external`) + severity (`critical` | `major` | `minor`). Max 2 retries before escalating to the
orchestrator. If GitLab's public docs don't cover the specific materialized-commit behavior
observed, that is itself a valid (and expected) finding — report it as such rather than treating it
as a blocker.

## Findings

### 0. Method note
All commands below were run read-only inside this task's isolated worktree
(`.claude/worktrees/agent-a51089c656d5a3c14`) against `origin` (`https://gitlab.com/em-age/emage.code.git`,
already fetched). No push, branch, tag, or MR write operation was performed. `glab api` calls used
were all `GET` (read-only), routed through the pre-authenticated `glab` CLI session already present
in the environment (`glab auth status` reported an "Invalid token" *warning* but `GET` calls
succeeded regardless — noted, not investigated further, since it did not block read access).

Note on artifact location: this task's own worktree was branched at commit `c14bf79` (before the
`ca30dca`/`6efcb64` commits on `develop` that filed T337–T340 and updated the ledger), so
`docs/tasks/task-T340.md`, `task-T339.md`, and later files did not exist inside this worktree. Per
the delegation brief the agent read the canonical copies from the shared checkout — read-only, no
writes there — and reproduced this file's pre-Findings content verbatim before appending Findings,
so nothing was lost and no other file was touched.

### 1. Independent re-verification of the cited SHAs (repo plumbing)

All six SHAs cited in T331/T339 are real, reachable commit objects on `origin`:
```
$ git cat-file -t febd85a / 6b2d680 / 5d5fd00 / f75335c / c14bf79 / b866a77
commit  commit  commit  commit  commit  commit
```

Parent graphs (`git log --parents --oneline -1 <sha>`):
```
5d5fd00 febd85a 6b2d680   release(v6.5.0): sync main with develop
6b2d680 febd85a           release(v6.5.0): sync main with develop
c14bf79 5d5fd00 25fa98e   Merge branch 'release/v6.6.0' into 'main'
25fa98e 5d5fd00           release(v6.6.0): sync main with develop
f75335c 88c6ce8 43194bf   Merge branch 'docs/release-v6.5.0' into 'develop'
b866a77 82f98ab c9e2436   Merge branch 'bugfix/main-develop-drift-tag-fetch-force' into 'develop'
```
This confirms T331/T339's parent-relationship narrative exactly: `6b2d680` (cited as
GitLab-"materialized") has a **single** parent, `febd85a` (the *old* `main` tip) — not `f75335c`
(develop's real tip). Same pattern for `25fa98e`/`b866a77` in the T339 incident: `25fa98e`'s single
parent is `5d5fd00` (old `main` tip), not `b866a77` (develop's real tip).

Tree identity, independently confirmed via `git show -s --format=%T`:
```
6b2d680 tree = 453c18c0506e59057036d1137851fd4912b78217
f75335c tree = 453c18c0506e59057036d1137851fd4912b78217   (IDENTICAL)
25fa98e tree = 5420fa084db7863202caec9c636566b3b36d1f63
c14bf79 tree = 5420fa084db7863202caec9c636566b3b36d1f63   (IDENTICAL to 25fa98e; c14bf79 is the
                                                             merge commit itself, tree naturally
                                                             matches its own squash-commit parent
                                                             since squash content == merge content)
```
Ancestry, independently confirmed via `git merge-base --is-ancestor` (exit code, not text output):
```
$ git merge-base --is-ancestor f75335c 6b2d680 ; echo $?
1        # f75335c is NOT an ancestor of 6b2d680 — confirmed
$ git merge-base --is-ancestor b866a77 25fa98e ; echo $?
1        # b866a77 is NOT an ancestor of 25fa98e — confirmed
```
**T331/T339's factual narrative is independently re-confirmed, not taken on faith.**

### 2. The actual mechanism: this is GitLab's documented squash-then-merge behavior, not an
   unexplained "materialization"

Digging one level further than T331/T339 did (they stopped at "GitLab materialized a commit"),
the commit objects themselves identify what `6b2d680`/`25fa98e` are:
```
$ git cat-file -p 6b2d680
tree 453c18c0506e59057036d1137851fd4912b78217
parent febd85a3bca5a17ed67e13b1d367cf88ae8e155a
author em age <emage@email.de> 1786088060 +0000
committer em age <emage@email.de> 1786088060 +0000

release(v6.5.0): sync main with develop
```
`6b2d680`'s author/committer timestamp (`1786088060`) is **byte-identical** to `5d5fd00`'s
timestamp (`1786088060`) — the two commits were created in the same instant. Same pattern for
`25fa98e`/`c14bf79` (both `1786098271`). This is the fingerprint of GitLab's server-side merge
worker creating both commits back-to-back in one API call, not two independent local commits from
two different sessions.

Querying GitLab's own MR records (`glab api projects/em-age%2Femage.code/merge_requests/103` and
`/109`, both read-only `GET`) makes this unambiguous — GitLab **names** these commits explicitly:
```
MR !103: "merge_commit_sha":"5d5fd007c7f0065a593dc7014d29ce6608c73d6f",
         "squash_commit_sha":"6b2d680c5499d0e12f1e4c9f910bcfc2984728d6",
         "squash":true, "squash_on_merge":true,
         "sha":"1f4fe60a62fa8dc1e8e0dfcfbf1ead98561ac893"   (real MR source-branch HEAD at merge time)

MR !109: "merge_commit_sha":"c14bf7903b8cdaa1e845a57069c7fc5888b64bd9",
         "squash_commit_sha":"25fa98efe5c8c9aea9a72d40b9de651d085a1e7b",
         "squash":true, "squash_on_merge":true,
         "sha":"618cd86be649ac22cb5f3df7aa1e2c61e2ea586a"    (real MR source-branch HEAD at merge time)
```
**`6b2d680` and `25fa98e` are GitLab's own `squash_commit_sha` for these MRs.** They are not an
unexplained "materialization" — they are the normal, documented squash commit GitLab creates when
squashing a merge request, confirmed both by GitLab's own API field naming and by independently
inspecting the commit objects' parentage/timestamps.

GitLab's own docs describe exactly this two-commit shape, quoted verbatim
(`https://docs.gitlab.com/user/project/merge_requests/methods/`, "Merge commit" section):
> "By default, GitLab creates a merge commit when a branch is merged into main. **A separate merge
> commit is always created, regardless of whether or not commits are squashed when merging.** This
> strategy can result in both a squash commit and a merge commit being added to your main branch."

And (`https://docs.gitlab.com/user/project/merge_requests/squash_and_merge/`, "Squash and merge
workflow"):
> "Each time a branch merges into your base branch, up to two commits are added: **The single
> commit created by squashing the commits from the branch.** A merge commit, unless you have
> enabled fast-forward merges in your project."

The same page gives the literal git-command equivalent of what GitLab's squash-then-merge-commit
combination does (`https://docs.gitlab.com/user/project/merge_requests/methods/`, "Merge commit"
section, squash-merge diagram caption):
```
git checkout `git merge-base feature main`
git merge --squash feature
git commit --no-edit
SOURCE_SHA=`git rev-parse HEAD`
git checkout main
git merge --no-ff $SOURCE_SHA
```
This is exactly what the SHAs show happened. The real MR source-branch tip at merge time
(`1f4fe60a` for !103, `618cd86` for !109) was **not** develop's plain tip — it was a real,
independently-verified 2-parent merge commit created during conflict resolution:
```
$ git log --parents --oneline -1 1f4fe60a
1f4fe60 f75335c febd85a   release(v6.5.0): merge main into release/v6.5.0, resolve GitFlow drift
$ git show -s --format=%T 1f4fe60a
453c18c0506e59057036d1137851fd4912b78217   (== f75335c's tree, == 6b2d680's tree)

$ git log --parents --oneline -1 618cd86
618cd86 b866a77 5d5fd00   release(v6.6.0): merge main into release/v6.6.0, resolve GitFlow drift
```
Because conflict resolution merged `main` into the release branch *first* (standard GitLab-conflict
resolution practice: merge target into source, resolve, push), by the time GitLab computed
`git merge-base(release/vX.Y.Z, main)` for the squash step, `main`'s own tip (`febd85a` / `5d5fd00`)
was **already a direct parent of the release branch's tip** (`1f4fe60a` / `618cd86`) — so
`merge-base = main`'s own tip exactly. Squashing from that merge-base necessarily produces a
squash commit parented *only* on `main`'s tip, with the tree of the release branch's resolved
content (which is develop's content) — discarding the real, already-merged-in ancestry to
`f75335c`/`b866a77` that existed one commit earlier on the (now-squashed-away) branch. This is not
a bug in GitLab's squash implementation; it is squashing doing exactly what squashing is documented
to do (flatten multi-commit history into one commit rooted at the merge-base) — applied to a branch
whose "one logical commit" already happened to *be* a real merge of main into develop's content.

### 3. Whether the misleading `squash` field is the same root cause: CONFIRMED same cause,
   and the field was not actually misleading

T331/T339 both flagged: "the API's `squash` field read `True` even when `squash=false` was
explicitly passed." Findings §2 shows this field is **the same root cause**, not a separate one —
`squash: true` / `squash_on_merge: true` / a populated `squash_commit_sha` are GitLab accurately
reporting that squashing genuinely occurred. The field was not lying or "misleading" in the sense of
contradicting reality; the prior investigators' surprise came from an unverified assumption that
`squash: false` in the request body had taken effect. It demonstrably had not, on both occasions.

**What is NOT independently verifiable from this task:** the exact raw HTTP request body/headers
that were sent by the historical `glab api -X PUT .../merge` invocations in the T331/T339 sessions —
those requests were not logged or preserved anywhere in this repo, and cannot be replayed
non-destructively (replaying would perform a real merge action). GitLab's own merge-endpoint
documentation (`https://docs.gitlab.com/api/merge_requests/#merge-a-merge-request`, "Merge a merge
request" attributes table, fetched and quoted verbatim) states plainly:
> `squash` — boolean — No — "If true, squash all commits into a single commit on merge."

Per this doc text alone, omitting the field or passing `false` should not force squashing. The
project's `squash_option` is `default_on`, which GitLab's own UI docs
(`https://docs.gitlab.com/user/project/merge_requests/squash_and_merge/`, "Configure squash options
for a project") define as:
> "**Encourage**: Squashing is allowed **and selected by default, but can be disabled**."

— i.e. `default_on` is documented as overridable, not equivalent to `Require` ("Squashing is always
performed... users cannot change it," which this project is *not* set to). So per GitLab's own
documented semantics, `squash: false` sent to `/merge` on a `default_on` project should have
produced a non-squashed, real 2-parent merge (with `1f4fe60a`/`618cd86` — the branch's *actual* tip
— as the second parent, not a squash commit), and it did not, twice.

Third-party evidence (not GitLab's own docs, so weighted lower) of the general class of
problem — GitLab API/CLI callers passing an explicit `squash` value not reliably overriding
project/MR-level squash configuration — was found via a public community bug report,
[`backstage/backstage#32787`](https://github.com/backstage/backstage/issues/32787) ("Make squash
parameter conditional to respect GitLab project settings"), which documents unexpected interaction
between a caller-supplied `squash` value and project-level squash settings (in that report's case,
`squash_option: always`/"Require", the opposite edge from ours). Also found:
[`gitlab-org/cli#7370`](https://gitlab.com/gitlab-org/cli/-/issues/7370) ("Parameter
squash-before-merge doesn't work"), documenting a related-but-distinct `glab` (the same CLI tool
used for both T331 and T339's merges) bug where a squash-related flag passed to `glab mr create` is
silently not applied to the created MR. Neither report is an exact reproduction of "raw `glab api -X
PUT .../merge` with `squash: false` on a `default_on` project still squashes" — so **it cannot be
conclusively proven, from public sources alone, whether this specific failure mode is (a) a
GitLab server-side quirk where the per-call `squash` override does not reliably take effect under
`default_on` (plausible, given the `backstage` and `gitlab-org/cli` precedents of squash-parameter
handling being unreliable elsewhere in GitLab's stack), or (b) a client-side issue in how the
historical `glab api` invocations actually serialized the `squash` field (e.g., a bare `-f
squash=false` form field vs. a typed/JSON boolean) that happened not to reach the server as an
effective `false`.** This is exactly the kind of unresolved point the task brief asked to flag
rather than guess at.

**Practical conclusion, independent of which of (a)/(b) is true:** the demonstrated, 2-for-2 failure
rate of "explicit `squash: false` via `glab api -X PUT .../merge`" on this project means that call
pattern cannot currently be trusted to produce a non-squashed merge, regardless of root cause. Any
remediation must either stop depending on that specific call succeeding as requested, or add a
verification step that catches it when it doesn't (see §4).

### 4. Remediation options (≥3, with tradeoffs)

1. **Verify-then-fix at merge time (cheapest, recommended as the immediate step).** After calling
   `/merge`, immediately `GET` the MR again and assert `squash == false` and
   `squash_commit_sha == null`. If GitLab squashed anyway, the merge has already happened (GitLab's
   `/merge` is not reversible via a "retry" without a revert) — so this option's real value is
   *catching the failure at the moment it happens*, not preventing it. Pair with a documented
   runbook step: if the assertion fails, immediately open a follow-up "ancestry restore" MR (a
   trivial no-op commit on `main` with the true source tip as an explicit second parent via
   `git merge --no-ff <true-source-sha> -s ours` locally then pushed through a maintainer path) so
   the next sync's `merge-base` is correct going forward, instead of discovering the problem a whole
   release cycle later as happened in T339.
   *Tradeoff:* does not prevent the squash from happening; only shortens the detection loop from
   "next release's phantom conflict" (T339's actual experience) to "immediately." Very low
   implementation cost (a few lines in the existing release runbook / a follow-up script).

2. **Bypass the `/merge` API entirely for `release/* → main` syncs; merge and push locally
   instead.** Perform `git merge --no-ff release/vX.Y.Z` locally (real 2-parent merge, guaranteed
   correct ancestry — no squash step exists in this path at all) and push directly to `main`.
   *Tradeoff:* `main` is currently protected with `push=[No one]` — this exact setting is *why*
   MR-based merges were used in the first place. This option requires either a scoped, audited
   exception (e.g., a dedicated deploy token/service account permitted to push only
   fast-forward/no-squash merges to `main`, only for this workflow) or a temporary manual unprotect
   step for each release sync — both weaken the protected-branch invariant and need careful scoping
   to avoid becoming a general bypass hole. Highest reliability, highest process/security cost.

3. **Use `GET .../merge_ref` to inspect the would-be merge commit before committing to the API
   `/merge` call, and fast-forward `main` onto it out-of-band if the ancestry is confirmed
   correct.** `merge_ref` ("Merge to default merge ref path") produces
   `refs/merge-requests/:iid/merge`, documented as "the state the target branch would have if a
   regular merge action was taken" without touching the actual target branch. Inspecting this ref's
   parents *before* calling `/merge` would surface whether GitLab intends to squash before the
   action is irreversible.
   *Tradeoff:* `merge_ref`'s own docs do not confirm it reflects the *squashed* result specifically
   (it describes "a regular merge action," and squash is documented as a distinct, additional step —
   see §2) — this option's effectiveness is not fully verified and would need a live (out-of-band,
   non-production) experiment to confirm before relying on it.

4. **Change the project's `squash_option` to `never` ("Do not allow") — but only if scoped
   correctly.** At the *project* level this eliminates squashing entirely, guaranteeing this failure
   mode can never recur on any MR, including `release/* → main`.
   *Tradeoff:* `squash_option` is a **project-wide** setting in GitLab — there is no branch-pattern
   scoping for it. Disabling squash project-wide removes a feature the team may want for ordinary
   `feature/* → develop` MRs (clean single-commit history for small changes), which is a real
   behavior change beyond the scope of fixing `release/* → main` specifically.

5. **Accept the phantom-ancestry commit as permanent and rely solely on plan-019's content-based
   drift gate (status quo, zero-cost).**
   *Tradeoff:* Zero implementation cost, and plan-019 already prevents the *user-visible* incident
   (surprise conflicts / silent drift) from recurring by using content comparison instead of
   `merge-base` ancestry. But it does not fix `git merge-base --is-ancestor` itself, which remains a
   false-negative-prone signal for `main`/`develop` reconciliation anywhere else it might be used in
   this repo's tooling in the future.

### 5. Recommendation

Adopt **Option 1** (post-merge verification + documented recovery runbook step) as an immediate,
low-cost addition to the existing release runbook — it directly targets the actual observed
failure mode (squash occurring silently despite an explicit override attempt) and converts a
release-scale surprise (T339's actual experience: discovered a full release cycle later) into an
immediate, actionable one.

Do **not** adopt Option 2 (bypass `/merge` via direct push) or Option 4 (disable squash project-wide)
as a first move — both have real, non-trivial security/process costs (weakening `main`'s
`push=[No one]` protection, or removing a feature used elsewhere) that are not justified until
Option 1 has been tried on a real future `release/* → main` sync and shown to be insufficient.

Option 5 (accept as permanent) is not a standalone recommendation — plan-019 already effectively
implements this as the *current* mitigation for the user-visible symptom, and that remains correctly
in place regardless of this task's outcome; these findings do not suggest plan-019 should be
reverted or changed.

### 6. Proposed follow-up task (for orchestrator/user approval — not created by this task)

**Proposed `active-tasks.md` row:**

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T341 (proposed) | Add post-merge squash/ancestry verification step to release/*→main runbook | devops-engineer | pending | P2 | — | 2026-08-07 |

**What T341 would do:** Add a small, scripted verification step (a short addition to the existing
release runbook and/or a `glab api` follow-up call immediately after every `release/vX.Y.Z → main`
merge) that fetches the just-merged MR's own record and asserts `squash == false` and
`squash_commit_sha == null`; if the assertion fails, the runbook directs the operator to immediately
open a small "ancestry restore" follow-up so the *next* release sync's `git merge-base` is correct,
rather than discovering the drift a full release cycle later as happened in T339. Deliberately
scoped small (verification + documented manual recovery step, not a new CI gate or a
branch-protection change) so it can be evaluated on the next real `release/* → main` sync before
deciding whether heavier options (§4, options 2 or 4) are warranted.

## Outcome (2026-08-07)
Root cause identified and independently verified against real repo data and GitLab's own
documentation: `6b2d680` (T331/MR !103) and `25fa98e` (T339/MR !109) are GitLab's own documented
`squash_commit_sha` for those MRs, not an unexplained "materialization." Squashing occurred despite
an explicit `squash: false` override passed via `glab api -X PUT .../merge`, both times, on a
project with `squash_option: default_on` — whether this is a GitLab server-side quirk or a
client-serialization issue in the historical `glab api` calls could not be conclusively determined
from public sources, and is reported as unresolved rather than guessed at. Recommendation: adopt
the cheapest option (post-merge `squash`/`squash_commit_sha` verification + documented recovery
runbook step), not the heavier options (bypass `/merge` via direct push, or disable squash
project-wide) until the cheap option is tried on a real sync and shown insufficient. A follow-up
task (T341) is proposed, not created — awaiting orchestrator/user decision on whether to schedule it,
per the same Plan-Approve-Execute pattern that turned T331's recommendation into plan-019.
