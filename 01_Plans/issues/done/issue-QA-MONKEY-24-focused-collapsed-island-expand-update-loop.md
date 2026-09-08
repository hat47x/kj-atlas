# Issue: QA-MONKEY-24 focus中の折りたたみ島を展開するとReact更新loop警告が発生する

- Type: Bug / Reliability
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`
- Related Backlog: `QA-MONKEY-24`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`（UQ-1）
- Expected verification level: `e2e`

## 課題

390px・seed 808のランダム操作で、島を折りたたみ、その島へ表示focusを設定した後に展開すると、Reactの`Maximum update depth exceeded`警告が発生した。最小再現では、focus用camera transformと文書側transformの同期中に、`onTransformChange`が文書更新ごとに新しいcallbackとなり、CanvasShellのeffectが新旧transformを交互に親へ書き戻すfeedback loopを確認した。共有カードを持つ複数島のfixtureでも再現する。

警告後も画面が即座にクラッシュするとは限らないが、CPU消費、操作遅延、将来の無限loop化につながる信頼性欠陥である。

## 対応方針

- `onTransformChange`が文書オブジェクトの参照変更だけでは再生成されないよう、最新文書をref経由で参照する。
- 島focus、折りたたみ・展開、camera transformの永続化内容そのものは変更しない。
- 最小再現プローブと発見seedの両方でconsole警告が消えることを確認する。

三要素牽制: 業務上は島の詳細確認・展開操作を停止させない。データ設計・保存境界は不変。機能上はCanvasShellと親のcamera同期callbackだけを安定化し、camera値、島focus、関係線、選択、永続化は変更しない。新しい製品判断ではないためADR不要。

## 受入条件

- [x] 折りたたみ島へfocusを設定して展開しても`Maximum update depth exceeded`が出ない。
- [x] 通常のpan・zoomで文書transformが引き続き更新される。
- [x] seed 808・390px・150操作で同警告が再発しない。
- [x] 島focus、折りたたみ、展開、SafeMode、保存データの契約を変えない。

## 検証計画

- `monkey_adversarial_probes.mjs` A13で最小再現を実画面確認する。
- seed 808・390pxを再実行する。
- frontend typecheck、対象unit test、docs-check、active issue validatorを実行する。

## 対応結果（2026-08-16）

- 最新文書をrefで参照し、`handleTransformChange`を文書参照の更新だけでは再生成しないcallbackへ変更した。これによりCanvasShellの同期effectが新旧camera transformを交互に書き戻す循環を止めた。
- A13の共有カードを持つ複数島fixtureで警告0件、seed 808・390pxの150操作と300 loopでfinding 0件を確認した。
- A14で通常のwheel zoom後にSaveが有効化されることを確認し、利用者操作によるtransform永続化は維持した。


## 配置の整理（2026-09-05）

- 本Issueは、モンキーテストで見つかった直接のUI／キーボード操作不具合を修正し、個別の回帰確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 2026-09-05の残存39件参照グラフ監査で、本Issueは他のlegacy Doneとの系列内ID参照を持たない孤立成分であり、旧rootパスの外部引用もないことを確認した。
- 既存のライフサイクル契約に従い、本変更ではこの条件を満たすQA-MONKEY完了Issue 5件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を39から34へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
