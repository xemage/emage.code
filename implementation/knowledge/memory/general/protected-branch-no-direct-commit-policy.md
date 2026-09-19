---
scope: general
title: "No direct commits to the two protected branches, ever - not even a one-line docs edit"
tags: [branch-protection, branch-policy]
---

## The rule has no size or content exception

This harness's two integration branches are protected on the remote: the remote git host rejects
any direct push to either one, with no exception carved out for a change that is small, urgent, or
documentation-only. A single-file ledger-status edit requires exactly the same branch-plus-merge-
request flow as an application-code change — branch protection does not distinguish by diff size or
file type, and neither does this convention. This applies equally to changes an orchestrating role
makes directly, not only to changes made inside a dispatched agent's own isolated workspace.

## Recovery if it happens anyway

If a commit ends up directly on a local protected branch that is protected on the remote too, the
recovery is: create a new branch pointing at that commit, diff it against the remote branch to
confirm nothing unique would be lost, reset the local protected branch back to match the remote,
then push the new branch and open an ordinary merge request. Never force-push over the rejection,
and never discard the commit outright.
