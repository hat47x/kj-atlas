# Issue: QA-MONKEY-32 タイトル編集とAI候補の採用境界がキーボード・説明面で不明確

- Type: Accessibility / UX / AI Governance
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のDeepSeek提案UI・390px実Edgeモンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/DocumentTitleEditor.tsx`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/document-title-editor.spec.ts`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`
- Related Backlog: `QA-MONKEY-32`
- Related ADR/Spec: `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`
- Expected verification level: `e2e`

## 課題

タイトル表示は`h1`へclick handlerを付けただけで、キーボードfocus・Enter/Space操作ができなかった。編集をEnter/Escapeで閉じる場合も入力欄の消滅後にfocusが本文へ脱落した。AI候補領域には名前、生成完了の読み上げ、proposal-only説明、候補ボタンの採用動作を示すaccessible name、候補を閉じる操作がなかった。候補を採用するとfocus中のbuttonが消え、同様にfocusが脱落した。

## 対応方針

- headingを保ったまま、編集操作をnative buttonとして提供する。
- AI候補領域へ名前、生成件数のlive status、採用前はタイトル不変という説明を表示する。
- 候補buttonを「この候補を採用」と明示し、全文をtooltipでも確認可能にする。
- キーボード編集の確定・取消と候補採用後はタイトル編集button、候補を閉じた後は再生成buttonへfocusを戻す。pointerによるblur時は移動先のfocusを奪わない。

三要素牽制: 業務上はAI候補と現在値を区別し、人が採用を決める。データ上は候補表示中にDocumentを変更せず、候補buttonの明示操作だけでtitleを更新する。機能上はnative keyboard操作とfocus復帰を追加し、AI権限・SafeMode・自動適用を変更しない。安全境界の変更ではないためADR追加は不要。

## 受入条件

- [x] タイトル編集へTabで到達し、Enterで編集を開始できる。
- [x] Enter確定・Escape取消後にタイトル編集へfocusが戻る。
- [x] 候補領域が名前と生成件数を読み上げる。
- [x] 採用前は現在タイトルが変わらない旨を日英で表示する。
- [x] 候補buttonのaccessible nameが採用動作と候補全文を示す。
- [x] 採用後はタイトル、閉じた後は提案buttonへfocusが戻る。
- [x] 390px幅で横overflowが発生しない。

## 対応結果（2026-08-16）

- タイトル編集をheading内のnative buttonへ変更した。
- 候補領域へregion label、polite live status、proposal-only説明、明示的な採用名、閉じる操作を追加した。
- 採用・閉じる後のfocus復帰を追加し、英語E2Eと日英390px実Edgeで固定した。

## 検証計画

- `document-title-editor.spec.ts`でkeyboard編集、候補表示、採用前不変、採用・閉じる後のfocusを確認する。
- 390pxのWindows Edgeでaccessible name、region、横overflowを確認する。
- frontend近接test、typecheck、i18n整合検査を実行する。


## 配置の整理（2026-09-05）

- 本Issueは、モンキーテストで見つかった直接のUI／キーボード操作不具合を修正し、個別の回帰確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 2026-09-05の残存39件参照グラフ監査で、本Issueは他のlegacy Doneとの系列内ID参照を持たない孤立成分であり、旧rootパスの外部引用もないことを確認した。
- 既存のライフサイクル契約に従い、本変更ではこの条件を満たすQA-MONKEY完了Issue 5件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を39から34へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
