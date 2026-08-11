# Issue: DX-CODEGEN-03 コード生成パイプラインのテスト生成への拡張

- Type: Feature
- Status: Draft
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/generate_from_design_decision.py`, `02_Architecture/code-generation-from-design-decisions.html`
- Related ADR/Spec: `ADR-0067`, `AGENTS.md §1.3 L3基準①`, `DX-CODEGEN-01/02`
- Expected verification level: `unit`

## 課題

- 現在の問題: コード生成パイプラインは骨格・ロジック・検証・プロンプトまで実装（DX-CODEGEN-01/02）したが、「テスト生成」は未実装。L3自律（AGENTS.md §1.3）の「設計→実装→**テスト**→自律実行」のテスト部分が欠けている
- 利用者または開発への影響: L3自律の完全なループ（設計→実装→テスト）に達しない。生成されたコードの品質検証は人間に依存

## 対応方針

- 実施すること:
  1. `data_boundary`型で生成したPydanticモデルのテストを生成:
     - roundtripテスト（モデル→JSON→モデル）
     - 検証制約のテスト（min_length/max_length/pattern違反を拒否）
  2. `ai_task`型で生成したエンドポイントのテストを生成:
     - モックLLMでの成功ケース
     - provider disabled / エラーケース（既存test_ai_provider_error_contract.pyのパターン）
  3. 生成テストを `test_codegen_*.py` として出力し、既存テストスイートに組み込める形式にする
  4. `code-generation-from-design-decisions.html`にテスト生成パターンを追記
- 実施しないこと:
  1. 複雑なUIロジック（canvas描画・状態機械）のテスト自動生成
  2. 生成物の自動コミット（レビュー後に手動適用のproposal-only維持）
  3. 生成テストの完全自動実行（人間が適用判断）

## 三要素整合（ADR-0067）

| 次元 | このissueでの主張 | 他次元への制約 |
|------|-------------------|---------------|
| **業務設計** | L3自律の「設計→実装→テスト」のループを完結するには、生成コードに対応するテストの生成が必要。生成物の品質検証を人間だけに依存させない | 機能: 生成テストは既存テストパターン（test_ai_provider_error_contract.py等）に準拠し、モックLLMで実行可能。データ: 生成テストはproposal-onlyで人間が適用判断 |
| **データ設計** | data_boundary型はroundtrip・検証制約テスト、ai_task型はモックLLMでの成功/エラーケーステストを生成。既存のモックパターン（monkeypatchでgenerate_with_fallback差し替え）を再利用 | 業務: 複雑なUIロジックのテスト自動生成は対象外とし、人間の設計判断を残す。機能: 生成テストは`test_codegen_*.py`として既存スイートに組み込み可能 |
| **機能設計** | コード生成パイプラインにテスト生成機能を追加。生成物の構文検証（ast.parse）と同様に、生成テストも構文検証する | 業務: 生成物の自動コミットはしない。データ: テスト生成の成功率を`codegen_results.md`で追跡 |

## 受入条件

- [ ] `data_boundary`型で生成したモデルが、roundtripテストと検証制約テストを含むテストファイルを生成する（ドライラン）
- [ ] `ai_task`型で生成したエンドポイントが、モックLLMでの成功/エラーケーステストを生成する（ドライラン）
- [ ] 生成テストが構文検証（ast.parse）を通過する
- [ ] 既存のコード生成テスト（15 tests）がすべてパスする
- [ ] `code-generation-from-design-decisions.html`にテスト生成パターンが追記されている

## 補足

- 本issueはL3自律の「設計→実装→テスト」ループを完結させる
- 生成テストは既存のモックパターンを再利用し、実API不要で実行可能
- 生成物は常にレビュー後に手動適用（proposal-only原則）
