#!/usr/bin/env bash
set -euo pipefail

# Helper for loading and validating CWSO_JWT_SECRET in emage.code workflows.
# Usage examples:
#   eval "$(scripts/cwso-deploy-helper.sh export)"
#   scripts/cwso-deploy-helper.sh verify

DEFAULT_SECRET_FILE="/home/emage/Code/emage/CWSO/.env.jwt.dev"
DEFAULT_BASE_URL="http://localhost:8080"
DEFAULT_WORKSPACE="/tmp/cwso-credcheck"
DEFAULT_DIAG="/tmp/cwso-credcheck.json"
DEFAULT_SECRET_SOURCE="file"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'USAGE'
cwso-deploy-helper.sh

Commands:
  export            Print shell export statements for CWSO_JWT_SECRET (default)
  verify            Run a live auth smoke test using dispatch-test-sia.py
  up                Start local CWSO stack from deploy/docker-compose-t226.yml
  reload            Force-recreate CWSO services to apply updated secret material
  env-check         Print non-secret environment and connectivity checks
  help              Show this help

Options:
  --secret-file <path>   Secret file path (default: /home/emage/Code/emage/CWSO/.env.jwt.dev)
  --secret-source <src>  Token source: file | env | auto (default: file)
  --base-url <url>       CWSO base URL (default: http://localhost:8080)
  --workspace <path>     Workspace for verify command (default: /tmp/cwso-credcheck)
  --diag <path>          Diagnostic output path for verify command (default: /tmp/cwso-credcheck.json)

Examples:
  eval "$(scripts/cwso-deploy-helper.sh export)"
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

cmd_export() {
  local secret
  secret="$(read_secret "$SECRET_FILE")"
  printf 'export CWSO_JWT_SECRET=%q\n' "$secret"
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

cmd_up() {
  require_command docker
  docker compose -f "${REPO_ROOT}/deploy/docker-compose-t226.yml" up -d
  docker compose -f "${REPO_ROOT}/deploy/docker-compose-t226.yml" ps
}

cmd_reload() {
  require_command docker
  docker compose -f "${REPO_ROOT}/deploy/docker-compose-t226.yml" up -d --force-recreate orchestrator rollout sia-executor
  docker compose -f "${REPO_ROOT}/deploy/docker-compose-t226.yml" ps
}

cmd_verify() {
  require_command python3
  local secret
  case "$SECRET_SOURCE" in
    file)
      secret="$(read_secret "$SECRET_FILE")"
      ;;
    env)
      if [[ -z "${CWSO_JWT_SECRET:-}" ]]; then
        echo "ERROR: CWSO_JWT_SECRET not set in environment" >&2
        exit 1
      fi
      secret="$(printf '%s' "$CWSO_JWT_SECRET" | tr -d '\r\n')"
      ;;
    auto)
      if [[ -n "${CWSO_JWT_SECRET:-}" ]]; then
        secret="$(printf '%s' "$CWSO_JWT_SECRET" | tr -d '\r\n')"
      else
        secret="$(read_secret "$SECRET_FILE")"
      fi
      ;;
    *)
      echo "ERROR: Invalid --secret-source value: ${SECRET_SOURCE} (expected file|env|auto)" >&2
      exit 1
      ;;
  esac

  mkdir -p "$(dirname "$DIAG")"
  mkdir -p "$WORKSPACE"

  (
    cd "$REPO_ROOT"
    PYTHONPATH=. python3 implementation/scripts/dispatch-test-sia.py \
      --cwso-url "$BASE_URL" \
      --jwt-secret "$secret" \
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
SECRET_FILE="$DEFAULT_SECRET_FILE"
SECRET_SOURCE="$DEFAULT_SECRET_SOURCE"
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
      SECRET_SOURCE="$2"
      shift 2
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
