# ADR-0022: Documentation Quality Gates

- Status: Proposed
- Date: 2026-03-08
- Deciders: Project Maintainers
- Scope: `01_Plans/adr/`, `04_Documentation/`, `.github/workflows/`

## Context

DOC-OPS-04 の前処理監査では、Documentation Quality に関して以下が未統一であることが確認された。

- docs-check 運用は存在するが、`lint` / `link` / `metadata` の必須境界が文書化されていない。
- 品質確認がレビュー担当者の目視に依存し、回帰検知の一貫性が不足している。
- 例外許可（緊急対応・一時的ドリフト許容）の記録形式が固定されておらず、監査可能性が不足する。

この状態では、同一品質基準でのドキュメント更新が継続しにくく、
文書品質のばらつきと検知遅延が再発しやすい。

## Decision

Documentation 変更に対する品質ゲートを、**必須ゲート・警告ゲート・例外承認フロー**の3層で定義し、
品質基準と例外運用を分離管理する。

### 1. ゲート分類

1. 必須ゲート（merge blocking）
   - Front matter / 必須メタ情報の整合
   - 見出し構造の整合（レベル飛び・必須章欠落）
   - 参照リンク整合（内部リンク切れ）
2. 警告ゲート（non-blocking）
   - 可読性スコア（文長・箇条書き密度・見出し粒度）
   - 推奨スタイル違反（用語ゆれ候補、冗長表現）
3. 例外承認対象
   - 緊急修正・外部要因で必須ゲートを一時的に満たせない変更
   - 期限付き例外として記録し、追補PRで解消する変更

### 2. 運用原則

- 必須ゲートは CI 上で自動実行し、失敗時は merge しない。
- 警告ゲートは可視化するが、初期段階では merge blocking にしない。
- 例外は「理由・期限・責任者・解消Issue」を必須記録項目とする。
- 例外を無期限化しないため、期限切れ例外は再承認または修正完了を必須とする。

### 3. 導入方針

- Phase 1: 既存 docs-check を必須ゲート基準へマッピングする。
- Phase 2: 欠落ゲート（metadata/link など）を段階追加する。
- Phase 3: 警告ゲートのしきい値を観測し、必要に応じて必須化判断を行う。

### 4. 非目標（このADRで扱わない範囲）

- 具体的なCI実装コマンドやワークフローYAMLの即時変更。
- 全文書の一括リライト。
- 可読性警告を初版から全面的に merge blocking へ昇格すること。

## Consequences

### 期待効果

- ドキュメント品質をレビュー属人性から分離し、最低品質を自動ゲートで維持できる。
- 必須と推奨を分離することで、導入初期の運用負荷を抑えつつ品質改善を継続できる。
- 例外承認の記録が標準化され、監査時の説明責任を確保しやすくなる。

### 副作用・制約

- 初期導入では、既存文書の不整合検出により一時的に修正負荷が増える。
- 必須ゲートの境界設計を誤ると、実務速度を不必要に低下させる可能性がある。
- 例外記録の運用が形骸化すると、品質改善サイクルが停止する。

### 移行時の対応

- docs-check 実装との差分棚卸しを行い、必須/警告の判定表を先に作成する。
- 期限付き例外テンプレートを整備し、記録形式を統一する。
- 運用開始後に月次で例外件数と再発傾向をレビューする。

## Traceability

- Derived-from: `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `01_Plans/adr/ADR-0018-coding-standards-and-smell-remediation.md`
- Related: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Related: `04_Documentation/operations.md`
- Related: `04_Documentation/security.md`
