# Issue Draft: HIL-RS-02 A3 Operations/Documentation 同期

- Type: Documentation
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: TBD
- Priority: P2
- Owner: Operations Owner
- Scope: `04_Documentation/`, `01_Plans/`
- Related Backlog: `HIL-RS-02`
- Related ADR/Spec: `ADR-0027`, `ADR-0019`, `04_Documentation/operations.md`, `04_Documentation/security.md`
- Expected verification level: `docs-check`

## 1) 背景

- A2後に運用手順を同期しないと、検証・監査手順が実装と乖離する。

## 2) 目的

- 可逆統合フローの運用手順、異常時ロールバック、監査証跡採取を運用文書へ反映する。

## 3) スコープ

- operations/security/e2e_testingの必要差分更新。
- project-progress-dashboard の実施ログ同期。

## 4) 非スコープ

- 認証認可モデルの新規設計。
- backend API仕様変更。

## 5) 受入条件

- AC-1: 新運用手順が既存手順と矛盾しない。
- AC-2: ロールバック手順が明記される。
- AC-3: strict mode例外の状態遷移（`StoppedForClarification` / `RollbackPending` / `Closed`）と2者承認責務が operations/security で一致している。
- AC-4: D1〜D4固定値（承認TTL=4h、最大2h、代理承認なし、48hレビュー+15m/60m）が operations/security 双方で一致している。
- AC-5: docs-checkが通過する。

## 6) 検証方法

- `python 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "StoppedForClarification|RollbackPending|Closed|D1〜D4|Security Officer|System Owner|Platform Operator" 04_Documentation/operations.md 04_Documentation/security.md`

## 7) 依存関係

- `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md` Open化

## 8) リスク

- 運用文書の同期遅延で現場手順が旧仕様のまま残る。

## 9) 着手順

1. 差分棚卸し
2. 文書反映
3. 相互リンク/用語/固定値の監査
4. docs-check
