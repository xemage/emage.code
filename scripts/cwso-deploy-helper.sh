#!/usr/bin/env bash
set -euo pipefail

# Helper for loading and validating CWSO_JWT_SECRET in emage.code workflows.
# The secret comes from the CWSO_JWT_SECRET environment variable, or from a
# file only when --secret-file is given explicitly. There is no default
# secret file (T694). The script never prints the secret, with one explicit
# exception: `export --secret-file <path> --print-secret` prints an export
# line meant for eval, and refuses when stdout is a terminal (SEC-T694-06).
#
# Secret file rule (SEC-T694-07, shared with scripts/mint-cwso-jwt.py,
# implementation/scripts/sia-executor.py and runtime/cwso/mcp_client.py): the
# secret is the first line that is not empty and does not start with `#`,
# with surrounding whitespace removed; later lines are ignored.
#
# Error messages name options and variables only, never a value or a path
# (SEC-T694-05).
#
# Usage examples:
#   CWSO_JWT_SECRET=... scripts/cwso-deploy-helper.sh verify
#   eval "$(scripts/cwso-deploy-helper.sh export --secret-file <path> --print-secret)"

SECRET_ENV_VAR="CWSO_JWT_SECRET"
DEFAULT_BASE_URL="http://localhost:8080"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'USAGE'
cwso-deploy-helper.sh

Commands:
  export            Print shell export statements (default); prints the
                    CWSO_JWT_SECRET line only with --secret-file and
                    --print-secret, and never to a terminal
  verify            Run a live auth smoke test using dispatch-test-sia.py
  up                Start local CWSO stack from deploy/docker-compose-t226.yml
  reload            Force-recreate CWSO services to apply updated secret material
  env-check         Print non-secret environment and connectivity checks
  help              Show this help

Options:
  --secret-file <path>   Explicit secret file path (no default). Without it
                         the secret is read from CWSO_JWT_SECRET only. The
                         secret is the first non-empty line that does not
                         start with '#', whitespace trimmed.
  --print-secret         Required for `export --secret-file` to print the
                         CWSO_JWT_SECRET export line; refused when stdout is
                         a terminal (use it inside eval "$(...)" only)
  --base-url <url>       CWSO base URL (default: http://localhost:8080)
  --workspace <path>     Workspace for verify (default: a new mktemp -d directory)
  --diag <path>          Diagnostic output for verify (default: in that directory)
  --parquet-store <path> Parquet store for verify (default: in that directory)

Examples:
  eval "$(scripts/cwso-deploy-helper.sh export --secret-file <path> --print-secret)"
  scripts/cwso-deploy-helper.sh up
  scripts/cwso-deploy-helper.sh reload
  scripts/cwso-deploy-helper.sh verify
USAGE
}

require_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: Required command not found: ${cmd}" >&2
    exit 1
  fi
}

# The one secret-file rule (SEC-T694-07): the first line that is not empty
# and does not start with '#', with surrounding whitespace removed.
secret_from_file() {
  local line
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    if [[ -n "$line" && "$line" != \#* ]]; then
      printf '%s' "$line"
      return 0
    fi
  done < "$1"
  return 0
}

# Errors name the option only, never the path or the value (SEC-T694-05).
read_secret() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "ERROR: the file given to --secret-file is not a regular file" >&2
    exit 1
  fi
  if [[ ! -r "$path" ]]; then
    echo "ERROR: the file given to --secret-file is not readable" >&2
    exit 1
  fi
  local secret
  secret="$(secret_from_file "$path")"
  if [[ -z "$secret" ]]; then
    echo "ERROR: the file given to --secret-file has no secret line" >&2
    exit 1
  fi
  printf '%s' "$secret"
}

require_env_secret() {
  if [[ -z "${CWSO_JWT_SECRET:-}" ]]; then
    echo "ERROR: ${SECRET_ENV_VAR} is not set. Export ${SECRET_ENV_VAR} or pass --secret-file <path> explicitly." >&2
    exit 1
  fi
}

resolve_secret() {
  if [[ -n "$SECRET_FILE" ]]; then
    read_secret "$SECRET_FILE"
    return
  fi
  require_env_secret
  printf '%s' "$CWSO_JWT_SECRET" | tr -d '\r\n'
}

# SEC-T694-06: the secret export line needs an explicit --print-secret and
# a stdout that is not a terminal, so it reaches eval and not the screen.
require_secret_print_allowed() {
  if [[ "$PRINT_SECRET" != "1" ]]; then
    echo "ERROR: export --secret-file prints ${SECRET_ENV_VAR}; add --print-secret and run it inside eval \"\$(...)\"" >&2
    exit 1
  fi
  if [[ -t 1 ]]; then
    echo "ERROR: refusing to print ${SECRET_ENV_VAR} to a terminal; run it inside eval \"\$(...)\"" >&2
    exit 1
  fi
}

cmd_export() {
  if [[ -n "$SECRET_FILE" ]]; then
    require_secret_print_allowed
    local secret
    secret="$(read_secret "$SECRET_FILE")"
    printf 'export CWSO_JWT_SECRET=%q\n' "$secret"
  else
    require_env_secret
  fi
  printf 'export CWSO_BASE_URL=%q\n' "$BASE_URL"
}

cmd_env_check() {
  local have_secret="no"
  if [[ -n "${CWSO_JWT_SECRET:-}" ]]; then
    have_secret="yes"
  fi
  echo "CWSO_JWT_SECRET_set=${have_secret}"
  echo "CWSO_BASE_URL=${BASE_URL}"
  curl -sS -m 5 "${BASE_URL}/healthz" >/dev/null && echo "healthz=reachable" || echo "healthz=unreachable"
}

# docker compose takes the jwt_secret secret from CWSO_JWT_SECRET
# (deploy/docker-compose-t226.yml); resolve it before `up` so that an
# explicit --secret-file also works and a missing value fails here.
export_secret_for_compose() {
  local secret
  secret="$(resolve_secret)"
  export CWSO_JWT_SECRET="$secret"
}

cmd_up() {
  export_secret_for_compose
  require_command docker
  docker compose -f "${REPO_ROOT}/deploy/docker-compose-t226.yml" up -d
  docker compose -f "${REPO_ROOT}/deploy/docker-compose-t226.yml" ps
}

cmd_reload() {
  export_secret_for_compose
  require_command docker
  docker compose -f "${REPO_ROOT}/deploy/docker-compose-t226.yml" up -d --force-recreate orchestrator rollout sia-executor
  docker compose -f "${REPO_ROOT}/deploy/docker-compose-t226.yml" ps
}

# SEC-T694-11: no fixed /tmp paths; unset locations go into a new private
# directory from mktemp -d (mode 700), which is kept for inspection.
prepare_verify_paths() {
  if [[ -z "$WORKSPACE" || -z "$DIAG" || -z "$PARQUET_STORE" ]]; then
    local run_dir
    run_dir="$(mktemp -d "${TMPDIR:-/tmp}/cwso-credcheck.XXXXXXXX")"
    echo "verify: run directory ${run_dir}" >&2
    WORKSPACE="${WORKSPACE:-${run_dir}/workspace}"
    DIAG="${DIAG:-${run_dir}/diagnostic.json}"
    PARQUET_STORE="${PARQUET_STORE:-${run_dir}/parquet-store}"
  fi
  mkdir -p "$(dirname "$DIAG")" "$WORKSPACE"
}

cmd_verify() {
  require_command python3
  local secret
  secret="$(resolve_secret)"
  prepare_verify_paths

  (
    cd "$REPO_ROOT"
    # The secret goes through the environment, not argv (not visible in ps).
    CWSO_JWT_SECRET="$secret" PYTHONPATH=. python3 implementation/scripts/dispatch-test-sia.py \
      --cwso-url "$BASE_URL" \
      --rollout-timeout 25 \
      --max-turns 2 \
      --backend claude \
      --model baseline \
      --workspace "$WORKSPACE" \
      --parquet-store "$PARQUET_STORE" \
      --diagnostic-output "$DIAG"
  )
}

# Print an option error that names the option only (SEC-T694-05): a value,
# or a bare positional argument, may be a secret and is never echoed.
reject_argument() {
  local arg="$1"
  if [[ "$arg" == -* ]]; then
    echo "ERROR: Unknown option: ${arg%%=*} (value not shown)" >&2
  else
    echo "ERROR: Unexpected positional argument (not shown)" >&2
  fi
  usage >&2
  exit 1
}

require_value() {
  if [[ $2 -lt 2 ]]; then
    echo "ERROR: $1 needs a value" >&2
    exit 1
  fi
}

COMMAND="export"
SECRET_FILE=""
PRINT_SECRET="0"
BASE_URL="$DEFAULT_BASE_URL"
WORKSPACE=""
DIAG=""
PARQUET_STORE=""

if [[ $# -gt 0 ]]; then
  case "$1" in
    export|verify|up|reload|env-check|help)
      COMMAND="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
  esac
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --secret-file)
      require_value "$1" $#
      SECRET_FILE="$2"
      shift 2
      ;;
    --print-secret)
      PRINT_SECRET="1"
      shift
      ;;
    --secret-source)
      echo "ERROR: --secret-source was removed (T694). The secret comes from ${SECRET_ENV_VAR}, or from --secret-file <path> when given explicitly." >&2
      exit 1
      ;;
    --base-url)
      require_value "$1" $#
      BASE_URL="$2"
      shift 2
      ;;
    --workspace)
      require_value "$1" $#
      WORKSPACE="$2"
      shift 2
      ;;
    --diag)
      require_value "$1" $#
      DIAG="$2"
      shift 2
      ;;
    --parquet-store)
      require_value "$1" $#
      PARQUET_STORE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      reject_argument "$1"
      ;;
  esac
done

case "$COMMAND" in
  export)
    cmd_export
    ;;
  verify)
    cmd_verify
    ;;
  up)
    cmd_up
    ;;
  reload)
    cmd_reload
    ;;
  env-check)
    cmd_env_check
    ;;
  help)
    usage
    ;;
esac
