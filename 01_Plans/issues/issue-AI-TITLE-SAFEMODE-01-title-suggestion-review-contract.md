# Issue: AI-TITLE-SAFEMODE-01 タイトル提案UIのレビュー境界がAPI契約と不整合

- Type: Bug / Security / UX
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のDeepSeek実ブラウザモンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/api/client.test.ts`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`
- Related Backlog: `AI-TITLE-SAFEMODE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0068-ai-safe-mode-input-boundary.md`, `THREAT_MODEL.md`
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
