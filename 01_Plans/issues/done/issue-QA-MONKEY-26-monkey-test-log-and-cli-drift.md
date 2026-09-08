# Issue: QA-MONKEY-26 モンキーテストの恒久記録と再現CLIが現行ハーネスから乖離している

- Type: Documentation / Quality
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-07-29.md`, `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-08-16.md`
- Related Backlog: `QA-MONKEY-26`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）
- Expected verification level: `docs-check`

## 課題

恒久的なモンキーテスト記録は2026-08-13で止まっており、その後のQA-MONKEY-20〜25、日英locale、320px、300〜400 loop、focus遷移比較、拡張trace、固定プローブA10〜A15が記録されていなかった。また7月29日の再現例は`SEED`/`ACTIONS`/`VIEWPORT`/`ONLY`を使っているが、現行スクリプトが読む名前は`KJ_ATLAS_MONKEY_*`であり、そのままでは指定値が反映されない。

## 対応方針

- 8月16日の環境、方法、seed、検出課題、修正後結果、自動検査結果を新しい実施記録へ固定する。
- 7月29日の再現コマンドを現行の環境変数名へ更新する。
- 歴史的な観測本文は書き換えず、現在再現可能な入口だけを補修する。

三要素牽制: 業務・データ・製品機能は変更しない。QA contributorが同じ条件を再現できる文書契約だけを修正するためADR不要。

## 受入条件

- [x] QA-MONKEY-20〜26の検出・対応状況が1つの実施記録で追跡できる。
- [x] seed、locale、viewport、loop数、finding数が記録される。
- [x] adversarial、axe、responsive検査の結果が記録される。
- [x] 記載した環境変数名が現行スクリプトと一致する。

## 対応結果（2026-08-16）

- `mvp_exit_monkey_test_log_2026-08-16.md`を追加した。
- 7月29日記録の再現コマンドを`KJ_ATLAS_MONKEY_SEED`等へ更新した。
- docs-checkとactive issue validatorで文書契約を確認する。


## 配置の整理（2026-09-05）

- 本Issue群は、2026-08-16のモンキーテストで見つかった誤検知・検出漏れ・キーボードfocus継続性・再現記録のdriftを、QAハーネスと既存UI挙動の境界を崩さず解消した完了系列として `Done` となっていた。
- `QA-MONKEY-20/22/28` は正常な操作遮断や操作前からのbody focusを欠陥扱いしない一方、Enter / Space / Delete / Backspaceを含む実際のfocus脱落は検出できるよう、観測契約を精密化した。
- `QA-MONKEY-23/25/27/29` は選択解除・本文編集の取消/確定・カード削除でDOM要素が消える場合にも、作業文脈へfocusを戻してキーボード操作を継続できる境界を固定した。
- `QA-MONKEY-26` は現行ハーネスに合う再現CLIと実施記録を固定し、観測結果の再現可能性を回復した。
- これらは新しい製品仕様の追加ではなく、既存のアクセシビリティ基準・QA判定・再現性を実装と検証へ反映した完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は8から0へ縮小する。R18 identity manifestは不変の歴史境界として維持し、今後 `Status: Done` のmemoがactive rootへ残ることを許容しない。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
