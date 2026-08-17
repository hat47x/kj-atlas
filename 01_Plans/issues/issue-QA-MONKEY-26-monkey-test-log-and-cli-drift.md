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
