# Artifact: ca-check-t765-v1.md

**Task:** T765. **Date:** 2026-11-06. **Author:** devops-engineer.
**Based on:** `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (SEC-T756-02); `docs/plans/plan-145-release-v10.md` § T765; `docs/artifacts/mcp-pin-audit-v10-v1.md` § the CI images.

# CA check for SEC-T756-02: do the compromised eMudhra chains reach `git` in CI?

## Result

**Not reachable through the disclosed chains in the CI image's CA bundle.** All 16 chains in the disclosure's `chains.zip` are rejected by the bundle of the new digest, and by the old digest's, which is the same file. This does not depend on the runner's pin.

**The runner's pin does not protect `git` in the job's own image on the Docker executor, by source reading.** So the bundle is the only control there, and it holds today. It has to be re-checked at each image bump (see "What keeps this true").

Whether this is a blocker is the Security Engineer's call on SEC-T756-02. The condition set for a blocker, chains that validate and a pin that does not stop them, is **not met**: the second half is true, the first is not.

## Method

No Docker, and nothing from the layers or the archive was run.

- **Bundle.** Over the registry HTTP API: index, amd64 manifest, config and all four layers, each blob's body hashed against its digest. From the listing, `/etc/ssl/cert.pem` is a symlink to `certs/ca-certificates.crt`, present in layer 0 and written again in layer 1. Layer 1's copy is the effective one. Only that member was extracted (`tarfile`, `filter="data"`).
- **Chains.** `chains.zip` from `https://emudhra.we-have-a-problem.com/` (sha256 `afb9d69e8e5fc9eb0c08d5fe4baafc67edbcced2d63af2f9deb62edb6431d4a9`), 19 members: 16 PEM chains and 3 readmes. **No private key material:** each member was searched for `PRIVATE KEY` before being written, and none matched. `proof.zip` was not downloaded.
- **Verify.** `env -i PATH=/usr/bin:/bin openssl verify -no-CApath -no-CAstore -CAfile BUNDLE -purpose sslserver -untrusted CHAIN CHAIN`, OpenSSL 3.0.13 on this host. The disclosure's own command omits `-no-CApath -no-CAstore`; without them OpenSSL also loads the host's default directory, and the host's trust is not the question here. Leaves are in date (for example `dv-g3b-noct`: not after 2027-05-05).

| Image | Index digest | Base | Bundle sha256 | Certificates |
|---|---|---|---|---|
| `python:3.12-alpine`, new | `sha256:e064671c…0fc7` | Alpine 3.24.4 | `5961c0a3c65459931c023e0075c09733f09aea4ca439cb85bc4a08bb4f3f568b` | 118 |
| `python:3.12-alpine`, old | `sha256:92abd2ba…d656` | Alpine 3.24.3 | same | 118 |
| `node:24-alpine`, unchanged | `sha256:06d7adf3…8b53` | Alpine 3.24.3 | same | 118 |
| Package `ca-certificates-bundle-20261020-r0`, branch v3.24 | n/a | n/a | same | 118 |

The Node image counts because `sync-no-diff` runs there, though that job's `git` only runs `git diff`. The package row means a later `apk` upgrade on this branch today would change nothing.

## Chains against each bundle

Error 20 is `unable to get local issuer certificate`: the path ends at a certificate whose issuer the bundle does not hold.

| Chain | New digest | Old digest | Control: new + 4 roots |
|---|---|---|---|
| `regular/dv-g3b-aaa` | rejected, error 20 at depth 1 | rejected, error 20 at depth 1 | OK |
| `regular/dv-g3b-aaa-noct` | rejected, error 20 at depth 1 | rejected, error 20 at depth 1 | OK |
| `regular/dv-g3b` | rejected, error 20 at depth 2 | rejected, error 20 at depth 2 | OK |
| `regular/dv-g3b-noct` | rejected, error 20 at depth 2 | rejected, error 20 at depth 2 | OK |
| `regular/dv-g3c-aaa` | rejected, error 20 at depth 1 | rejected, error 20 at depth 1 | OK |
| `regular/dv-g3c` | rejected, error 20 at depth 2 | rejected, error 20 at depth 2 | OK |
| `regular/ev-g3b-aaa` | rejected, error 20 at depth 1 | rejected, error 20 at depth 1 | OK |
| `regular/ev-g3b` | rejected, error 20 at depth 2 | rejected, error 20 at depth 2 | OK |
| `regular/ev-g3c-aaa` | rejected, error 20 at depth 1 | rejected, error 20 at depth 1 | OK |
| `regular/ev-g3c` | rejected, error 20 at depth 2 | rejected, error 20 at depth 2 | OK |
| `regular/ov-g3b-aaa` | rejected, error 20 at depth 1 | rejected, error 20 at depth 1 | OK |
| `regular/ov-g3b` | rejected, error 20 at depth 2 | rejected, error 20 at depth 2 | OK |
| `regular/ov-g3c-aaa` | rejected, error 20 at depth 1 | rejected, error 20 at depth 1 | OK |
| `regular/ov-g3c` | rejected, error 20 at depth 2 | rejected, error 20 at depth 2 | OK |
| `rollover/dv-g3b-aaa-noct-rollover` | rejected, error 20 at depth 2 | rejected, error 20 at depth 2 | OK |
| `rollover/dv-g3b-noct-rollover` | rejected, error 20 at depth 3 | rejected, error 20 at depth 3 | OK |

**Totals:** new digest 0 of 16, old digest 0 of 16, Node image 0 of 16, control 16 of 16.

**Why they fail.** The disclosure's `roots.json` names 4 roots and `impacted-intermediates.json` 16 certificates. Compared with the 118 bundle certificates by certificate sha256 and by SPKI sha256, none of the 20 is present in either Python bundle. The bundle's only emSign root is `emSign Root CA - G1`, which the disclosure does not list.

**Controls.**
- Positive: the chain `gitlab.com:443` served today verifies `OK` against the new bundle, through `Sectigo Public Server Authentication Root R46`. So the bundle and the command accept a good chain, and it is the chain of the server the fetches go to.
- Positive: the new bundle plus the disclosure's 4 roots validates all 16 (last column). So each rejection comes from the missing roots and not from an expired leaf or a malformed file.

## How runner 19.5.2 handles `git`'s CA

Source: `gitlab-org/gitlab-runner` at tag `v19.5.2`, read over HTTP. No job was traced.

`shells/abstract.go`, `writeGitSSLConfig`, sets the pin only when the variable exists:

```go
tls.VariableCAFile:   "sslCAInfo",
...
key := fmt.Sprintf("http.%s.%s", host, config)
w.CommandArgExpand("git", append(args, key, w.EnvVariableKey(variable))...)
```

It has two callers, and which one runs depends on the executor:

```go
if !info.Build.IsSharedEnv() {
    b.writeGitSSLConfig(w, info.Build, []string{"--global"})      // abstract.go:519-521, the get_sources stage
}
...
if build.IsSharedEnv() {
    b.writeGitSSLConfig(w, build, []string{"-f", extConfigFile})  // abstract.go:1076-1078, .gitlab-runner.ext.conf
}
```

`IsSharedEnv` returns `b.ExecutorFeatures.Shared`. `executors/shell/shell.go` sets `features.Shared = true`; `dockerFeaturesUpdater` in `executors/docker/docker_command.go` does not set it. The variable holds a chain taken from the runner's own connection unless the runner has a configured CA (`network/client.go`, `buildCAChain`; `common/build.go`, `GetCITLSVariables`).

What follows, for the Docker executor:

| Git client | `FF_GIT_URLS_WITHOUT_TOKENS` off (default in `helpers/featureflags/flags.go`) | Flag on |
|---|---|---|
| The clone, in the helper container | Pinned: `--global` in the helper's own config, same container | Pinned: `--global` lands in the seed file `.glr.gconf` |
| `git fetch` in the job image, no allowlist (`unit-tests`, `main-develop-drift-check`) | **Not pinned:** the pin is in the helper's home and not in `.gitlab-runner.ext.conf`; the bundle decides | Pinned: every stage exports `GIT_CONFIG_GLOBAL` to the seed file |
| `git fetch` through `run-allowlisted.py` (`main-develop-drift-gate`) | **Not pinned**, as above; the allowlist changes nothing | **Not pinned:** the allowlist drops `GIT_CONFIG_GLOBAL` |
| `publish-release.py`'s `git fetch` (`release`) | **Not pinned**, as above | **Not pinned:** its allowlist drops `GIT_CONFIG_GLOBAL` too (`scripts/publish-release.py:109`) |

That helper and job containers do not share `$HOME` is the known Docker executor model, not read in this source **(unverified)**.

**The allowlist, `scripts/run-allowlisted.py`.** `ALLOWED_NAMES` keeps `SSL_CERT_FILE`, `SSL_CERT_DIR` and `CURL_CA_BUNDLE`. It drops `CI_SERVER_TLS_CA_FILE`, `GIT_SSL_CAINFO`, `GIT_SSL_CAPATH`, `GIT_SSL_NO_VERIFY` and every `GIT_CONFIG_*`.
- Dropping `CI_SERVER_TLS_CA_FILE` does not matter by itself: the runner writes the expanded path into config, and git does not read that variable.
- **The change it makes:** with the flag on, T750's allowlist removes the path to the pin on the drift gate. With the flag off it removes nothing, because there was no pin in that container. The flag's deployed value is **(unverified)**; `tracked-debt-register-v11.md` lists it as unread too.
- A kept `SSL_CERT_FILE` or `CURL_CA_BUNDLE` set as a project variable could point git or Python at another store. Whether any such variable exists is **(unverified)**: this role reads no CI variables.

**Is the token sent?** The project is public, so these fetches may succeed with no credential. With the flag off, the token sits in `.gitlab-runner.ext.conf` as a `url.<with creds>.insteadOf` entry; with it on, a credential helper returns it. `http.proactiveAuth=basic` is added by the runner only with `FF_USE_GIT_PROACTIVE_AUTH` (`proactiveAuthArgs`). So I expect `git` to send it only after a 401, which a public fetch does not draw. That is from my memory of git and libcurl **(unverified)**, and a man in the middle can return a 401 itself, so treat the token as reachable by anyone who passes certificate validation. Certificate validation is what this check found to hold.

## What keeps this true

The result rests on the bundle and not on any denylist: OpenSSL clients have none. Two facts make it fragile:

- **`roots.json` marks `emSign ECC Root CA - G3` as "Included" in Mozilla's store,** yet the bundle has no such certificate. I did not establish why **(unverified)**. If a later `ca-certificates` carries it, 8 of the 16 chains validate: the new bundle plus that root alone gave `OK` on 7 regular and 1 rollover chain. T756's proposed plan already says to re-check at each image bump; I would keep that, with this file's command.
- The same disclosure's `AAA Certificate Services` is marked "Removed" for Mozilla and is absent here.

## Could not establish

1. **A live connection.** `openssl verify` checks a path. No `git` ran against a test host, and no client ran in the image (no Docker). T759's rehearsal could run `git ls-remote https://dv-g3b-emudhra.we-have-a-problem.com/` in the image, and expect a certificate error, if the user's approval covers that endpoint; its approval names a fake API endpoint only, so I do not assume it does.
2. **The hashed directory `/etc/ssl/certs`.** The new image's layer 1 adds `ca-cert-*.pem` links. By name none is emSign G3 or AAA, and the only emSign one is G1, but I extracted no file behind them. Which of the file and the directory Alpine's libcurl reads is **(unverified)**.
3. **Other cross-signs.** Only the certificates the disclosure lists were compared. A crt.sh search by key was attempted and failed (`Network is unreachable`), so a cross-sign it does not list, from a root in this bundle, is **(unverified)**.
4. **The runner's deployed settings:** executor, `FF_GIT_URLS_WITHOUT_TOKENS`, whether `CI_SERVER_TLS_CA_FILE` is set in a real job. The `docker` and `dind` tags suggest the Docker executor; that is an inference **(unverified)**. Version 19.5.2 is from `tracked-debt-register-v11.md`, not re-read.
5. **The runner's helper image and its bundle.** Not read. By source the clone there is pinned **(unverified at runtime)**.
6. **The denylist inside the built `_ssl` module of 3.12.16.** The config says `PYTHON_VERSION=3.12.16`, and T756's record cites the release notes. The binary was neither read nor run **(unverified)**: T759 is the first chance.
7. **Non-amd64 images.** Only amd64 was read.
