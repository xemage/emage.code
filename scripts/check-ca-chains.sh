#!/bin/sh
# T766 (SEC-T756-02, CVE-2026-115557): prove that a CA trust store refuses every compromised
# eMudhra/emSign chain and key of the disclosure and still accepts a control chain.
#
# Usage: scripts/check-ca-chains.sh --cafile FILE FIXTURE_DIR
#        scripts/check-ca-chains.sh --capath DIR FIXTURE_DIR
#        scripts/check-ca-chains.sh --ca-release [APK_INSTALLED_DB]   (default /lib/apk/db/installed)
#
# FIXTURE_DIR (tests/fixtures/ca-chains, see its README.md) holds:
#   compromised/*.chain     the 16 chains of the disclosure's chains.zip, leaf first;
#   extra/*.cert            certificates on the disclosure's keys that crt.sh holds and the disclosure does not list
#                           (T767: two root cross-signs by emSign ECC Root CA - G3, a second EM DV TLS CA - G3B);
#   control/*.chain         chains that the store must accept (gitlab.com, the host CI's git fetches from);
#   disclosure-roots.certs  the 4 roots of the disclosure's roots.json;
#   disclosure-spki.txt     the SHA-256 of the 12 keys (SubjectPublicKeyInfo) in roots.json and impacted-intermediates.json.
#
# --cafile/--capath exit 0 only if: no compromised chain and no extra certificate validates against the store; every
# one of them validates against disclosure-roots.certs alone (so each refusal comes from the store's missing trust,
# not from an expired or malformed fixture); every control validates against the store; and no certificate in the
# store carries one of the 12 keys (a re-signed or cross-signed copy has a new hash but the same key).
# --ca-release exits 0 only if ca-certificates-bundle is installed, and it and ca-certificates (if installed) are
# at release 20261020 or later: that release removed emSign ECC Root CA - G3 (with it 8 of the 16 chains validate).
# Exit 1: a check failed. Exit 2: usage error.
#
# POSIX sh (busybox ash in both CI images; no bash there) and the openssl CLI only, no network. openssl verify:
# - `-attime`: the certificates expire (the first leaf on 2027-05-03), and an expired leaf is refused whatever the
#   store holds, which would turn the compromised half into a vacuous pass and the control half into a false failure.
#   Every fixture is valid at VERIFY_AT (2026-11-07T00:00:00Z), so the result depends on the store, not on the date.
# - `-partial_chain`: libcurl (git's HTTPS) sets X509_V_FLAG_PARTIAL_CHAIN by default, so a compromised intermediate
#   in the store would be trusted by git without its root. The flag makes this the more accepting verifier, so
#   "nothing validates" here also holds for a verifier without it.
# - `-purpose sslserver` for the chains (TLS server chains, git's use of the store); none for the extra CA
#   certificates, whose trust, not purpose, is the question.
# - Exactly one of -CAfile/-CApath, with the other default sources off, and `env -i`: only the store under test is
#   read, never the host's default store or an SSL_CERT_FILE/SSL_CERT_DIR/OPENSSL_CONF from the environment.
set -eu

VERIFY_AT=1794009600   # 2026-11-07T00:00:00Z, inside the validity of every fixture certificate
EXPECTED_COMPROMISED=16
EXPECTED_EXTRA=3
EXPECTED_KEYS=12
MIN_CA_RELEASE=20261020
APK_INSTALLED_DB=/lib/apk/db/installed
OPENSSL_PATH=/usr/bin:/bin:/usr/local/bin

die_usage() {
  echo "usage: $0 (--cafile FILE | --capath DIR) FIXTURE_DIR | --ca-release [APK_INSTALLED_DB]" >&2
  echo "error: $1" >&2
  exit 2
}

ossl() {
  env -i PATH="$OPENSSL_PATH" openssl "$@"
}

# Prints the store options for openssl verify; rejects a missing or empty store.
store_options() {
  case "$1" in
    --cafile)
      [ -f "$2" ] && grep -q -- '-----BEGIN CERTIFICATE-----' "$2" || die_usage "no certificate in the CA file"
      echo "-no-CApath -no-CAstore -CAfile $2" ;;
    --capath)
      [ -d "$2" ] && ls "$2" | grep -q '^[0-9a-f]\{8\}\.[0-9]*$' || die_usage "no hashed certificate in the CA directory"
      echo "-no-CAfile -no-CAstore -CApath $2" ;;
    *) die_usage "first argument must be --cafile, --capath or --ca-release" ;;
  esac
}

# verify_target FILE STORE_OPTIONS PURPOSE_OPTION -> status of openssl verify for the file's first certificate.
# The first certificate is split out because `openssl verify` checks the certificate(s) named on its command line;
# the whole file, that certificate included, is offered as untrusted intermediates.
verify_target() {
  ossl x509 -in "$1" -out "$WORK/target.pem" 2>/dev/null || return 3
  # shellcheck disable=SC2086 # $2 and $3 are option lists; paths were checked for whitespace in main
  ossl verify $2 $3 -attime "$VERIFY_AT" -partial_chain -untrusted "$1" "$WORK/target.pem" >"$WORK/out" 2>&1
}

# check_must_fail DIR SUFFIX STORE_OPTIONS ROOTS_OPTIONS PURPOSE -> one line per file; sets BAD, SEEN, VALID.
check_must_fail() {
  for file in "$1"/*"$2"; do
    [ -f "$file" ] || continue
    SEEN=$((SEEN + 1))
    name=$(basename "$file" "$2")
    if verify_target "$file" "$3" "$5"; then
      echo "FAIL compromised certificate VALIDATES against the store: $name"; BAD=$((BAD + 1)); VALID=$((VALID + 1))
      continue
    fi
    reason=$(grep -o 'error [0-9]* at [0-9]* depth' "$WORK/out" | head -n 1 || true)
    if ! verify_target "$file" "$4" "$5"; then
      echo "FAIL fixture does not validate against the disclosure roots (expired or malformed?): $name"
      sed 's/^/     /' "$WORK/out"; BAD=$((BAD + 1))
    else
      echo "ok   refused: $name (${reason:-no error code})"
    fi
  done
}

# check_controls STORE_OPTIONS -> one line per control chain; sets BAD, CONTROLS, GOOD.
check_controls() {
  for chain in "$FIXTURES"/control/*.chain; do
    [ -f "$chain" ] || continue
    CONTROLS=$((CONTROLS + 1))
    name=$(basename "$chain" .chain)
    if verify_target "$chain" "$1" "-purpose sslserver"; then
      echo "ok   control validates: $name"; GOOD=$((GOOD + 1))
    else
      echo "FAIL control does NOT validate against the store: $name"; sed 's/^/     /' "$WORK/out"; BAD=$((BAD + 1))
    fi
  done
}

# split_store MODE PATH -> writes one PEM per store certificate to $WORK/store/; prints the count.
# In --capath mode only the hash-named entries (<8 hex>.<n>) are read: those are what OpenSSL looks up.
split_store() {
  mkdir "$WORK/store"
  if [ "$1" = "--capath" ]; then
    for f in "$2"/*; do
      if basename "$f" | grep -q '^[0-9a-f]\{8\}\.[0-9]*$'; then cat "$f"; fi
    done
  else
    cat "$2"
  fi | awk -v dir="$WORK/store" '
    /-----BEGIN CERTIFICATE-----/ { n++; out = sprintf("%s/%05d.pem", dir, n) }
    out != "" { print > out }
    /-----END CERTIFICATE-----/ { close(out); out = "" }
    END { print n + 0 }'
}

# check_keys MODE PATH -> fails if any store certificate's SPKI SHA-256 is one of the disclosure's keys.
check_keys() {
  keys=$(grep -c '^[0-9a-f]\{64\} ' "$FIXTURES/disclosure-spki.txt" || true)
  [ "$keys" -eq "$EXPECTED_KEYS" ] || { echo "FAIL expected $EXPECTED_KEYS keys in disclosure-spki.txt, found $keys"; BAD=$((BAD + 1)); }
  total=$(split_store "$1" "$2"); hits=0
  for pem in "$WORK"/store/*.pem; do
    [ -f "$pem" ] || continue
    spki=$(ossl x509 -in "$pem" -pubkey -noout | ossl pkey -pubin -outform DER | ossl dgst -sha256 -r | cut -c1-64)
    case "$spki" in
      *[!0-9a-f]* | "") echo "FAIL could not read the key of a store certificate"; BAD=$((BAD + 1)); continue ;;
    esac
    if grep -q "^$spki " "$FIXTURES/disclosure-spki.txt"; then
      echo "FAIL the store holds a certificate on a compromised key: $(ossl x509 -in "$pem" -noout -subject -nameopt RFC2253)"
      hits=$((hits + 1)); BAD=$((BAD + 1))
    fi
  done
  [ "$total" -gt 0 ] || { echo "FAIL no certificate read from the store"; BAD=$((BAD + 1)); }
  echo "store certificates on a compromised key: $hits of $total"
}

# check_ca_release FILE -> the ca-certificates release check (see the header).
check_ca_release() {
  [ -f "$1" ] || die_usage "no such apk database file"
  awk -v min="$MIN_CA_RELEASE" '
    /^P:/ { pkg = substr($0, 3) }
    /^V:/ && (pkg == "ca-certificates" || pkg == "ca-certificates-bundle") {
      ver = substr($0, 3); rel = ver; sub(/[^0-9].*$/, "", rel)
      seen[pkg] = 1
      if (length(rel) != 8 || rel < min) { printf "FAIL %s %s is older than %s\n", pkg, ver, min; bad++ }
      else printf "ok   %s %s\n", pkg, ver
    }
    END {
      if (!seen["ca-certificates-bundle"]) { print "FAIL ca-certificates-bundle is not installed"; bad++ }
      if (bad) { print "RESULT: FAIL"; exit 1 }
      print "RESULT: PASS"
    }' "$1"
}

count_and_report() {
  if [ "$SEEN" -ne "$((EXPECTED_COMPROMISED + EXPECTED_EXTRA))" ]; then
    echo "FAIL expected $EXPECTED_COMPROMISED compromised chains and $EXPECTED_EXTRA extra certificates, found $SEEN"
    BAD=$((BAD + 1))
  fi
  [ "$CONTROLS" -ge 1 ] || { echo "FAIL no control chain"; BAD=$((BAD + 1)); }
  echo "compromised chains and certificates validating: $VALID of $SEEN; controls validating: $GOOD of $CONTROLS"
  [ "$BAD" -eq 0 ] || { echo "RESULT: FAIL ($BAD problem(s))"; exit 1; }
  echo "RESULT: PASS"
}

main() {
  if [ "${1:-}" = "--ca-release" ]; then
    [ "$#" -le 2 ] || die_usage "--ca-release takes at most one file"
    check_ca_release "${2:-$APK_INSTALLED_DB}"; return
  fi
  [ "$#" -eq 3 ] || die_usage "expected 3 arguments, got $#"
  case "$2$3" in *[[:space:]]*) die_usage "paths must not contain whitespace" ;; esac
  FIXTURES=$3
  [ -f "$FIXTURES/disclosure-roots.certs" ] && [ -f "$FIXTURES/disclosure-spki.txt" ] ||
    die_usage "FIXTURE_DIR lacks disclosure-roots.certs or disclosure-spki.txt"
  command -v openssl >/dev/null 2>&1 || die_usage "openssl CLI not found"
  store=$(store_options "$1" "$2")
  roots="-no-CApath -no-CAstore -CAfile $FIXTURES/disclosure-roots.certs"
  WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
  BAD=0 SEEN=0 VALID=0 CONTROLS=0 GOOD=0
  echo "store: $1 $2 (verification time $VERIFY_AT, 2026-11-07T00:00:00Z)"
  check_must_fail "$FIXTURES/compromised" .chain "$store" "$roots" "-purpose sslserver"
  check_must_fail "$FIXTURES/extra" .cert "$store" "$roots" ""
  check_controls "$store"
  check_keys "$1" "$2"
  count_and_report
}

main "$@"
