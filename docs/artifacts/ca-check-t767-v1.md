# Artifact: ca-check-t767-v1.md

**Task:** T767. **Date:** 2026-11-07. **Author:** devops-engineer.
**Based on:** `docs/artifacts/ca-check-t765-v1.md` (§ "Could not establish" items 1-7, § "How runner 19.5.2 handles `git`'s CA"); `docs/artifacts/security-review-t756-accepted-mediums-v1.md` § 2 (SEC-T756-02, "What would justify LOW"); `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` (Part A, item 2); `docs/tasks/task-T767.md`. Item 6 of T765 is cited from `docs/artifacts/release-rehearsal-t759-v1.md` § 9 and `docs/artifacts/security-review-release-v10-v1.md`, not redone.

# Open points of SEC-T756-02 after T765

## Result

**T765's result stands, and four of its open points are now settled; three remain, two of them for the user.** Grading stays with the Security Engineer (T768).

| T765 open point | Status after T767 |
|---|---|
| Why `emSign ECC Root CA - G3` is absent (T765 § "What keeps this true") | **Settled.** Mozilla removed it from NSS in an emergency removal (NSS 3.131.1); Alpine shipped that as the security upgrade `ca-certificates` 20261020 on 2026-10-20. `roots.json`'s "Included" predates the removal. A forward bump does not bring it back unless Mozilla re-adds it; an image built from `ca-certificates` 20260909 or older would carry it |
| 2. The hashed directory | **Settled.** Python image: 118 hash links to the same 118 certificates as the bundle, hash names correct, no emSign G3 or AAA. Node image: no hashed directory. git (libcurl) reads both the bundle file and `/etc/ssl/certs`; Python reads `/etc/ssl/cert.pem` (same file) and `/etc/ssl/certs` |
| 3. Other cross-signs | **Settled as far as CT shows.** crt.sh by all 12 keys: 4 certificates beyond the disclosure's JSON, all under eMudhra G3 roots that no bundle here holds, all rejected by the bundle. No cross-sign from a root in the bundles |
| 4. Runner executor and version | **Settled by the orchestrator's observation:** Docker executor, runner 19.5.3. `FF_GIT_URLS_WITHOUT_TOKENS` and CA-related variables: **open, user action A-21** |
| 5. Helper image | **Partly settled:** tag `x86_64-v19.5.3`, not digest-pinned by source; today's image has the same bundle. Which image the runner actually used: **open, A-21** |
| 1. A live connection | **Open**, not in this task's scope (see "Could not establish") |
| 6. `_ssl` denylist | Settled earlier by T759 § 9 and T762; not redone |
| 7. Non-amd64 images | **Open**, only amd64 read |

**One new fact for the re-grade.** crt.sh holds a second, validly signed `EM DV TLS CA - G3B` certificate with the same TBS as the listed one and a different signature, hence a different SHA-256 (point 3). It does not change the CI result (it chains to a root not in the bundle), but it means the bump check must compare by key (SPKI), not only by certificate hash, as T765's comparison already did.

## Method

No Docker, no CI variable read, no job log read. Nothing downloaded was executed.

- **Images.** Over the Docker Hub registry HTTP API (anonymous pull token): index, amd64 manifest, config and every layer of both pinned images, each blob hashed against its digest (all matched). Listing with Python `tarfile` (`python3 -I`, scripts outside the download directory); only regular files under `usr/share/ca-certificates/mozilla/`, the bundle and `etc/ca-certificates.conf` were extracted, with `filter="data"`.
  - `python:3.12-alpine@sha256:e064671c…0fc7` -> amd64 manifest `sha256:a61cbd76a882645de7f91423329fe43a67eed60d7da24f9e5331414bb3618b20`.
  - `node:24-alpine@sha256:06d7adf3…8b53` -> amd64 manifest `sha256:1200d815de24f8dcca745fbf7651d166034a35adbcad8860a8538ffff44f1420`.
- **Certificates.** `openssl x509 -fingerprint -sha256` and `-subject_hash`, OpenSSL 3.0.13 on this host.
- **Disclosure data.** `https://emudhra.we-have-a-problem.com/roots.json` (sha256 `119f32cd81a6b5a4e3c4c2df5fe07daa90dc43cafa123a62f0394f1895d92380`) and `impacted-intermediates.json` (sha256 `f67b3abe9b4879f4e91874ed041beccd71257f1db41c588c724ccf12aa90c59e`), downloaded 2026-11-07. Together 20 certificates over 12 distinct keys (4 roots, 8 intermediate keys).
- **Sources read over HTTPS:** Alpine `aports` (branch `3.24-stable`) and `alpine/ca-certificates` on `gitlab.alpinelinux.org` (API and raw files), `pkgs.alpinelinux.org`, CPython `Lib/ssl.py` at `v3.12.16`, git `http.c` at `v2.54.0`, `gitlab-org/gitlab-runner` at `v19.5.3`, Mozilla bug 2083449 (summarising fetch), `crt.sh` JSON.

## 1. Why `emSign ECC Root CA - G3` is absent

**Result: removed from Mozilla's NSS in NSS 3.131.1, and so from Alpine's `ca-certificates` 20261020, the package in all three images. `roots.json`'s "Included" is the state before the removal.**

- `roots.json` gives that root `role: cross_signer` and `root_store_status.mozilla: "Included"`; it lists the same snapshot for every program. The disclosure page itself lists "Alpine Linux ca-certificates 20261020-r0" under "Who has patched?" and, for unpatched Alpine, a workaround that comments out `mozilla/emSign_ECC_Root_CA_-_G3.crt` in `/etc/ca-certificates.conf`.
- Alpine `aports`, `main/ca-certificates`, branch `3.24-stable`: commit `e78f5987166c6ffbe23f6472e2e8f040298fe2da`, 2026-10-20, "main/ca-certificates: security upgrade to 20261020" (previous: `eb7078df`, 2026-09-17, 20260909). The APKBUILD builds from `alpine/ca-certificates` tag `20261020`, whose `Makefile` has `NSS_VERSION := NSS_3_131_1_RTM` and whose commit `cbaa3e6f` is "certdata: NSS_3_131_1_RTM".
- The diff of `cbaa3e6f` on `certdata.txt` removes exactly three roots, each object and trust record: `emSign ECC Root CA - G3`, `emSign Root CA - C1`, `emSign ECC Root CA - C3`. The removed trust records carried `CKA_TRUST_SERVER_AUTH CKT_NSS_TRUSTED_DELEGATOR` and `CKA_NSS_SERVER_DISTRUST_AFTER CK_FALSE`: before the removal the root was fully trusted for TLS with no distrust-after date. `certdata.txt` at tag `20260909` has 8 lines naming `emSign ECC Root CA - G3`; at `20261020`, 0.
- Mozilla bug 2083449 ("eMudhra: Private key compromise of Intermediate Certificates", ASSIGNED), Comment 18 as returned by a summarising fetch: "we have decided that the circumstances warrant the emergency removal of trust in emSign ECC Root CA - G3", tracked in bug 2084101 "Remove eMudhra emSign Root CA - G3 from NSS" (RESOLVED FIXED); "At this time we are not removing trust in emSign Root CA - G1." The quotes come through a summarising tool and were not read verbatim **(unverified wording)**.
- **AAA Certificate Services** is still in `certdata.txt` at `20261020` (label `Comodo AAA Services root`) with `CKA_TRUST_SERVER_AUTH CKT_NSS_MUST_VERIFY_TRUST`, i.e. not a TLS anchor, so `mk-ca-bundle.pl` leaves it out of the TLS bundle. It is absent from all bundles here (T765).
- **`emSign Root CA - G1`** stays, with `CKA_TRUST_SERVER_AUTH CKT_NSS_TRUSTED_DELEGATOR`. The disclosure does not list it, and Mozilla keeps it on purpose. eMudhra plans to move affected subscribers under G1 (bug 2083449, Comment 19, through the same summarising fetch).

**Could a later bundle carry it?** Only if Mozilla re-added the root to NSS, or if an image were built from a `ca-certificates` older than 20261020, i.e. a digest bump to an image built before 2026-10-20 or an `apk` repository pinned to an older index. A forward bump on Alpine does not bring it back as long as NSS does not. Before 20261020 it was in the bundle: an image built from Alpine `ca-certificates` 20260909 or older would validate 8 of 16 chains (T765's measurement with the root added). So the digest-bump check (T765's command, T766's control) must reject a bundle older than 20261020 as well as one with the root in it.

## 2. The hashed directory `/etc/ssl/certs` and which store each client reads

**Result: in the Python image the directory holds the same 118 certificates as the bundle, so it adds nothing; the Node image has no hashed directory. No emSign G3 or AAA certificate in either.**

Listing of the Python image (layers counted from 0; layer 0 is the Alpine minirootfs, layer 1 is `apk add ca-certificates tzdata` from the image's history):

- Layer 0: `etc/ssl/cert.pem` -> `certs/ca-certificates.crt`; `etc/ssl/certs/ca-certificates.crt` (178791 bytes); `etc/ssl1.1/cert.pem` -> `/etc/ssl/cert.pem`; `etc/ssl1.1/certs` -> `/etc/ssl/certs`.
- Layer 1: `etc/ssl/certs/ca-certificates.crt` again (sha256 `5961c0a3…f568b`, T765's file), 118 regular files `usr/share/ca-certificates/mozilla/*.crt`, 118 links `etc/ssl/certs/ca-cert-<name>.pem` -> `/usr/share/ca-certificates/mozilla/<name>.crt`, and 118 links `etc/ssl/certs/<8 hex>.0` -> `ca-cert-<name>.pem`. No other member under `etc/ssl/certs`, no whiteouts. Layers 2 and 3 add nothing under these paths. `etc/ca-certificates.conf` enables 118 entries and disables none.
- The only emSign file is `emSign_Root_CA_-_G1.crt` (hash link `2923b3f9.0`). No name contains `G3`, `AAA` or `Comodo_AAA`.
- **Same set.** The SHA-256 fingerprints of the 118 `.crt` files and of the 118 certificates in the bundle are identical (`diff` empty). Since T765 found none of the disclosure's 20 certificates in the bundle, by certificate hash and by SPKI hash, none is in the directory either.
- **Hash names are honest.** For all 118 hash links, `openssl x509 -subject_hash` of the target equals the link name (0 mismatches), and every name ends in `.0`, so no two subjects collide.
- **Node image:** only the minirootfs layer touches these paths: the bundle (same 178791-byte file; T765: same sha256) and the `cert.pem` link. No `ca-cert-*.pem`, no hash links. `lib/apk/db/installed` lists `ca-certificates-bundle 20261020-r0` and no `ca-certificates`.
- **Installed packages** (`lib/apk/db/installed`, last layer that writes it): Python image `ca-certificates 20261020-r0`, `ca-certificates-bundle 20261020-r0`, `libssl3`/`libcrypto3 3.5.9-r0`; Node image `ca-certificates-bundle 20261020-r0`, `libssl3`/`libcrypto3 3.5.9-r0`. Neither image has `git` or `libcurl`.

**Which store each client reads (from source):**

| Client | How it gets there | Store |
|---|---|---|
| `git` (HTTPS) in a job | `apk add --no-cache 'git~=2.54'` at job time (`.gitlab-ci.yml` lines 101, 151, 164, 234, 253) pulls `libcurl` | git `http.c` at `v2.54.0` sets `CURLOPT_CAINFO`/`CURLOPT_CAPATH` only from `http.sslCAInfo`/`http.sslCAPath` or `GIT_SSL_CAINFO`/`GIT_SSL_CAPATH` (lines 1122-1131, 1410-1411); otherwise libcurl's built-in defaults. Alpine `curl` 8.23.0-r0 APKBUILD (`3.24-stable`): `--with-ca-bundle=/etc/ssl/certs/ca-certificates.crt --with-ca-path=/etc/ssl/certs`. So git reads **the bundle file and the hashed directory**, which hold the same 118 certificates (Python image) or the bundle only (Node image) |
| `apk add git` and the bundle | `pkgs.alpinelinux.org`, `libcurl` v3.24: depends on `ca-certificates-bundle` with no version | `apk add` without `-u` keeps the installed `20261020-r0`; it does not swap the bundle **(apk solver behaviour from memory, unverified)** |
| Python's default context (`ssl.create_default_context()`, `urllib`) | CPython `Lib/ssl.py` at `v3.12.16`: `load_default_certs()` calls `set_default_verify_paths()` on non-Windows (line 534) | OpenSSL's compiled defaults: Alpine `openssl` 3.5.9 APKBUILD `--openssldir=/etc/ssl`, so `/etc/ssl/cert.pem` (a link to the same bundle) and `/etc/ssl/certs`; overridable by `SSL_CERT_FILE`/`SSL_CERT_DIR`. The image builds Python against `openssl-dev` (image history). Python additionally has the `_ssl` key denylist (T759 § 9, T762), which git does not |

`SSL_CERT_FILE` and `SSL_CERT_DIR` (kept by `scripts/run-allowlisted.py`) change Python's defaults if set as CI variables; `CURL_CA_BUNDLE` is read by the `curl` tool, and whether libcurl as used by git honours it or OpenSSL's `SSL_CERT_*` is from memory **(unverified)**. Whether any of these, or `GIT_SSL_CAINFO`/`GIT_SSL_CAPATH`, is set as a CI variable is **(unverified)**, see A-21.

Both images serve `git` the same 118 certificates whichever of file or directory libcurl consults first, so the question T765 left open ("which of the file and the directory") no longer changes the answer for these digests.

## 3. Other cross-signs (crt.sh by key)

**Result: crt.sh knows 4 certificates on the disclosure's keys that the disclosure's JSON files do not list. All 4 chain only to eMudhra roots that are absent from the bundles, and all 4 are rejected by the image bundle. No cross-sign by any root in the bundles was found.**

Query: `https://crt.sh/?spkisha256=<hex>&output=json` for each of the 12 distinct `spki_sha256` values in `roots.json` and `impacted-intermediates.json`, 2026-11-07. crt.sh answered intermittently (HTTP 502, once 404); each query was retried until it returned HTTP 200 with valid JSON, and all 12 did. Matching to the disclosure was by issuer CN plus serial, then by certificate SHA-256 for the unmatched ones (fetched with `https://crt.sh/?d=<id>`).

| Key (`spki_sha256`, prefix) | Name | crt.sh certificates | Not in the disclosure's JSON |
|---|---|---|---|
| `bd153ed7…` | AAA Certificate Services | 1 (self-signed, id 331986) | none |
| `8d417db2…` | emSign ECC Root CA - G3 | 1 (self-signed, id 713604941) | none |
| `c619e478…` | emSign Root TLS CA - G3 | 2 | **id 14658191778**: cross-sign by `emSign ECC Root CA - G3`, 2024-07-11 to 2039-07-09, `CA:TRUE, pathlen:1`, sha256 `3094025792039A68AF6E553686410BDAB7C0D4A36B9084CBA64202E35D6EBBDD` |
| `0a6c2b2c…` | emSign Root CS CA - G3 | 2 | **id 14658191774**: cross-sign by `emSign ECC Root CA - G3`, 2024-07-11 to 2039-07-09, sha256 `7137FA71AD46BA686F746D1014AC57E8E6C6E9AF4AA2F73C0C44A5CF27DEBB59` |
| `ebed6475…` | EM DV TLS CA - G3B | 3 | **id 30002976010**: same issuer (`emSign Root TLS CA - G3`) and serial `00a4aee6…f214` as the listed certificate, same TBS bytes (sha256 of the TBS identical), but a different ECDSA signature (875 vs 876 bytes), so a different certificate SHA-256: `37E866582D43C35D7C17D47794B974F291B3047B868DC123382477F7A08AEFA8` |
| `49dd353d…` DV G3C, `e0254c7f…` EV G3B, `5c0660a2…` EV G3C, `43bffa19…` OV TLS G3B, `63ecefee…` OV TLS G3C, `ec4ffa1a…` OV CS G3B, `92c063d6…` OV CS G3C | the other 7 intermediates | 2 each, one under the eMudhra G3 root and one under AAA | none |

- **The two root cross-signs** are what `roots.json` means by `emSign ECC Root CA - G3`'s `role: cross_signer`; they are the path of T765's rollover chains. Signatures checked: `openssl verify -no-CApath -no-CAstore -CAfile <emSign ECC Root CA - G3 from roots.json>` gives `OK` for both. They matter only where `emSign ECC Root CA - G3` is trusted, which the bundles are not (point 1).
- **The DV G3B variant** has a valid signature from `emSign Root TLS CA - G3` (`openssl verify` with that root as the only CA: `OK`). An identical TBS under a second signature means a fingerprint-based blocklist of the 16 listed certificates would miss it; a key-based block (Python's `_ssl` SPKI denylist, T759 § 9) or an issuer-plus-serial block (OneCRL) would not. Whether it is a re-signature or a malleated signature was not established. It chains only to `emSign Root TLS CA - G3`, which is in no bundle here.
- **Against the image bundle** (`5961c0a3…`, `-no-CApath -no-CAstore -CAfile`): ids 30002976010, 14658191778 and 14658191774 each give `error 20 at 0 depth lookup: unable to get local issuer certificate`.
- **Limits.** crt.sh knows only certificates logged in CT or submitted to it; CA certificates need not be logged, so an unlogged cross-sign stays possible **(unverified)**. The search was by exact key; a subordinate CA with a different key under one of these roots is not a cross-sign of a compromised key and was not searched for. CCADB's own records for these keys were not read (`ccadb.my.salesforce-sites.com` did not answer from this host).

## 4. Runner settings

**Observed by the orchestrator, not by me** (v10.0.0 tag pipeline 3039977704, 2026-11-07; I cannot read job logs): all three jobs ran on `gitlab-runner 19.5.3 (33227fd4)`, "Preparing the \"docker\" executor", "Using Docker executor with image python:3.12-alpine@sha256:e064671c…"; the `release` job's "Fetching changes" said "Created fresh repository" (GIT_STRATEGY clone); the drift gate's `git fetch` through `scripts/run-allowlisted.py --keep CI_JOB_TOKEN` succeeded; no 401/403 in any log. The project is public, so a successful fetch does not show that a credential was used.

What this settles from T765 item 4:
- **Executor: Docker** (was an inference from tags). So T765's table for the Docker executor applies: the job's own `git` is not pinned when `FF_GIT_URLS_WITHOUT_TOKENS` is off, and is not pinned through the allowlist when it is on. The bundle (point 2) is the control.
- **Version: 19.5.3**, not 19.5.2. Tag `v19.5.3` is commit `33227fd4`, 2026-11-05 (GitLab API), which matches the observed revision. I did not re-read `shells/abstract.go` at `v19.5.3`; that T765's reading of 19.5.2 still holds is **(unverified)** — a patch release, so likely.

Still open, and not readable by this role without printing CI variables or runner config: `FF_GIT_URLS_WITHOUT_TOKENS`, whether `CI_SERVER_TLS_CA_FILE` is present in a real job, whether `SSL_CERT_FILE`/`SSL_CERT_DIR`/`CURL_CA_BUNDLE`/`GIT_SSL_*` are set as project, group or instance variables, and the runner's `helper_image` setting. Recorded as user action **A-21**.

## 5. The runner helper image's bundle

**Result: by source, runner 19.5.3 names the helper by tag, not digest; today's image behind that tag has the same bundle as the job images.**

- `helpers/container/helperimage/info.go` at `v19.5.3`: `GitLabRegistryName = "registry.gitlab.com/gitlab-org/gitlab-runner/gitlab-runner-helper"`, `DefaultFlavor = "alpine"`, `Version()` returns `v<MAJOR.MINOR.PATCH>`. `linux_info.go`: for the `alpine` flavor the tag is `<arch>-<revision>`, so `x86_64-v19.5.3`, and a `Prebuilt` name `prebuilt-alpine-x86_64` for the image archive shipped with the runner package. No digest anywhere in that path: **the helper is not pinned by digest** unless the runner's `helper_image` setting does so.
- Registry, 2026-11-07: tag `x86_64-v19.5.3` -> index `sha256:81cd16e217b2c45368c13c71197b11738158c435eee8a5fbb1bc2e34899ce338` -> amd64 manifest `sha256:40e668b75f140f477c588ea9d59843cc54aa51fd1a2a10312e976da9431206fd`; all 6 blobs hashed against their digests. History: `ADD alpine-minirootfs-3.24.3-x86_64.tar.gz` (the same base-layer blob `7b229517…` as the Node image), then `apk upgrade` and `apk add -u ca-certificates curl git …`.
- Its packages: `ca-certificates 20261020-r0`, `ca-certificates-bundle 20261020-r0`, `git 2.54.0-r0`, `libcurl 8.23.0-r0`. Its bundle in both layers that write it has sha256 `5961c0a3c65459931c023e0075c09733f09aea4ca439cb85bc4a08bb4f3f568b`, the file T765 tested (0 of 16), and its `/etc/ssl/certs` has 236 links like the Python image's.
- **Unverified:** whether the runner used this registry image or its local `prebuilt` archive (built from the same source, presumably, but not read), whether `helper_image` is overridden (A-21), and which digest the pipeline actually pulled. Because the tag is rebuilt with `apk upgrade`, its bundle follows Alpine's current package; with NSS 3.131.1 that excludes the emSign G3 root (point 1). The clone in the helper is pinned to the runner's CA chain when `CI_SERVER_TLS_CA_FILE` exists (T765, by source), so the helper's bundle is a second line there, not the only one.

## Could not establish

1. **A live connection** (T765 item 1). No `git` ran against a host serving one of the chains, and nothing ran in the image (no Docker). Next step, if the user approves that endpoint: in a throwaway job or rehearsal on the pinned Python image, `git ls-remote https://dv-g3b-emudhra.we-have-a-problem.com/` and expect a certificate verification error. Not in this task's scope.
2. **The runner's deployed settings** (A-21): `FF_GIT_URLS_WITHOUT_TOKENS`, presence of `CI_SERVER_TLS_CA_FILE` in a job, any `SSL_CERT_FILE`/`SSL_CERT_DIR`/`CURL_CA_BUNDLE`/`GIT_SSL_CAINFO`/`GIT_SSL_CAPATH`/`GIT_SSL_NO_VERIFY` CI variable, and `helper_image`.
3. **Which helper image ran**: registry tag or the runner's prebuilt archive, and its digest (A-21).
4. **Runner 19.5.3's git CA code**: T765 read `shells/abstract.go` at `v19.5.2`; not re-read at `v19.5.3` **(unverified, patch release)**.
5. **Unlogged cross-signs**: crt.sh covers only CT-logged or submitted certificates; CCADB was not reachable from this host.
6. **Non-amd64 images** (T765 item 7): not read.
7. **Mozilla bug wording**: the bug 2083449 quotes came through a summarising fetch and were not read verbatim. The removal itself is proven independently by the `certdata.txt` diff.
8. **`apk add git` keeps the bundle**: from the unversioned dependency and apk's solver behaviour as I remember it; not observed in a job.

## User actions

- **A-21 (new).** Owner: the runner's owner (the user). Read, without pasting any value into chat or an artifact, and report only presence or the boolean:
  - `FF_GIT_URLS_WITHOUT_TOKENS`: on or off (runner `config.toml` `[runners.feature_flags]`, or a CI variable of that name).
  - Whether a CI variable at project, group or instance level is named `SSL_CERT_FILE`, `SSL_CERT_DIR`, `CURL_CA_BUNDLE`, `GIT_SSL_CAINFO`, `GIT_SSL_CAPATH` or `GIT_SSL_NO_VERIFY` (names only).
  - Whether the runner has a `tls-ca-file` configured (which decides what `CI_SERVER_TLS_CA_FILE` holds) and whether `helper_image` is set, and if so to a digest.
  - Optionally, the helper image digest the runner pulled (`Using helper image` line of any job).
- **Next step for the bump procedure (for T766/T768, not done here):** besides "0 of 16 validate" and the `gitlab.com` control, the check should fail on a `ca-certificates`/`ca-certificates-bundle` version older than `20261020` and on any bundle certificate whose SPKI SHA-256 is one of the 12 in the disclosure's JSON files, and should include the 4 extra certificates of point 3 as further negative cases.
