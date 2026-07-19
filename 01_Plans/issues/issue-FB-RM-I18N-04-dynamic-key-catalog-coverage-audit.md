# Issue: FB-RM-I18N-04 動的キー構築箇所の翻訳カタログ網羅性を確認

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/i18n/translate.ts`, および動的キーを構築している約13ファイル（下記）
- Related ADR/Spec: `issue-FB-RM-I18N-02-locale-json-fallback-order.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: `en.json`/`ja.json`のキー集合は完全に対称（1721キー、差分0）で、静的なリテラルキー呼び出し（`t("foo.bar")`）はすべて両ロケールに存在することを確認済み。しかし、テンプレートリテラルで実行時の値をキーパスに埋め込む動的呼び出し（例: `` t(`app.status.diagnostics.stage.${stage}`) ``）が最低13ファイルに29箇所以上存在し、これらは静的なキー集合比較では網羅的にチェックできない。該当箇所の例:
  - `App.tsx:306` `` t(`app.status.diagnostics.stage.${stage}`) ``
  - `App.tsx:3721` `` t(`app.status.import.review_pack_zip_error_${error.code.toLowerCase()}`) ``
  - `canvas/CardView.tsx:138` `` t(`side_panel.hold_state.${holdState}`) ``
  - `ui/SidePanel.tsx:1964/3079/3093` `` t(`side_panel.connect.${edgeType}`) ``
  - `ui/ContextQueryPreviewPanel.tsx:17` `` t(`context_query.preview.value.${category}.${value}`) ``（2段階の埋め込み）
  - 他: `AgentResponseImportPanel.tsx`, `AgentTaskExportPanel.tsx`, `BulkOperationsBar.tsx`, `DiagnosticsBundlePanel.tsx`, `InquiryJourneyPrototypePanel.tsx`, `RepresentativeVisualCuePrototypePanel.tsx`, `TenantSessionBootstrapGate.tsx`, `ViewControlsPanel.tsx`, `PatchWorkspacePanel.tsx`
  - `i18n/translate.ts:97`の`t(key: MessageKey | string, ...)`はプレーンな`string`も受け付け、`resolveTemplateFromCatalogs`（L74-89）はカタログに一致するテンプレートが無い場合、生のキー文字列をそのまま返す設計になっている。つまり、動的キーが指す先の翻訳エントリが片方のロケール（または両方）に存在しない場合、それを検知する仕組みが型システムにもテストにも無く、実行時に「未翻訳のキー文字列がそのままUIに表示される」形で顕在化する。
- 利用者または開発への影響: 現時点でこの網羅性チェックによって実際に欠落しているキーが見つかったわけではない（`side_panel.hold_state.*`は抜き取り確認済みで完備）。しかし、上記13ファイルの列挙型/runtime値の分岐すべてに対応するカタログエントリが両ロケールに揃っているかは体系的に確認されていない。

## 対応方針

- 実施すること: 上記13ファイルそれぞれについて、動的キーに埋め込まれ得るすべての値（enumの全メンバー、エラーコードの全パターンなど）を洗い出し、対応する`en.json`/`ja.json`エントリが存在することを確認する。欠落があれば追加する。
- 実施しないこと: 全13ファイルの網羅的な確認そのもの（対象範囲が広く、各ファイルのenum/runtime値のドメイン知識を要するため、機械的な一括対応ではなく個別確認が必要）。

## 受入条件

- [ ] 13ファイルすべてについて、動的キーの到達可能な全パターンがen/ja両方でカタログに存在することを確認する。
- [ ] 欠落が見つかった場合、追加後に`i18n/key_consistency.test.ts`が通過することを確認する。

## 検証計画

- 実行する確認: 対応後、`npm run test`（frontend、i18n関連テスト一式）。
- 期待結果: 動的キーの到達可能な全パターンが両ロケールで解決されることを確認する。

## 補足

- 発見経緯: 第9ラウンドの棚卸し（i18nキー存在観点）で発見。当初の探索エージェントは「動的キー構築は存在しない」と報告したが、検証エージェントが独立した再grepでこれを覆し、テンプレートリテラルによる動的キー構築が実際には多数存在することを確認した（探索エージェントの網羅性主張の誤りを検証フェーズで捕捉した事例）。
