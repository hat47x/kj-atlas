# Issue: FB-RM-I18N-06 `app.toolbar.import_doc_json_legacy`がproductionで未使用だがtestに直結している

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/i18n/locales/en.json`, `03_Implement/frontend/src/i18n/locales/ja.json`, `03_Implement/frontend/src/ui/i18n_equivalence.integration.test.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `app.toolbar.import_doc_json_legacy`（"Import doc JSON (legacy, confirm in Share)"）はproduction sourceのどこからも呼び出されていない。UIには`_short`版（`app.toolbar.import_doc_json_legacy_short`、`App.tsx:10649`）のみが表示されている。しかし`ui/i18n_equivalence.integration.test.ts:312,317`がこのキーを`t("app.toolbar.import_doc_json_legacy")`で直接呼び出し、ja/en文字列にそれぞれ「旧式」「Import doc JSON」が含まれることを検査している。
- 判断が必要な理由: 第16ラウンドの棚卸しで同時に発見した10件の孤立キー（本ラウンドでカタログから削除済み）とは異なり、このキーは削除するとテストが壊れる。ラベル短縮時にテストの更新が漏れた可能性が高いが、「テストのアサーションを`_short`版へ差し替えてキーを削除する」か「キーをtest専用の生存アーティファクトとして維持する」かは、テストの意図（productionコードの網羅を検査したいのか、カタログの文字列品質だけを検査したいのか）を把握しているMaintainerの判断が必要。
- 利用者または開発への影響: 実害は現状なし（未使用キーがカタログに残っているだけ）。放置すると将来的に孤立キー監査のたびに同じ判断保留が繰り返される。

## 対応方針

- 実施すること: `i18n_equivalence.integration.test.ts:308-322`付近のテスト意図を確認し、(a) アサーション対象を`app.toolbar.import_doc_json_legacy_short`に差し替えて`app.toolbar.import_doc_json_legacy`をカタログから削除する、または(b) このキーをtest専用の意図的な生存アーティファクトとして`TEMPLATE.md`外のコメント等で明示する、のいずれかをMaintainerが選択する。
- 実施しないこと: テストの意図を確認せずにキーとテストを機械的に削除・変更すること。

## 受入条件

- [ ] `app.toolbar.import_doc_json_legacy`の扱い（削除 or 維持）が決定される。
- [ ] 決定に応じて、カタログとテストの整合が取れている。

## 検証計画

- 実行する確認: 変更する場合、`vitest run src/ui/i18n_equivalence.integration.test.ts`および`vitest run src/i18n`。
- 期待結果: 決定した方針とカタログ・テストの内容が一致し、`key_consistency.test.ts`のen/ja key parityが崩れない。

## 補足

- 発見経緯: 第16ラウンドの孤立i18nキー監査で発見。同時に見つかった10件の完全孤立キー（productionにもtestにも参照なし）は本ラウンドで直接カタログから削除済み。このキーだけがtestに直結しているため判断保留とした。
