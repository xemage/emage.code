# Artifact: release-rehearsal-t759-v1.md

> Immutable once produced; revisions bump `<N>`.

**Based on:** `docs/tasks/task-T759.md`; `docs/plans/plan-145-release-v10.md` (T759); `docs/artifacts/release-rehearsal-t706-v1.md` (the v9.0.0 rehearsal, the model followed); `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (SEC-T756-01); `docs/artifacts/ca-check-t765-v1.md` (read in part); `.gitlab-ci.yml` (`release`), `scripts/publish-release.py`, `scripts/verify-release-docs.py`, `docs/releases/v10.0.0.md`, `CHANGELOG.md`. All inputs as of `release/v10.0.0` at `bd3770f2`. CPython: `https://github.com/python/cpython/pull/160042.diff`, and `Modules/_ssl/distrusted_spki.h` and `Modules/_ssl.c` at tag `v3.12.16`.

**Author / mode:** DevOps Engineer, T759. Only this file was added to the repository. Nothing was pushed, and no tag or release was created on any GitLab project or in any real repository or worktree. No request reached GitLab's API, and no real token was used or read. The tag `v10.0.0` existed only inside the scratch container and was destroyed with it. `tests/golden/held-out/` was not checked out (sparse checkout) and not opened. Its blobs were inside the git bundle, as at T706, and went with the container.

**Basis marker:** **(V)** = run or read in this task. **(unverified)** = not checked.

## 1. Result

**The rehearsal passes, and the block is found. No defect, no blocker.**

- The job's `before_script` line and its `script` line both ran **verbatim** in the digest-pinned image, without `--skip-api`, and both exit 0. The script's real `main()` and real `urllib` opener sent real HTTPS requests with the `JOB-TOKEN` header to a double on loopback.
- The description sent equals `docs/releases/v10.0.0.md` byte for byte (40901 bytes).
- Item 6 holds: the entry lands below `## [Unreleased]`. Item 7 holds in the image's code, but the real commit range holds no reference or URL to escape (section 7).
- **`_ssl` (SEC-T756-01): found.** The image runs Python 3.12.16, and one denylisted key hash is in the built `_ssl` module once, as raw bytes, with its controls behaving (section 9). The rejection itself was not observed.

## 2. Host state and approval

| | Containers (`docker ps -a`) | Images (`docker images`) |
|---|---|---|
| Before | `portainer`, `hindsight` (both Up 3 days) | `portainer/portainer-ce:latest` `03f94a406496`, `ghcr.io/vectorize-io/hindsight:latest` `a0e937366261` |
| After | `portainer`, `hindsight` (both Up 3 days) | the same two, same IDs |

**The host reads the same afterwards** (V): `diff` of the before and after lists is empty for images and for container names. One container was used, on the first attempt, with no second attempt. `portainer` and `hindsight` were not touched beyond those two read commands. No volume, bind mount, prune or `--all` was used.

**Every `docker` command, in order** (each under `timeout`; `IMG` = `python:3.12-alpine@sha256:e064671ca452259bab50e8e2c7bd896e39e9a343bb06ca25234adf6fe18d0fc7`, `C` = `t759-rehearsal`):

1. `docker ps -a --format ...`; `docker images --format ...`
2. `docker pull IMG`
3. `docker run -d --name C --memory 1g --pids-limit 256 IMG sleep 2400`
4. `docker cp <payload> C:/rehearse`
5. `docker exec C sh -c 'mv /rehearse/wrap /wrap; mkdir -p /rehearse/out; ...'`
6. `docker cp step1.sh`, then `docker exec C sh /rehearse/step1.sh` (the `before_script`)
7. `docker network disconnect bridge C`
8. `docker cp step2.sh`, then `docker exec C sh /rehearse/step2.sh` (reachability check, origin, clone)
9. `docker exec C python3 -I /rehearse/sslcheck.py` (the one extra read-only command)
10. `docker cp step3.sh`, then `docker exec C sh /rehearse/step3.sh` (the job's `script` and the cases of section 5)
11. `docker cp step4.py`, then `docker exec C python3 -I /rehearse/step4.py` (the escaping examples)
12. `docker cp C:/rehearse/out/CHANGELOG.generated.md <scratchpad>`
13. `docker cp step5.sh`, then `docker exec C sh /rehearse/step5.sh` (the untrusted-server case with `SSL_CERT_FILE` unset)
14. `docker rm -f C`
15. `docker rmi IMG`
16. `docker ps -a --format ...`; `docker images --format ...`; `docker ps -a`; `docker images`

## 3. Environment (V)

| Item | Value |
|---|---|
| Job image | The digest above, the same in `.gitlab-ci.yml` `release`; pulled by digest |
| In the image | Python 3.12.16, OpenSSL 3.5.9, Alpine 3.24.4, uid 0, x86_64, Unicode database 15.0.0 (equals `SUBJECT_REVIEWED_UNICODE_VERSION`) |
| Git | `git~=2.54` resolved to `2.54.0-r0` on Alpine 3.24.4. Host git for the cross-check: 2.43.0 |
| Network | Connected only for the `before_script`. After the disconnect: only `lo`, no route, `gitlab.com` fails to resolve (`gaierror`), `1.1.1.1:443` fails (`OSError`) |
| Fake variables | `CI_JOB_TOKEN` and `CI_REGISTRY_PASSWORD` = `fake-job-token-t759`; `WIKI_TOKEN` = that value plus `-WIKI`; `CI_REPOSITORY_URL` = an https URL holding it on `localhost`; `CI=true`, `GITLAB_CI=true`, `CI_COMMIT_TAG=v10.0.0`, `CI_SERVER_HOST=localhost`, `CI_API_V4_URL=https://localhost:8443/api/v4`, `CI_PROJECT_ID=1`, `LC_ALL=C.UTF-8` |
| TLS of the double | A throwaway CA and `localhost` leaf made in the scratchpad for this run (EC P-256, 2 days), sent with `docker cp`, deleted from the scratchpad and gone with the container. `SSL_CERT_FILE` names that CA for the script line, and is **not** set during the `before_script`. Nothing related to eMudhra |
| Double | Python `http.server` with `ssl`, on `127.0.0.1:8443` (API) and `:8444` (redirect target). It logs method, path, headers with the fake value masked, whether `JOB-TOKEN` equals the fake value, and the body |
| Probes | `/wrap/git` and `/wrap/apk` first on `PATH`, as at T706: they log the variable names and how many variables hold the fake value, then `exec` the real binary |

**Scratch repository.** A bundle of `refs/heads/release/v10.0.0` and all tags (8.3 MB, 42 refs) went in with `docker cp`. Bare origin `/origin.git`; annotated scratch tag `v10.0.0` on `bd3770f2`; `git clone --no-checkout file:///origin.git /build`; sparse checkout `'/*' '!/tests/golden/held-out/'`; `git checkout --detach v10.0.0`. Not shallow, clean status, `README.md:14` reads `Latest release: v10.0.0`.

**Where this differs from T706.**

| Point | T706 | T759 |
|---|---|---|
| API path | `--skip-api`, plus an `importlib` stub of the API function | **The verbatim line and the real opener, no stub**; requests reach a double over TLS |
| Endpoint | `gitlab.invalid`, never contacted | `localhost:8443`, contacted |
| CA | Not relevant | `SSL_CERT_FILE` set to the double's CA: **the one added variable** |
| Refs in the bundle | Also `main`, `develop` (for the gates' scripts) | Release branch and tags only; the gates are out of scope |
| Clean clone | `git clone` | `git clone`, plus a runner-shaped init and fetch of the one tag (case s16) |
| Image afterwards | Left in the daemon's cache | Removed |

## 4. The job's lines

### 4.1 `before_script` (extracted from `.gitlab-ci.yml`, run with `sh -c`)

Exit 0. `(11/12) Installing git (2.54.0-r0)`, `(12/12) Installing git-init-template (2.54.0-r0)`, `OK: 25.9 MiB in 50 packages`. The probe saw `apk add` with `HOME LANG LC_ALL PATH` (plus `PWD SHLVL` from its own shell) and **0** variables holding the fake value.

### 4.2 `script` (extracted from `.gitlab-ci.yml`, verbatim)

```
python3 scripts/publish-release.py --tag "${CI_COMMIT_TAG}" --api-v4-url "${CI_API_V4_URL}" --expected-host "${CI_SERVER_HOST}" --project-id "${CI_PROJECT_ID}" --token-env CI_JOB_TOKEN --token-header JOB-TOKEN
release-publish: regenerated CHANGELOG.md for v10.0.0
release-publish: published GitLab release for v10.0.0                       (exit 0)
```

`git status --short` afterwards: only ` M CHANGELOG.md`.

**Child environment.** The script made 7 git calls: `fetch`, `rev-parse`, `tag`, `merge-base`, `rev-list` twice, `log`. Each received only `HOME LANG LC_ALL PATH SSL_CERT_FILE` (plus `PWD SHLVL` from the probe), with **0** variables holding the fake value.

## 5. The HTTP request path, against the double (V)

**What the double received on the normal run (s1):**

```
GET  /api/v4/projects/1/releases/v10.0.0   Host=localhost:8443  JOB-TOKEN is the fake value: True  PRIVATE-TOKEN present: False  body 0
POST /api/v4/projects/1/releases           Host=localhost:8443  JOB-TOKEN is the fake value: True  PRIVATE-TOKEN present: False  body 41324
```

- POST headers: `Accept-Encoding: identity`, `Host`, `User-Agent: Python-urllib/3.12`, `Job-Token: <masked>`, `Content-Type: application/json`, `Connection: close`.
- Payload keys: `description`, `name`, `ref`, `tag_name`; the last three are `v10.0.0`.
- `description` equals `docs/releases/v10.0.0.md`: `True`, 40901 bytes, sha256 `630bb0f171a51a0819a48a3ef42829757f013e58ae0280c2373b87467b73da14`, the same sha256 as the file in my worktree.
- The fake value is in no request path or body, and in no output line or `CHANGELOG.md` in any case below.

| Case | Set up | Exit | Requests | Output |
|---|---|---|---|---|
| s2 update | GET 200 with the tag | 0 | GET, PUT | `CHANGELOG.md` byte-identical to s1 (`cmp` 0), so the run is idempotent |
| s3 redirect on GET | 302 to `https://localhost:8444/sink` | 1 | 1; **0 on :8444** | `GitLab API GET ... failed: 302 {}` |
| s4 redirect on POST | 307 to the same | 1 | 2; **0 on :8444** | `GitLab API POST ... failed: 307 {}` |
| s5 refused | POST 403 | 1 | 2 | `failed: 403 {"message": "403 Forbidden"}`; `CHANGELOG.md` already written (section 11) |
| s6 wrong answer | POST 201 with another `tag_name` | 1 | 2 | `GitLab release publish failed: unexpected response {'tag_name': 'v0.0.1'}` |
| s7 server error | GET 500 | 1 | 1 | `failed: 500 {"message": "500"}`; no POST |
| s8 host pin | `CI_SERVER_HOST=gitlab.invalid` | 1 | **0** | `invalid --api-v4-url: host does not match the expected GitLab host`; no file changed |
| s9 plain http | `CI_API_V4_URL=http://...` | 1 | **0** | `must start with https://` |
| s10 user information | `https://u:p@localhost...` | 1 | **0** | `must not contain user information` |
| s11 untrusted server | `SSL_CERT_FILE=/etc/ssl/cert.pem` (the image's bundle) | 1 | **0** | `[SSL: CERTIFICATE_VERIFY_FAILED] ... unable to get local issuer certificate` |
| s11b the same | `SSL_CERT_FILE` unset, as in CI | 1 | **0** | the same message |
| s12 no server | Nothing listening | 1 | 0 | `[Errno 111] Connection refused` |
| s13 no token | `CI_JOB_TOKEN` empty | 1 | **0** | `environment variable CI_JOB_TOKEN is not set or empty` |
| s14 T706's case A | `GIT_CONFIG_COUNT=1`, `KEY_0`, `VALUE_0` holding the fake value | 0 | 2 | Differs from T706, see section 11 |
| s15 no such tag | `CI_COMMIT_TAG=v10.0.1` | 1 | 0 | `current tag 'v10.0.1' not found in local git tags` |
| s16 clean clone, one tag | `git init`, `fetch --no-tags` of `v10.0.0` only | 0 | 2 | Tags 1 before, 42 after; `CHANGELOG.md` byte-identical to s1 |

s16 shows that the script's own `git fetch --tags --force` finds `v9.0.0` when the checkout brought no other tag. s11 and s11b show that the image's real default trust path rejects a server outside its bundle, with no HTTP request sent, so the token header never left the client.

## 6. The verdict sections holding `pending`

**The release job reads them only as part of the body, and it does not care.** `load_release_brief` reads the whole file, checks that it is a non-blank regular file, and `render_release_description` returns it unchanged (`scripts/publish-release.py:361-382`, `:568-570`). No line of the script looks at a verdict. On s1 the double received 17 lines holding the word `pending`, and the job still exited 0.

The check lives in the gate before it. `release` has `needs: ["release-docs-gate", "main-develop-drift-gate"]`, and `_line_problems` in `scripts/verify-release-docs.py:526-527` reports `value is still pending`. On the host's Python with `markdown-it-py` 3.0.0 (not in the image), `python3 scripts/verify-release-docs.py --tag v10.0.0` exits **1** today with 16 lines, for example `Gate Verdicts: value is still pending: - Architecture: pending`. So the protection against publishing `pending` is the gate alone, and the body published is the document as it stands on the tagged commit, so T763 must land before the tag.

## 7. Checklist items 6 and 7

**Item 6 (V): the entry lands below `[Unreleased]`.** The first lines of the generated file, from line 13:

```
## [Unreleased]

Changes merged since the latest `vX.Y.Z` tag. This committed file carries no
released entries: the `release` CI job lists the commits of each tag in the
`CHANGELOG.md` of its job artifact, and the release notes are in
`docs/releases/vX.Y.Z.md`.

## [v10.0.0] - 2026-11-07

_Commits since v9.0.0._

### Bug Fixes
- the rest of batch S, gate limits and tag job environment (T749, T750, T751)
```

Against the committed file: 41 lines inserted, 0 removed. T706's O-1 (entry above `[Unreleased]`) no longer applies.

**Item 7 (V, in part).** The real commit range holds **no** subject with a reference sigil or a URL, so the generated file has no escape to show: on real data this item is vacuous. The final range will also gain the commits made after `bd3770f2`, so it should be re-read in the first tag pipeline's artifact. The examples below come from calling the clone's own `markdown_entry` directly in the image, not from the job's output:

| Subject text | `markdown_entry` output |
|---|---|
| ``close #42 and !12 for @alice in ~bug %v10 $7 ^1`` | ``close \#42 and \!12 for \@alice in \~bug \%v10 \$7 \^1`` |
| ``see https://gitlab.invalid/a/b?x=1 and www.example.invalid (#42)`` | ``see `https://gitlab.invalid/a/b?x=1` and `www.example.invalid` (\#42)`` |
| ``keep `code #1` then [x](https://evil.invalid) <b>&#8238;</b>`` | ``keep `code #1` then `[x](https://evil.invalid)` \<b\>\&\#8238;\</b\>`` |
| ``<!-- hidden`` | ``\<\!-- hidden`` |
| ``# heading`` | ``\# heading`` |
| ``mail bob@example.invalid`` | ``mail bob\@example.invalid`` |

The last row is the residual the source documents: the at sign is escaped, and a bare e-mail address can still be autolinked as `mailto:`. Rendering on GitLab stays **(unverified)**.

## 8. The "Commits since" line (V)

`_Commits since v9.0.0._`, as required. `git merge-base v9.0.0 HEAD` is the `v9.0.0` commit `e4c7e7d4`. The entry has 26 bullets and 0 `Merge branch` lines. From the host's git 2.43, `v9.0.0..bd3770f2` has 26 non-merge subjects out of 49. After the Conventional prefix is stripped, the bullets and the subjects are the same multiset (script check: `True`, 26). Groups: Bug Fixes 6, Documentation 7, CI 1, Chores 3, Other 9. `Other` holds the nine `plan-NNN: ...` subjects, which have no Conventional type; that is correct classifier behaviour.

## 9. The `_ssl` check for SEC-T756-01 (V)

**Result: FOUND. Python 3.12.16 and one blocked key hash are in the built module.** Confidence: high that the denylist table is compiled into this image's `_ssl`. Good, but indirect, that it is wired in. Not observed: a chain actually rejected.

**How the denylist is stored.** PR 160042 adds `Modules/_ssl/distrusted_spki.h`: a `static const unsigned char _distrusted_spki[][SHA256_DIGEST_LENGTH]` of raw SHA-256 digests of each key's DER `SubjectPublicKeyInfo`. `Modules/_ssl.c` compares them in `_cert_has_distrusted_spki`, called from `_ssl_verify_callback`, and sets `X509_V_ERR_CERT_REJECTED`. The header and these functions are also at tag `v3.12.16` (`_ssl.c:2922`, `:2930`, `:2957`, `:3006`). So the stored form to look for is 32 raw bytes, and I took the hash from the `v3.12.16` header, not only from the PR.

**Output of the one command** (`python3 -I /rehearse/sslcheck.py`):

```
sys.version: 3.12.16 (main, Nov  5 2026, 19:26:55) [GCC 15.2.0]
ssl.OPENSSL_VERSION: OpenSSL 3.5.9 29 Sep 2026
_ssl.__file__: /usr/local/lib/python3.12/lib-dynload/_ssl.cpython-312-x86_64-linux-musl.so
size: 226816 sha256: 0eed52ea8e6d390243d12e8a6e3cd7e06a015283be69132820ddf880d8815727
TARGET raw 32 bytes (CN=EM OV TLS CA - G3B): [181568]
TARGET as ASCII hex (form check): []
NEGATIVE same hash, last bit flipped: []
NEGATIVE random 04bf95acba1eb30e9de9ab06fa080dfdf395292e216a073d3980119a3307e8f2 []
NEGATIVE random aa7be9d9ca21e2262b6c8dc5682a1928836e866f715997ee17e03e54d68578ba []
NEGATIVE random edc58d150720d30ee7bf8097489b6e90c0913999197f9bbeac441b5d4c3cb55a []
POSITIVE ssl.SSLCertVerificationError 1
POSITIVE i2d_X509_PUBKEY 1
POSITIVE SSL_get_verify_callback 1
POSITIVE X509_STORE_CTX_set_error 1
POSITIVE EVP_Digest 1
POSITIVE SSL_CTX_set_verify 1
ABSENT-STRING control 0
```

The target is `43bffa19d6ef651451f6841e019931e96f6f2eaeff28ab4b6f1ce4576de2717b`, public, a digest of a public key. No key material or certificate was fetched or used.

**What the controls show.** The positive control proves that the search reads this file; the negative controls (three random, one a single bit away, one absent string) show that a hit is not an accident of the method. `i2d_X509_PUBKEY`, `EVP_Digest` and `X509_STORE_CTX_set_error` are the OpenSSL functions the new check calls at `v3.12.16` (`_ssl.c:2930`, `:2937`, `:2973`), and `SSL_get_verify_callback` is what keeps the callback on a server socket (`_ssl.c:874`). That is corroboration from names, not proof of the call path, and I did not compare with a 3.12.15 module, which would have taken a second image.

**One behavioural observation in passing.** s1 validated the double's certificate through this module, so the callback, if active, does not reject a key outside the list. That says nothing about a key on the list.

**Driving the block over a local TLS server: possible only by hand, and not done.**

- A normal server cannot do it from public certificates. `load_cert_chain` needs the leaf's private key, and CPython's own `test_distrusted_spki` uses a fixture that holds one (`distrusted_keycert.pem` in `distrusted.zip`). That is excluded here.
- The disclosure's `chains.zip` has no private key (T765). A hand-written responder could send a plaintext TLS 1.2 `ServerHello` and `Certificate`, because the client checks the chain before any proof of key possession **(unverified)**. The client would also need the chain's issuer as its trust anchor, because `_ssl_verify_callback` returns early when OpenSSL already reported an error, and T765 found 0 of 16 chains validate against the image's bundle.
- I did not build it. It is more than the user's approval of "one extra read-only command", and the brief asks for nothing elaborate. It would be the way to raise "wired in" from indirect to observed.

## 10. Not exercised

All **(unverified)** until the real tag pipeline, unless stated.

- **The real `CI_JOB_TOKEN`**, whether GitLab accepts it in `JOB-TOKEN` (the wire form is in section 11), the role and allowlist behind it, whether job tokens work on protected `v*` tags, and its masking in job logs.
- **The real clone credential**: the runner's clone over https, and whether `git fetch --tags --force` succeeds with the job's filtered environment. The origin here is `file://` and needs none. SEC-T686-06 therefore stays open.
- **The Releases API's real response**: status codes, response shape, size limit and any normalising of the 40901-byte body. The double's answers are mine.
- **GitLab's rendering** of the release body and of the escaped changelog text.
- **`release-docs-gate` and `main-develop-drift-gate` on the new image**, including the `pip install` in the docs gate, `run-allowlisted.py`, and the tag-tree and drift checks. Only `release` was rehearsed. Section 6's gate run used the host's Python.
- **Real TLS to GitLab** through the image's bundle, with this image's `_ssl` callback.
- **The runner itself**: its refspecs, `GIT_STRATEGY: clone` on a real runner, the external config file, `needs:` ordering, `expire_in: never` artifact upload, and the executor. s16 only imitates the fetch shape.
- **The tag day**: the final document after T763, the commits after `bd3770f2`, and whether `git~=2.54` still resolves that day.
- **Architecture**: x86_64 on this host; the runner's is unknown.

## 11. Observations (no change made, no defect)

- **O-1 (wire form of the header).** The script adds `JOB-TOKEN`, and the double received `Job-Token`, because `urllib` normalises header names. HTTP header names are case-insensitive, so this should not matter, but this is the first time the form on the wire has been seen; GitLab's acceptance stays unverified.
- **O-2 (T706's case A has changed).** At T706, `GIT_CONFIG_COUNT` with a filtered `VALUE_0` made git stop. Since T716 all of the `GIT_CONFIG_*` names are dropped, so git never sees them and s14 passes. With a real https origin, a runner that delivers its credential only this way would now fail at the fetch for lack of a credential, which still fails closed **(unverified)**; a `file://` origin cannot show that.
- **O-3 (order of writes).** `CHANGELOG.md` is written before the API call, so on s5 the file changed and the job failed. The job's `artifacts` has no `when`, so GitLab's default of `on_success` should keep it from being uploaded **(unverified)**. A retry starts from a clean clone. Harmless.
- **O-4 (Alpine moved).** The image is now on Alpine 3.24.4, and the `apk` pin of `release` still resolves. That answers the risk in the T756 review for this one job only; the other jobs' pins were not run.

## 12. Reproduction

The helper scripts were throwaway files in the session scratchpad and were not committed. The steps:

1. `git bundle create repo.bundle refs/heads/release/v10.0.0 --tags`; make a throwaway CA and `localhost` leaf.
2. `docker pull` and `docker run -d` the digest, then `docker cp` the bundle, TLS files, double, probes, and the two lines extracted from `.gitlab-ci.yml`.
3. Run the `before_script` line with the fake variables of section 3.
4. `docker network disconnect bridge <container>`.
5. Build the bare origin, add the scratch tag, clone with the sparse checkout.
6. Start the double in a given mode, set `SSL_CERT_FILE` to its CA, and run the `script` line in `/build`; repeat per case in section 5.
7. `docker rm -f` the container and `docker rmi` the digest, then compare `docker ps -a` and `docker images` with the state before.
