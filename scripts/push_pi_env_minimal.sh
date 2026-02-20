#!/usr/bin/env bash
set -euo pipefail

# Stage a minimal env directory for Prime hub pushes.
# Rationale: `prime env push --path .` uploads the whole directory contents.
# We keep the hub artifact lean by pushing only runtime-relevant files.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE_ROOT="${ROOT}/out/pi_env_stage_tower_defence"
ENV_STAGE="${STAGE_ROOT}/tower_defence"

rm -rf "${STAGE_ROOT}"
mkdir -p "${ENV_STAGE}/src"

cp -f "${ROOT}/pyproject.toml" "${ENV_STAGE}/pyproject.toml"
cp -f "${ROOT}/README.md" "${ENV_STAGE}/README.md"
cp -f "${ROOT}/LICENSE" "${ENV_STAGE}/LICENSE"
cp -f "${ROOT}/env.py" "${ENV_STAGE}/env.py"

rsync -a --delete --exclude '__pycache__/' --exclude '*.pyc' \
  "${ROOT}/src/prime_td_env/" "${ENV_STAGE}/src/prime_td_env/"
rsync -a --delete --exclude '__pycache__/' --exclude '*.pyc' \
  "${ROOT}/src/tower_defence/" "${ENV_STAGE}/src/tower_defence/"

echo "Staged minimal env directory at: ${ENV_STAGE}"
echo "Top-level files:"
find "${ENV_STAGE}" -maxdepth 2 -type f | sed "s#^${ENV_STAGE}/##" | sort

if [[ "${1:-}" == "--push" ]]; then
  echo
  echo "Pushing staged env to Prime hub..."
  prime env push --path "${ENV_STAGE}"
else
  echo
  echo "To push: prime env push --path \"${ENV_STAGE}\""
  echo "Or:   ${0} --push"
fi
