# Issue: QA-MONKEY-22 モンキーハーネスのfocus脱落判定が操作前状態を比較しない

- Type: Test / Quality
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/scripts/monkey_ui_sweep.mjs`
- Related Backlog: `QA-MONKEY-22`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）, `issue-QA-MONKEY-20-monkey-harness-reports-normal-ui-blocking.md`
- Expected verification level: `e2e`

## 課題

390px seed 808と1440px seed 909の両方で、`Escape`後に`focus-lost-to-body`が1件ずつ報告された。しかし直前の操作はラバーバンド選択、またはtop layer下の操作skipであり、Escapeを押す前からfocusがbodyにある可能性が高い。

現行ハーネスは操作後snapshotだけを見て、`Escape`/`Tab`/`Shift+Tab`後にbodyなら無条件でfindingにする。操作前もbodyだった場合は「focusが脱落した」という状態遷移は起きておらず、製品欠陥と入力開始状態を区別できない。

## 対応方針

- 各ランダム操作の直前にactive elementを取得する。
- `focus-lost-to-body`は、操作前がbody以外で、操作後にbodyへ遷移した場合だけ報告する。
- 操作後のapp/SafeMode/ARIA/overflow/NaN等の不変条件は変更しない。

三要素牽制: QA結果の意味を「focus状態の遷移」へ正すだけで、業務操作、保存データ、製品機能は変更しない。ADR不要。

## 受入条件

- [x] 操作前からbody focusの場合はfocus脱落として報告しない。
- [x] 操作前が操作要素で、Tab/Escape後にbodyへ移った場合は引き続き報告する。
- [x] seed 808/390pxとseed 909/1440pxの再実行で誤検知が消える。
- [x] その他の不変条件検査を維持する。

## 検証計画

- 上記2 seedを各300反復で再実行する。
- script構文、docs-check、active issue validatorを実行する。

## 対応結果（2026-08-16）

- 各操作前のactive elementを記録し、非bodyからbodyへ遷移したTab/Shift+Tab/Escapeだけをfocus脱落として扱うよう修正した。
- traceへ操作前focusを含め、console error本文と直近traceを拡張して、誤検知の背後にあったQA-MONKEY-23/24を分離できるようにした。
- seed 808・390pxとseed 909・1440pxを各300 loopで再実行し、finding 0件を確認した。


## 配置の整理（2026-09-05）

- 本Issue群は、2026-08-16のモンキーテストで見つかった誤検知・検出漏れ・キーボードfocus継続性・再現記録のdriftを、QAハーネスと既存UI挙動の境界を崩さず解消した完了系列として `Done` となっていた。
- `QA-MONKEY-20/22/28` は正常な操作遮断や操作前からのbody focusを欠陥扱いしない一方、Enter / Space / Delete / Backspaceを含む実際のfocus脱落は検出できるよう、観測契約を精密化した。
- `QA-MONKEY-23/25/27/29` は選択解除・本文編集の取消/確定・カード削除でDOM要素が消える場合にも、作業文脈へfocusを戻してキーボード操作を継続できる境界を固定した。
- `QA-MONKEY-26` は現行ハーネスに合う再現CLIと実施記録を固定し、観測結果の再現可能性を回復した。
- これらは新しい製品仕様の追加ではなく、既存のアクセシビリティ基準・QA判定・再現性を実装と検証へ反映した完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は8から0へ縮小する。R18 identity manifestは不変の歴史境界として維持し、今後 `Status: Done` のmemoがactive rootへ残ることを許容しない。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
