# CI: Enterprise Gates

## Checklist
- [ ] CI runs on Ubuntu & Windows
- [ ] Lint: ruff
- [ ] Types: mypy (best-effort)
- [ ] Tests: pytest + coverage.xml generated
- [ ] Security: bandit + pip-audit
- [ ] Trivy SARIF uploaded to Code Scanning
- [ ] Templates, scripts, runbook present

## Notes
Link to artifacts (coverage, SARIF, audit): Attach CI run links here.


## Checklist sicurezza
- [ ] CI – Enterprise verde (lint/type/pytest/pip-audit/bandit/trivy)
- [ ] CodeQL senza alert nuovi
- [ ] SBOM generato al prossimo push su main
- [ ] Nessun segreto nei diff
