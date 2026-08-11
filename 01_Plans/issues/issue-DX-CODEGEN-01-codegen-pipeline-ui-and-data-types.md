# Issue: DX-CODEGEN-01 コード生成パイプラインのui_component型・data_boundary型への拡張

- Type: Feature
- Status: Draft
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/generate_from_design_decision.py`, `02_Architecture/code-generation-from-design-decisions.html`
- Related ADR/Spec: `ADR-0067`, `AGENTS.md §1.3 L3基準①`, `02_Architecture/code-generation-from-design-decisions.html`
- Expected verification level: `unit`

## 課題

- 現在の問題: コード生成パイプライン（`generate_from_design_decision.py`）は `ai_task` 型のみ対応。L3自律性（設計→実装→テストの自律実行）の中核である「画面型」「データ境界型」の設計判断からコードを生成できない
- 利用者または開発への影響: L3自律の前提「コード生成成功率80%以上」を測定できない。UI変更・データ契約変更は依然として手動実装に依存する

## 対応方針

- 実施すること:
  1. `ui_component` 型を追加: Reactコンポーネント + i18nキー + App.tsx統合のテンプレート生成
     - 入力: コンポーネント名、props型、必要i18nキー、data-testid、三要素検証
     - 出力: `ui/{ComponentName}.tsx` + ja/en i18n + テストファイル
  2. `data_boundary` 型を追加: Pydanticモデル + schemas.md + api.mdのテンプレート生成
     - 入力: 型名、フィールド定義、保存範囲、三要素検証
     - 出力: models.py/models_ai.pyの型 + schemas.md/api.mdの追記
  3. 各型の生成前に三要素整合チェックを必須化（既存のai_task型と同様）
  4. `code-generation-from-design-decisions.html` にui_component/data_boundaryの生成パターンを追記
- 実施しないこと:
  1. 実コードベースへの自動書き込み（生成物はレビュー後に手動適用）
  2. 複雑なUIロジック（状態機械・canvas描画）の完全自動生成
  3. L3昇格判定の自動実行

## 三要素整合（ADR-0067）

| 次元 | このissueでの主張 | 他次元への制約 |
|------|-------------------|---------------|
| **業務設計** | L3自律（AIが設計→実装→テストを自律実行）には、設計判断からコードを生成するパイプラインが画面型・データ境界型までカバーする必要がある。生成成功率を測定可能にする | 機能: 生成物はレビュー後に手動適用し自動書き込みしない。データ: 生成は三要素整合チェックを通過した設計判断のみ |
| **データ設計** | ui_component型はコンポーネント名・props・i18nキー・data-testidを、data_boundary型は型名・フィールド・保存範囲を入力とし、既存パターン（DocumentTitleEditor等）のテンプレートから生成する | 業務: 生成物が既存のUI/契約パターンと乖離しないよう、既存実装を雛形とする。機能: 複雑なcanvas描画・状態機械は自動生成対象外 |
| **機能設計** | `generate_from_design_decision.py` に `ui_component` / `data_boundary` 型のジェネレータを追加。入力JSONスキーマを型別に定義し、三要素検証を通過した場合のみ生成 | 業務: 生成パターンを`code-generation-from-design-decisions.html`に文書化。データ: 既存のai_task型の挙動を変更しない |

## 受入条件

- [ ] `ui_component` 型でDocumentTitleEditor相当のコンポーネントを生成できる（ドライラン）
- [ ] `data_boundary` 型でSuggestDocumentTitle相当の型を生成できる（ドライラン）
- [ ] 三要素整合チェックを通過していない設計判断では生成を拒否する
- [ ] `code-generation-from-design-decisions.html` に新規型の生成パターンが追記されている
- [ ] 既存のai_task型テストがすべてパスする

## 補足

- 本issueはL3自律（AGENTS.md §1.3）の基盤であり、コード生成成功率の測定を可能にする
- 生成物はレビュー後に手動適用する（提案の自動適用はしないproposal-only原則）
