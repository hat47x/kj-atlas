# Issue: HIL-RS-02 A3 strict-mode例外運用 文書同期（Stream G）

- Type: Documentation Sync
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Owner: Stream G
- Source Issue: TBD
- Expected verification level: `docs-check`
- Scope:
  - `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
  - `02_Architecture/strict_mode_exception_approval_flow.md`
  - `04_Documentation/security.md`
  - `04_Documentation/security_operational_guidelines.md`
  - `04_Documentation/e2e_testing.md`
- Out of scope:
  - `04_Documentation/operations.md`
  - `01_Plans/project-progress-dashboard.md`
  - `01_Plans/issues/README.md`
  - `03_Implement/*`
- Related ADR/Spec:
  - `ADR-0019`
  - `ADR-0027`
  - `02_Architecture/strict_mode_exception_approval_flow.md`

## 1) Context

strict mode 例外運用（AUTH-OPS-03）は D1〜D4 固定値で運用するが、文書間で状態語彙・導線・責務分離のドリフトが混在すると運用停止条件が曖昧化する。

特に A3 同期では次を同時に満たす必要がある。

1. 用語一致（Security Officer / System Owner / Platform Operator）
2. 責務分離一致（2者承認と実行責務分離）
3. 固定値一致（D1〜D4）
4. 導線一致（architecture -> security -> guidelines -> e2e）

## 2) Decision

Stream G は docs-only で上記5ファイルのみ更新し、strict mode 例外運用の canonical 表現を次で固定する。

- 状態語彙: `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed` と `StoppedForClarification`
- D1〜D4 固定値:
  - D1: Security Officer先行、承認TTL=4h
  - D2: tenant単位、最大2h
  - D3: 2者共同判定、代理承認なし
  - D4: 変更台帳+監査ID相互参照、48hレビュー、15m一次/60m二次エスカレーション
- フェイルセーフ: D1〜D4 の不整合を検知した時点で即停止（TODO化しない）

## 3) Consequences

- 文書横断ドリフト（用語/責務/固定値/導線）の再発検知が容易になる。
- `operations.md` を編集せずに、security/guidelines/e2e 側から整合検証を完結できる。
- Verify 失敗時は自己修復を最大3回までに制限し、4回目相当は停止して差分を記録する。

## 4) Phase Plan（固定）

### Phase 1 Read

- `strict_mode_exception_approval_flow.md` を正本として再読。
- `security.md` / `security_operational_guidelines.md` / `e2e_testing.md` の語彙・固定値・導線を棚卸し。

### Phase 2 ADR必要時のCDC明文化

- ADR変更が必要な場合のみ Context / Decision / Consequences を追記して承認待ちへ遷移。
- ADR不要の場合は issue 側 CDC を正本として作業継続。

### Phase 3 Plan（AC/DoD）

- AC-1: 役割語彙が3文書+アーキ文書で一致。
- AC-2: 状態語彙が canonical に一致。
- AC-3: D1〜D4 固定値が一致。
- AC-4: 導線（architecture -> security -> guidelines -> e2e）が明示。
- AC-5: `operations.md` / dashboard / issues README / 実装コードを編集しない。
- AC-6: docs-check を再現可能コマンドで記録。

DoD:
- 上記 AC を全て満たし、`git diff --check` が成功。
- D1〜D4 不整合ゼロを証跡付きで確認。

### Phase 4 Execute

- 許可ファイルのみ更新。
- alias語彙（Requested / ExceptionActive など）を canonical へ収束。
- 参照リンクと停止条件の明文化を同期。

### Phase 5 Verify / Proceed

実行コマンド:

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
rg -n "Security Officer|System Owner|Platform Operator|DraftRequest|ApprovalPending|Approved|ActiveException|RollbackPending|Closed|StoppedForClarification|D1|D2|D3|D4|4h|2h|48h|15m|60m" \
  02_Architecture/strict_mode_exception_approval_flow.md \
  04_Documentation/security.md \
  04_Documentation/security_operational_guidelines.md \
  04_Documentation/e2e_testing.md
rg -n "operations\.md|security_operational_guidelines\.md|e2e_testing\.md" \
  02_Architecture/strict_mode_exception_approval_flow.md \
  04_Documentation/security.md \
  04_Documentation/security_operational_guidelines.md \
  04_Documentation/e2e_testing.md
git diff --check
```

Proceed 条件:

- すべての Verify コマンドが成功。
- D1〜D4 不整合が0件。
- 編集禁止ファイルへの差分が0件。

## 5) Fail-safe（即停止条件）

1. D1〜D4 固定値に不整合が出た場合。
2. `StoppedForClarification` を回避する運用文言が混入した場合。
3. SafeMode既定ON / share-export漏えい防止の後退表現が混入した場合。
4. 許可外ファイル編集が必要になった場合。

停止時は以下を記録する。

- 不整合箇所（ファイル+行）
- 発生フェーズ
- 修復案（最小差分）
- 再開条件
