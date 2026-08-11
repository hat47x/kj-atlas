# Issue: DX-CODEGEN-02 コード生成パイプラインのロジック生成への拡張

- Type: Feature
- Status: Draft
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/generate_from_design_decision.py`, `02_Architecture/code-generation-from-design-decisions.html`
- Related ADR/Spec: `ADR-0067`, `AGENTS.md §1.3 L3基準①`, `DX-CODEGEN-01`
- Expected verification level: `unit`

## 課題

- 現在の問題: コード生成パイプライン（DX-CODEGEN-01）は**骨格生成**（props型・PascalCase・data-testid・i18nキー）に留まり、JSXロジック・フィールド検証・翻訳は人間が実装する。L3自律（AGENTS.md §1.3）の「設計→実装→テストの自律実行」には、ロジック生成が必要
- 骨格生成成功率: 80%（4/5、`codegen_results.md`）。これは骨格の信頼性を示すが、完全なコード生成ではない
- 利用者または開発への影響: L3自律の核心（自動実装）が未達。生成物は常に人間の実装作業を要する

## 対応方針

- 実施すること:
  1. **共通UIパターンのロジックテンプレート**を追加:
     - リスト表示（`<ul>` + `map`）
     - フォーム入力（`<input>` + `onChange` + 保存）
     - ボタン操作（`onClick` + disabled状態）
     - Escape/Ctrl+Enterハンドリング（既存document_titleパターン）
  2. `ui_component`型の入力に `pattern` フィールドを追加し、パターンに応じたJSXロジックを生成
  3. 生成物に型定義の雛形（`FieldworkRequestV1`等）を添付可能にする
  4. ロジック生成の成功率を `codegen_results.md` で追跡（骨格成功率とは別計上）
- 実施しないこと:
  1. 複雑な状態機械・canvas描画・非同期フローの自動生成（骨格+ロジックの範囲を超える）
  2. 生成物の自動コミット（レビュー後に手動適用のproposal-onlyを維持）
  3. テスト生成の自動化（別issue）

## 三要素整合（ADR-0067）

| 次元 | このissueでの主張 | 他次元への制約 |
|------|-------------------|---------------|
| **業務設計** | L3自律の「設計→実装→テストの自律実行」には、骨格だけでなくJSXロジックの生成が必要。共通UIパターンのテンプレート化でロジック生成を開始する | 機能: 生成は既存パターン（document_title等）に準拠し、プロジェクトのUI規約を逸脱しない。データ: 生成物はproposal-onlyでレビュー後に手動適用 |
| **データ設計** | `ui_component`型の入力に`pattern`フィールドを追加し、リスト/フォーム/ボタン/Escapeの共通パターンからJSXロジックを生成。型定義の雛形も添付可能にする | 業務: 複雑な状態機械・canvas描画・非同期フローは自動生成対象外とし、人間の設計判断を残す。機能: ロジック生成の成功率を骨格成功率と別に追跡 |
| **機能設計** | 共通UIパターンのロジックテンプレート（リスト/フォーム/ボタン/Escape）をジェネレータに追加。`pattern`フィールドで選択し、既存実装パターンを雛形にする | 業務: テスト生成の自動化は別issue。データ: 骨格生成成功率（80%）を維持しつつロジック生成を段階的に追加 |

## 受入条件

- [ ] `ui_component`型で`pattern: "form"`を指定したコンポーネントが、input+onChange+保存ボタンのJSXロジックを含む骨格を生成する（ドライラン）
- [ ] `pattern: "list"`でリスト表示の`map`ロジックを生成する
- [ ] Escape/Ctrl+Enterハンドリングが既存document_titleパターンに準拠して生成される
- [ ] 既存の骨格生成テスト（10 tests）がすべてパスする
- [ ] `codegen_results.md`にロジック生成の成功率を骨格成功率と別に記録する

## 補足

- 本issueはL3自律の核心（自動実装）への第一歩
- 生成物は常にレビュー後に手動適用（proposal-only原則）
- 骨格生成成功率80%は維持しつつ、ロジック生成を段階的に追加する
