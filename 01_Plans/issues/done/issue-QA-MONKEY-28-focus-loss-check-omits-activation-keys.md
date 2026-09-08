# Issue: QA-MONKEY-28 モンキーハーネスのfocus脱落判定が操作キーを網羅していない

- Type: Test / Quality
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `QA-MONKEY-27`
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/scripts/monkey_ui_sweep.mjs`
- Related Backlog: `QA-MONKEY-28`
- Related ADR/Spec: `01_Plans/issues/done/issue-QA-MONKEY-22-focus-loss-check-does-not-compare-pre-action-state.md`
- Expected verification level: `e2e`

## 課題

seed 404のtraceにはtextarea上のEnter確定が含まれていたが、focus脱落判定はTab/Shift+Tab/Escapeだけを対象にしていたため、Enter確定でfocusがbodyへ落ちるQA-MONKEY-27をfindingとして報告できなかった。Spaceで操作対象が消えるUIに加え、Delete/Backspaceでfocus中の要素自体を削除するQA-MONKEY-29も同じ検出漏れを持つ。

## 対応方針

- 操作前が非body、操作後がbodyという既存の状態遷移条件を維持する。
- 判定対象キーへEnter、Space、Delete、Backspaceを追加する。
- DOM置換後の次frame、および非同期画面遷移の短い完了待ち後に確定判定する。
- pointer操作や操作前からbodyだった場合は従来どおりfocus脱落として扱わない。

三要素牽制: QA観測範囲だけの変更で、業務・データ・製品機能は変更しない。ADR不要。

## 受入条件

- [x] Enter/Space/Delete/Backspaceによる非bodyからbodyへの遷移を報告する。
- [x] 操作前からbodyの場合は報告しない。
- [x] Tab/Shift+Tab/Escapeの既存判定を維持する。
- [x] RAFまたは非同期読込中の一時的なbody focusを誤検知しない。
- [x] 修正後の複数seedで誤検知がない。

## 対応結果（2026-08-16）

- 監視キーを操作・削除キーへ広げ、次frameと最大1秒の非同期focus復帰を待ってから判定するようにした。
- seed 606（en/390）と8080（en/1440）は各500 loopでfinding 0。seed 505の候補はA18へ固定して製品側を修正した。

## 検証計画

- 新規seedを日英・狭幅/通常幅で各400 loop以上実行する。
- script構文、docs-check、active issue validatorを実行する。


## 配置の整理（2026-09-05）

- 本Issue群は、2026-08-16のモンキーテストで見つかった誤検知・検出漏れ・キーボードfocus継続性・再現記録のdriftを、QAハーネスと既存UI挙動の境界を崩さず解消した完了系列として `Done` となっていた。
- `QA-MONKEY-20/22/28` は正常な操作遮断や操作前からのbody focusを欠陥扱いしない一方、Enter / Space / Delete / Backspaceを含む実際のfocus脱落は検出できるよう、観測契約を精密化した。
- `QA-MONKEY-23/25/27/29` は選択解除・本文編集の取消/確定・カード削除でDOM要素が消える場合にも、作業文脈へfocusを戻してキーボード操作を継続できる境界を固定した。
- `QA-MONKEY-26` は現行ハーネスに合う再現CLIと実施記録を固定し、観測結果の再現可能性を回復した。
- これらは新しい製品仕様の追加ではなく、既存のアクセシビリティ基準・QA判定・再現性を実装と検証へ反映した完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は8から0へ縮小する。R18 identity manifestは不変の歴史境界として維持し、今後 `Status: Done` のmemoがactive rootへ残ることを許容しない。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
