#!/usr/bin/env bash

set -euo pipefail

# Run code-quality auto-fixes and validations for the backend service.
# Uses `uv` if available (preferred for speed), otherwise falls back to the
# currently active Python environment.

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${REPO_ROOT}/backend"

if [[ ! -d "${BACKEND_DIR}" ]]; then
  echo "Backend directory not found at ${BACKEND_DIR}" >&2
  exit 1
fi

use_uv=false
if command -v uv >/dev/null 2>&1; then
  use_uv=true
fi

run() {
  if [[ "${use_uv}" == true ]]; then
    (cd "${BACKEND_DIR}" && uv run "$@")
  else
    (cd "${BACKEND_DIR}" && "$@")
  fi
}

echo "== Formatting (ruff format + black) =="
run ruff format .
run black .

echo "== Linting (ruff check --fix) =="
run ruff check --fix .

echo "== Type checking (pyrefly) =="
run pyrefly check app tests

echo "== Testing (pytest) =="
run pytest

echo "All quality checks completed."
