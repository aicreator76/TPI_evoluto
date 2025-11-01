Param()

$ErrorActionPreference = "Stop"
$artDir = "artifacts"
New-Item -ItemType Directory -Force -Path $artDir | Out-Null

Write-Host ">>> Ruff"
ruff check .

Write-Host ">>> Mypy (best-effort)"
try { mypy . } catch { Write-Warning "mypy issues (not blocking)" }

Write-Host ">>> Pytest + coverage"
pytest -q --maxfail=1 --disable-warnings --cov --cov-report=xml --cov-report=term

Write-Host ">>> Bandit"
try { bandit -r . -q -f txt -o "$artDir/bandit.txt" } catch {}

Write-Host ">>> pip-audit"
try { pip-audit -f json -o "$artDir/pip-audit.json" } catch {}

Write-Host ">>> Trivy (filesystem)"
try { trivy fs --format sarif --output "$artDir/trivy.sarif" --ignore-unfixed . } catch {}

Write-Host "Artifacts in $artDir/"
