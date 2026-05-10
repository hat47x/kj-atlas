# 04_Documentation Hub

このREADMEは `04_Documentation/` 配下の公開向け運用ドキュメント導線を定義します。

## DOC-OPS-05 issue ↔ documentation mapping（Stream H）

| DOC-OPS-05 Issue | Primary target document | Classification |
| --- | --- | --- |
| `issue-doc-ops-05-01-04doc-canonicalization.md` | `04_Documentation/canonicalization.md` | Move internal |
| `issue-doc-ops-05-02-04doc-codex-skill-operations.md` | `04_Documentation/codex_skill_operations.md` | Move internal |
| `issue-doc-ops-05-03-04doc-configuration.md` | `04_Documentation/configuration.md` | Improve external |
| `issue-doc-ops-05-04-04doc-diagnostics.md` | `04_Documentation/diagnostics.md` | Improve external |
| `issue-doc-ops-05-05-04doc-documentation-quality.md` | `01_Plans/documentation_quality.md`（例外: 04配下対象なし） | Move internal |
| `issue-doc-ops-05-06-04doc-e2e-testing.md` | `04_Documentation/e2e_testing.md` | Improve external |
| `issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md` | `04_Documentation/e2e_verification_log_2026-03-03.md` | Move internal |
| `issue-doc-ops-05-08-04doc-installation.md` | `04_Documentation/installation.md` | Improve external |
| `issue-doc-ops-05-09-04doc-local-llm-ops-guide.md` | `04_Documentation/local_llm_ops_guide.md` | Improve external |
| `issue-doc-ops-05-10-04doc-narratives.md` | `04_Documentation/narratives.md` | Improve external |
| `issue-doc-ops-05-11-04doc-operations.md` | `04_Documentation/operations.md` | Improve external |
| `issue-doc-ops-05-12-04doc-release.md` | `04_Documentation/release.md` | Improve external |
| `issue-doc-ops-05-13-04doc-security.md` | `04_Documentation/security.md` | Improve external |
| `issue-doc-ops-05-14-04doc-security-operational-guidelines.md` | `04_Documentation/security_operational_guidelines.md` | Improve external |

## Verification checklist（docs-only）

- 用語: Audience / Goal / Non-goal / Public boundary / GoNoGoGate / VerificationLevel
- 固定値: `VerificationLevel=docs-check`、自己修復上限3回（4回目はHold）
- 導線: issueと対象文書の相互参照を維持

## Related governance

- Documentation quality baseline: `../01_Plans/documentation_quality.md`
- Architecture baseline: `../02_Architecture/architecture.md`
- Security and safeMode boundary: `../04_Documentation/security.md`
