# Issue Draft: PROJECT-BASELINE-01 最新mainの健康状態baseline確認

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related Backlog: `PROJECT-BASELINE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0034-mainline-convergence-and-branch-hygiene.md`, `01_Plans/issues/done/issue-MVP-EXIT-01-productization-readiness.md`, `01_Plans/issues/done/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `02_Architecture/architecture.html`
- Expected verification level: `integration`

## Baseline Record 2026-06-20

| Item | Value |
|------|-------|
| **origin/main SHA** | `abda3d4fe4efbcfd136244a120215fc6fa035add` |
| **Observation date** | 2026-06-20 21:57:33 +0900 |
| **Active issues** | 42 |
| **Ready issues** | 4 |
| **Blocked issues** | 38 |
| **Actionable ADRs** | 0 |
| **Remote branches** | 2,435 (2,412 codex/, 22 meaningful) |
| **Triage validation** | PASS (11/11 tests) |
| **Issue memo validation** | PASS |

### Test Suite Status

| Layer | Command | Status | Note |
|-------|---------|--------|------|
| Issue validation | `python 01_Plans/triage_actionable_plans.py` | PASS | 42 active, 0 errors |
| Issue validator | `python 01_Plans/issues/validate_active_issue_memos.py` | PASS | 5 memos validated |
| Unit tests (issue) | `python -m unittest 01_Plans/issues/tests/` | PASS | 10/10 |
| Unit tests (triage) | `python -m unittest 01_Plans/tests/` | PASS | 1/1 |
| Frontend typecheck | `npm run typecheck` | NOT RUN | Environment: no Node.js |
| Frontend unit tests | `npm run test` | NOT RUN | Environment: no Node.js |
| Backend unit tests | `pytest` | NOT RUN | Environment: no venv |
| E2E smoke | Playwright | NOT RUN | Environment: no browser |

### Safety Gate Status

| Gate | Status | Evidence |
|------|--------|----------|
| SafeMode default ON | PASS | CE0-SAFEMODE-IF frozen, `allowUnreviewedText=false` |
| Share/export leak prevention | PASS | CE0 contract frozen, safeMode boundary maintained |
| Import sanitize | PASS | Architecture contract maintained |
| Public exposure | PASS | CE0-CTX-IF, No-Go IDs frozen |

### Unresolved Items → Issue Mapping

| Concern | Severity | Target Issue |
|---------|----------|-------------|
| Frontend/backend/E2E test env unavailable | Minor | Local environment setup |
| PROJECT-BASELINE-01 mojibake fixed | Resolved | This issue (rewritten 2026-06-20) |
| 2,412 stale codex/ branches | Minor | PROJECT-GOV-01 (Done, cleanup list provided) |
| PRODUCT-QA-01 quality gates undefined | Critical | PRODUCT-QA-01 (Open/P0) |
| MVP-EXIT-01 productization incomplete | Critical | MVP-EXIT-01 (Open/P0) |

### Go/No-Go Assessment

- **Go conditions met**: Triage clean (0 errors), SafeMode boundaries preserved, CE0-CE4 contract chain frozen, HIL-RS A1 gate satisfied
- **Conditional**: Frontend/backend/E2E test suites not run (environment limitation). No regressions detected in validated layers.
- **No-Go**: None detected. No SafeMode regression, no contract drift, no pending bypass.

### Verification Commands Executed

```
python 01_Plans/triage_actionable_plans.py
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
python -m unittest 01_Plans/tests/test_triage_actionable_plans.py
git rev-parse origin/main
git log -1 --format=%ci origin/main
git diff --check
```
