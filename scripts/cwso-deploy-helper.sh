#!/usr/bin/env bash
set -euo pipefail

# Helper for loading and validating CWSO_JWT_SECRET in emage.code workflows.
# The secret comes from the CWSO_JWT_SECRET environment variable, or from a
# file only when --secret-file is given explicitly. There is no default
# secret file (T694). The script never prints the secret, except that
# `export --secret-file <path>` prints an export line meant for eval.
# Usage examples:
#   CWSO_JWT_SECRET=... scripts/cwso-deploy-helper.sh verify
#   eval "$(scripts/cwso-deploy-helper.sh export --secret-file <path>)"

SECRET_ENV_VAR="CWSO_JWT_SECRET"
DEFAULT_BASE_URL="http://localhost:8080"
DEFAULT_WORKSPACE="/tmp/cwso-credcheck"
DEFAULT_DIAG="/tmp/cwso-credcheck.json"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'USAGE'
cwso-deploy-helper.sh

Commands:
  export            Print shell export statements (default); prints the
                    CWSO_JWT_SECRET line only with an explicit --secret-file
  verify            Run a live auth smoke test using dispatch-test-sia.py
  up                Start local CWSO stack from deploy/docker-compose-t226.yml
  reload            Force-recreate CWSO services to apply updated secret material
  env-check         Print non-secret environment and connectivity checks
  help              Show this help

Options:
  --secret-file <path>   Explicit secret file path (no default). Without it
                         the secret is read from CWSO_JWT_SECRET only.
  --base-url <url>       CWSO base URL (default: http://localhost:8080)
  --workspace <path>     Workspace for verify command (default: /tmp/cwso-credcheck)
  --diag <path>          Diagnostic output path for verify command (default: /tmp/cwso-credcheck.json)

Examples:
  eval "$(scripts/cwso-deploy-helper.sh export --secret-file <path>)"
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

read_secret() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "ERROR: Secret file not found: ${path}" >&2
    exit 1
  fi
  local secret
  secret="$(tr -d '\r\n' < "$path")"
  if [[ -z "$secret" ]]; then
    echo "ERROR: Secret file is empty: ${path}" >&2
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

cmd_export() {
  if [[ -n "$SECRET_FILE" ]]; then
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

cmd_verify() {
  require_command python3
  local secret
  secret="$(resolve_secret)"

  mkdir -p "$(dirname "$DIAG")"
  mkdir -p "$WORKSPACE"

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
      --parquet-store /tmp/t226-parquet-store \
      --diagnostic-output "$DIAG"
  )
}

COMMAND="export"
SECRET_FILE=""
BASE_URL="$DEFAULT_BASE_URL"
WORKSPACE="$DEFAULT_WORKSPACE"
DIAG="$DEFAULT_DIAG"

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
      SECRET_FILE="$2"
      shift 2
      ;;
    --secret-source)
      echo "ERROR: --secret-source was removed (T694). The secret comes from ${SECRET_ENV_VAR}, or from --secret-file <path> when given explicitly." >&2
      exit 1
      ;;
    --base-url)
      BASE_URL="$2"
      shift 2
      ;;
    --workspace)
      WORKSPACE="$2"
      shift 2
      ;;
    --diag)
      DIAG="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage
      exit 1
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
