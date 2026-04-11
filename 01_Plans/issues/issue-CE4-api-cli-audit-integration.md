# Issue Draft: CE4 API/CLI/監査統合

- Type: Feature request
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Backend/Ops Team
- Scope: `03_Implement/backend/`, `04_Documentation/operations.md`, `04_Documentation/local_llm_ops_guide.md`
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）
- RequirementID: `CE4-API-CLI-AUDIT`
- RequirementStatement: API/CLI/GUI同値性と監査ログ4点セットを運用導線へ統合する。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE3完了 / 操作=同一queryをAPI/CLI/GUI実行 / 期待結果=同一bundleHash / 除外=認可機能拡張
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: integration
- DecisionStatus: Fixed
- DecisionQueueRef: N/A

## 1) 実装対象（具体）

- API: query/bundle/proposal/apply の監査イベントを統一フォーマットで出力。
- CLI: `context-query`, `context-bundle`, `proposal-diff`, `apply --dry-run` を提供。
- Ops: 監査ログ保全手順（rotation, retention, redact）を文書化。

## 2) 受入条件 / Acceptance criteria

- [ ] API/CLI/GUI で同一Query時に同一bundleHashを返す。
- [x] 監査ログ4点セット欠損率0%（query/bundle/proposal/apply）。
- [ ] `--dry-run` で副作用0（DB永続化なし）を保証。
- [ ] 失敗時のreject reasonが分類コード付きで記録される。
- [ ] CIで同値性テストが自動実行される。

## 3) 実装タスク分解 / Task breakdown

- [x] T1: 監査ログイベントスキーマ定義（version付き）。
- [x] T2: API/CLI共通のquery実行ライブラリ化。
- [ ] T3: 同値性integration test（API vs CLI vs GUI fixture）追加。
- [x] T4: operations/local_llm_ops_guideへrunbook追記。

## 4) 検証計画 / Validation plan

- 実行コマンド:
  - `pytest -q 03_Implement/backend/tests -k "api_cli_gui_equivalence or audit_log"`
  - `python -m kj_atlas_api.cli context-query --input 03_Implement/backend/tests/fixtures/context_query.json --dry-run`
- 期待結果:
  - 同値性テスト成功、監査ログ欠損0、dry-run副作用0。

## 5) リスクとロールバック / Risks & rollback

- 失敗モード: CLI/API実装差で同値性が崩れる。
- ロールバック: 共通実行ライブラリに統合し、片系実装を廃止。
