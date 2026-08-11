# Issue: AI-EVAL-01 DeepSeek実APIでのKJ操作品質検証

- Type: Feature
- Status: Draft
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/tests/`, 新規評価用fixture
- Related ADR/Spec: `ADR-0067`, `AGENTS.md §1.2`, `AGENTS.md §1.3 L2基準③`
- Expected verification level: `manual`

## 課題

- 現在の問題: DeepSeek API providerは実装・モックテスト済みだが、実際のDeepSeek APIを使用したKJ操作の出力品質が未検証。L2自律性（AIが三要素チェックを自律実行）の前提として、AIのKJ操作品質が実用レベルにあることの確認が必要
- 利用者または開発への影響: L2基準③が未達のままL2移行判定ができない。モックテストのみでは実APIの応答品質・レイテンシ・エラー耐性が不明

## 対応方針

- 実施すること:
  1. DeepSeek API keyを取得し `KJ_ATLAS_DEEPSEEK_API_KEY` に設定
  2. 評価用テスト文書（評価用fixture）を用意。島3〜5個・カード15〜30枚程度の中規模KJ法文書
  3. 以下の2操作で実API品質を評価:
     a. `refine_card_text`（カード化・低深度）: 10件のカード本文改善を実行し、名詞止め禁止・元意味保持・過剰言い換えなし の3軸で定性評価
     b. `suggest_island_summary`（表札作成・中深度）: 3〜5島の表札提案を実行し、表札検査（別の島に載せても成立しないか）・代弁性・名詞止め禁止 の3軸で定性評価
  4. 評価結果を `01_Plans/dogfood/ai_eval_results.md` に記録
  5. 合格基準: 両操作とも3軸中2軸以上で「実用可」判定
- 実施しないこと:
  1. 数値スコアリング（反スコアリング原則）
  2. 全10操作の一括評価（段階的に拡大）
  3. 自動評価パイプラインの構築（まずは人間評価）

## 予算申告

- 複雑性予算（ADR-0043 CB-1..4）: N/A（評価作業のみ、UI変更なし）
- 性能予算（ADR-0046 PB-1..5）: N/A
- 触れるUQ次元（ADR-0044）: N/A

## 受入条件

- [ ] DeepSeek APIで `refine_card_text` 10件の評価完了、3軸中2軸以上で合格
- [ ] DeepSeek APIで `suggest_island_summary` 3〜5件の評価完了、3軸中2軸以上で合格
- [ ] 評価結果が `01_Plans/dogfood/ai_eval_results.md` に記録されている
- [ ] L2基準③が達成と判定され、AGENTS.mdのL2進捗が更新される

## 補足

- 本issueはL2自律性到達の最後の未達基準（③）を解除するためのものである
- 評価用fixtureは `03_Implement/backend/tests/fixtures/` に配置
- DeepSeek API keyは環境変数で設定し、Gitにコミットしない
- 評価は定性3軸（合格/不合格/要改善）で行い、数値化しない
