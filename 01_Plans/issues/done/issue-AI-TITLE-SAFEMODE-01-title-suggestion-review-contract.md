# Issue: AI-TITLE-SAFEMODE-01 タイトル提案UIのレビュー境界がAPI契約と不整合

- Type: Bug / Security / UX
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のDeepSeek実ブラウザモンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/api/client.test.ts`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`
- Related Backlog: `AI-TITLE-SAFEMODE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0068-safemode-enforcement-at-api-boundary.md`, `THREAT_MODEL.md`
- Expected verification level: `e2e`

## 課題

タイトル提案UIはレビュー済みカードだけを抽出していたが、`POST /ai/suggest-document-title`へ`textReviewed=true`を送らず、backendのfail-closed境界で常に422となっていた。一方、島タイトルは`titleReviewed`で絞られていなかったため、証明だけを追加すると未レビューの島タイトルを外部LLMへ送る危険があった。

## 対応方針

- タイトル提案コンテキストを`titleReviewed=true`の島タイトルと`textReviewed=true`のカード本文に限定する。
- 限定後のpayloadだけを`textReviewed=true`としてAPI境界へ渡す。
- 未レビュー情報を含める緩和、SafeMode解除、自動採用は追加しない。

三要素牽制: 業務上は人間が確認した内容だけを外部AIへ渡して候補を得る。データ上は未レビュー島タイトルとカード本文をpayloadから除外し、レビュー済み証明を明示する。機能上は候補生成後も現在タイトルを変更せず、候補ボタンを人が選んだ場合だけ採用する。既存SafeMode方針の実装修正でありADR追加は不要。

## 受入条件

- [x] 未レビュー島タイトルとカード本文がタイトル提案payloadへ入らない。
- [x] レビュー済みだけのpayloadが`textReviewed=true`を伴う。
- [x] 実DeepSeek APIでタイトル候補が表示される。
- [x] 候補表示だけでは現在タイトルが変わらず、人の候補選択でのみ変わる。
- [x] View panelへDeepSeekの呼出数・token usageが反映される。

## 対応結果（2026-08-16）

- App側の島タイトル抽出を`titleReviewed=true`へ限定し、既存のレビュー済みカード抽出と揃えた。
- API clientが限定済みpayloadへ`textReviewed=true`を付与するよう修正した。
- client payloadとApp境界を近接testへ固定した。
- Windows Edge実操作でカードをレビュー済みにした後、DeepSeekタイトル候補の表示、採用前のタイトル不変、View panelの利用量表示を確認した。

## 検証計画

- frontend client・SafeMode境界・typecheckを実行する。
- 実DeepSeek backendへ接続したWindows Edgeで、レビュー操作→タイトル提案→候補表示→採用前不変→provider利用量表示を確認する。


## 配置の整理（2026-09-05）

- 本Issueは受入条件を満たし、fail-closedなAI利用境界を保ったまま実画面を含む確認まで完了して `Done` となっていた一方、R18以前からの経緯により、完了済みのまま作業中Issueと同じルートへ残るlegacy集合に含まれていた。
- 既存のライフサイクル契約は、このlegacy集合を恒久的に残すための例外ではない。完了済みIssueを `01_Plans/issues/done/` へ移すたびに `LEGACY_DONE_AT_ROOT_BASELINE` も同じ変更で下げる、単調減少のラチェットである。
- 本変更ではAI利用画面・レビュー境界に関する完了済みIssue 2件を正規配置へ移し、baselineを52から50へ縮小した。R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
