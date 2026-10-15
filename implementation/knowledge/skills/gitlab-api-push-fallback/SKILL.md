---
name: gitlab-api-push-fallback
description: "Publish a branch, open and merge its MR, and (with approval) create a tag through the GitLab API when git push fails with an authentication error. Use when push reports 'Authentication failed' or 'HTTP Basic: Access denied' while glab API calls still work."
maturity: experimental
---

# GitLab API Push Fallback

## When to Use

- `git push` to GitLab fails with `Authentication failed`, `HTTP Basic: Access denied` or `glab auth git-credential: "erase" is an invalid operation`, while `glab api` calls still work.
- The user asks to publish a branch or tag and a working `git push` is not available.
- Not for protected-branch rejections (`You are not allowed to push code to protected branches`): those need the branch and MR flow of the `git-workflow` rule, not this fallback.

## Inputs

Required:
- A local branch with committed changes (a worktree is fine).
- The base branch (usually `develop`) and the remote name (`origin`).
- The commit message (Conventional Commits; the attribution lines the session requires).
- `glab` already authenticated for the project. The agent never reads, prints or changes tokens or credential configuration.

Optional:
- A tag name, used only after the user explicitly approved that tag.
- An MR title and description.

## Procedure

1. Retry the push once after a pause of one to two minutes. The `erase` failure is a transient on the GitLab side; more immediate retries do not help. If the retry succeeds, stop: this skill is not needed.
2. Do not touch `glab` or git credential configuration (helpers, tokens, `glab auth`) without asking the user first, each time. Do not force-push.
3. Build the change list from the local branch: `git diff --no-renames --name-status <base>..HEAD`. Map `A` to `create`, `M` to `update`, `D` to `delete`; for every non-deleted file read its content from the working tree. Only text files go through this path; stop and ask for binary files.
4. Create the branch commit: `POST projects/:id/repository/commits` with `branch`, `start_branch` (the base), `commit_message` and the `actions` list. One API commit replaces the local commits (the history is squashed).
5. Verify: `git fetch origin <branch>` and compare `FETCH_HEAD^{tree}` with `HEAD^{tree}`. If they differ, stop and report; do not continue.
6. Open the MR: `POST projects/:id/merge_requests` with `source_branch`, `target_branch`, a title and a description. Add the attribution line the session requires.
7. Merge only when `detailed_merge_status` is `mergeable` and the head pipeline is `success`, and pin the verified commit: `PUT projects/:id/merge_requests/<iid>/merge` with `sha=<verified sha>`. Never merge on `unchecked` or `ci_still_running`.
8. Tags and releases go through the API only after the user explicitly approved that tag and its target: `POST projects/:id/repository/tags` with `tag_name` and `ref`. Never delete or move a tag, never force.
9. Tell the user that the API fallback replaced a push, and which commit sha the API created.

## Success Criteria

- The remote branch tree equals the local tree (step 5).
- The MR exists and its pipeline is green before it is merged.
- No credential configuration was changed and no force push was used.
- The user was told that the API fallback replaced a push.

## Examples

- Push of `agent/devops-engineer/T640` fails with `Authentication failed` twice, a minute apart. Build the actions from `git diff --no-renames --name-status origin/develop..HEAD`, POST them to the commits API with `start_branch=develop`, fetch the branch and compare tree ids (equal), open the MR, wait for `mergeable` with a green pipeline, merge with the pinned sha.
- The user approved tag `v8.0.0` on `main`: after the release merge is verified, `POST projects/:id/repository/tags` with `tag_name=v8.0.0&ref=main`.
