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
#   disclosure-spki.txt     the SHA-256 of the 14 compromised keys (SubjectPublicKeyInfo): the 12 of roots.json and
#                           impacted-intermediates.json and the 2 new keys of the rollover chains' self-issued
#                           EM DV TLS CA - G3B certificates (T859: in chains.zip, not in the JSON).
#
# --cafile/--capath exit 0 only if: no compromised chain and no extra certificate validates against the store; every
# one of them validates against disclosure-roots.certs alone (so each refusal comes from the store's missing trust,
# not from an expired or malformed fixture); every control validates against the store; and no certificate in the
# store carries one of the 14 keys (a re-signed or cross-signed copy has a new hash but the same key).
# The fixtures are cross-checked first (SEC-T768-02): 16 chains, 3 extra certificates, 4 roots and 14 keys, each counted
# on its own, and every root, every non-leaf chain certificate and every extra certificate carries a listed key, so an
# edit that drops a key line or swaps a fixture fails here. The store scan (SEC-T768-01) reads every PEM block that
# OpenSSL's CA loaders accept as a certificate (BEGIN CERTIFICATE, TRUSTED CERTIFICATE, X509 CERTIFICATE), fails on
# any other BEGIN type, and fails unless the certificates read equal the PEM blocks.
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
EXPECTED_KEYS=14
EXPECTED_ROOTS=4
CERT_BEGIN_RE='-----BEGIN (TRUSTED |X509 )?CERTIFICATE-----'
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
      [ -f "$2" ] && grep -Eq -- "$CERT_BEGIN_RE" "$2" || die_usage "no certificate in the CA file"
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

# split_pems DIR -> reads PEM text on stdin, writes one file per certificate block to DIR; prints "<certificates>
# <other BEGIN blocks>". A certificate block is any form OpenSSL's CA loaders take (see CERT_BEGIN_RE).
split_pems() {
  mkdir -p "$1"
  awk -v dir="$1" -v re="$CERT_BEGIN_RE" '
    /-----BEGIN / { if ($0 ~ re) { n++; out = sprintf("%s/%05d.pem", dir, n) } else { other++ } }
    out != "" { print > out }
    /-----END ([A-Z0-9]+ )*CERTIFICATE-----/ { if (out != "") close(out); out = "" }
    END { print n + 0, other + 0 }'
}

# split_store MODE PATH -> split_pems of the store into $WORK/store/.
# In --capath mode only the hash-named entries (<8 hex>.<n>) are read: those are what OpenSSL looks up.
split_store() {
  if [ "$1" = "--capath" ]; then
    for f in "$2"/*; do
      if basename "$f" | grep -q '^[0-9a-f]\{8\}\.[0-9]*$'; then cat "$f"; fi
    done
  else
    cat "$2"
  fi | split_pems "$WORK/store"
}

# spki_of PEM -> the SHA-256 of the certificate's DER SubjectPublicKeyInfo, or nothing. The key is read into a file
# first: piped straight into dgst, an unreadable certificate would hash the empty input to a valid-looking hex string.
spki_of() {
  ossl x509 -in "$1" -pubkey -noout >"$WORK/pubkey" 2>/dev/null || return 0
  ossl pkey -pubin -outform DER -in "$WORK/pubkey" -out "$WORK/spki.der" 2>/dev/null || return 0
  ossl dgst -sha256 -r "$WORK/spki.der" | cut -c1-64
}

# listed_key PEM WHAT -> fails (BAD) unless the certificate's key is one of disclosure-spki.txt.
listed_key() {
  spki=$(spki_of "$1")
  case "$spki" in *[!0-9a-f]* | "") echo "FAIL could not read the key of fixture $2"; BAD=$((BAD + 1)); return ;; esac
  grep -q "^$spki " "$FIXTURES/disclosure-spki.txt" && return
  echo "FAIL fixture $2 carries a key that disclosure-spki.txt does not list: $spki"; BAD=$((BAD + 1))
}

# check_count WHAT FOUND EXPECTED
check_count() {
  [ "$2" -eq "$3" ] || { echo "FAIL expected $3 $1, found $2"; BAD=$((BAD + 1)); }
}

# check_fixtures -> SEC-T768-02: per-directory counts and every CA certificate of the fixtures on a listed key.
check_fixtures() {
  keys=$(grep -c '^[0-9a-f]\{64\} ' "$FIXTURES/disclosure-spki.txt" || true)
  distinct=$(grep '^[0-9a-f]\{64\} ' "$FIXTURES/disclosure-spki.txt" | cut -c1-64 | sort -u | wc -l)
  check_count "keys in disclosure-spki.txt" "$keys" "$EXPECTED_KEYS"
  check_count "distinct keys in disclosure-spki.txt" "$distinct" "$EXPECTED_KEYS"
  chains=0; extras=0
  for f in "$FIXTURES"/compromised/*.chain; do [ -f "$f" ] && chains=$((chains + 1)); done
  for f in "$FIXTURES"/extra/*.cert; do [ -f "$f" ] && extras=$((extras + 1)); done
  check_count "compromised chains" "$chains" "$EXPECTED_COMPROMISED"
  check_count "extra certificates" "$extras" "$EXPECTED_EXTRA"
  set -- $(split_pems "$WORK/roots" <"$FIXTURES/disclosure-roots.certs")
  check_count "roots in disclosure-roots.certs" "$1" "$EXPECTED_ROOTS"
  check_count "non-certificate PEM blocks in disclosure-roots.certs" "$2" 0
  for pem in "$WORK"/roots/*.pem; do [ -f "$pem" ] && listed_key "$pem" "root $(basename "$pem" .pem)"; done
  i=0
  for f in "$FIXTURES"/compromised/*.chain "$FIXTURES"/extra/*.cert; do
    [ -f "$f" ] || continue
    i=$((i + 1)); split_pems "$WORK/fx$i" <"$f" >/dev/null
    case "$f" in */extra/*) first=00001 ;; *) first=none ;; esac
    for pem in "$WORK/fx$i"/*.pem; do
      n=$(basename "$pem" .pem)
      [ "$n" = 00001 ] && [ "$first" = none ] && continue   # a chain's leaf carries its own key
      listed_key "$pem" "$(basename "$f") certificate $n"
    done
  done
  echo "fixtures: $chains chains, $extras extra certificates, $1 roots, $keys keys"
}

# check_keys MODE PATH -> fails if any store certificate's SPKI SHA-256 is one of the disclosure's keys.
check_keys() {
  set -- $(split_store "$1" "$2"); total=$1 other=$2 hits=0 read=0
  [ "$other" -eq 0 ] || { echo "FAIL the store holds $other PEM block(s) of a type other than a certificate"; BAD=$((BAD + 1)); }
  for pem in "$WORK"/store/*.pem; do
    [ -f "$pem" ] || continue
    spki=$(spki_of "$pem")
    case "$spki" in
      *[!0-9a-f]* | "") echo "FAIL could not read the key of a store certificate"; BAD=$((BAD + 1)); continue ;;
    esac
    read=$((read + 1))
    if grep -q "^$spki " "$FIXTURES/disclosure-spki.txt"; then
      echo "FAIL the store holds a certificate on a compromised key: $(ossl x509 -in "$pem" -noout -subject -nameopt RFC2253)"
      hits=$((hits + 1)); BAD=$((BAD + 1))
    fi
  done
  [ "$total" -gt 0 ] || { echo "FAIL no certificate read from the store"; BAD=$((BAD + 1)); }
  [ "$read" -eq "$total" ] || { echo "FAIL certificates read ($read) differ from certificate PEM blocks ($total)"; BAD=$((BAD + 1)); }
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
  check_fixtures
  check_must_fail "$FIXTURES/compromised" .chain "$store" "$roots" "-purpose sslserver"
  check_must_fail "$FIXTURES/extra" .cert "$store" "$roots" ""
  check_controls "$store"
  check_keys "$1" "$2"
  count_and_report
}

main "$@"
