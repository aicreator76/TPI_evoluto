#!/usr/bin/env bash
set -euo pipefail

ART_DIR="artifacts"
mkdir -p "$ART_DIR"

echo ">>> Ruff"
ruff check .

echo ">>> Mypy (best-effort)"
set +e
mypy . || echo "mypy issues (not blocking)"
set -e

echo ">>> Pytest + coverage"
pytest -q --maxfail=1 --disable-warnings --cov --cov-report=xml --cov-report=term

echo ">>> Bandit"
bandit -r . -q -f txt -o "${ART_DIR}/bandit.txt" || true

echo ">>> pip-audit"
pip-audit -f json -o "${ART_DIR}/pip-audit.json" || true

echo ">>> Trivy (filesystem)"
trivy fs --format sarif --output "${ART_DIR}/trivy.sarif" --ignore-unfixed . || true

echo "Artifacts in ${ART_DIR}/"
