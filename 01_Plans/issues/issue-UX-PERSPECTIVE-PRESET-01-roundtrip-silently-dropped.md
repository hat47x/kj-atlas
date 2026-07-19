# Issue: UX-PERSPECTIVE-PRESET-01 perspectivePresetsがimport時に静かに失われる（未配線の可能性）

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/domain/view/perspective.ts`, `03_Implement/frontend/src/export/view_metadata.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `view_metadata.ts`の`buildExportViewMetadata`（237行目）は`viewState.perspectivePresets`を書き出し、`validateImportViewMetadata`（532-566行目）はこのfieldの形（`{id, name, perspective:{mode, strictFilter, ...}}`）を完全に検証してvalidationを通す。`view_metadata.test.ts`にはこの往復を検証する明示的なテストまで存在する。しかし、実際にimportした`ExportViewMetadata`をReact stateへ反映する唯一の箇所`App.tsx`の`applyImportedViewMetadata`（2979行目〜）は、`setViewPresets`・`setActivePresetId`・`setMergeAuditLog`・`setReviewEvents`等、他の全fieldに対応するsetterを呼ぶ一方、`perspectivePresets`に対応する`setPerspectivePresets`のような呼び出しは一切ない（`grep -n "perspectivePresets" App.tsx`は0件）。
- 加えて、このfield専用のCRUD API一式（`domain/view/perspective.ts`の`DEFAULT_PERSPECTIVE_PRESETS`・`mergeWithDefaultPerspectivePresets`・`replacePerspectivePreset`・`renamePerspectivePreset`・`removePerspectivePreset`・`resolveCurrentPerspectivePresetId`）が実装されているが、これらは自身のfileと自身のtestファイル以外のどこからも呼ばれていない（UIコンポーネントからの呼び出しが一切ない）。
- 利用者または開発への影響: 手作業で`perspectivePresets`を含む`view.json`をimportした場合、エラーも警告も出ずにvalidationを通過するが、`applyImportedViewMetadata`がこのfieldを読み捨てるため、値はメモリ上のReact stateへ反映されない。その後アプリから再度exportすると、このfieldは（一度も捕捉されていないため）出力に含まれない。エラーとしての拒否ではなく、静かなdata loss（load→resave）である。

## 対応方針

- 実施すること: この機能を実際にUIへ配線する（state管理・preset管理UI・restore/export呼び出しの追加）か、まだ使われていない先行スキーマ・CRUD実装として削除するかをMaintainerが判断する。
- 実施しないこと: 配線の実装、または削除の実行。どちらも製品機能の判断であり、コーディングエージェントが独断で決めるべきではない。

## 受入条件

- [ ] `perspectivePresets`機能について、実装を完成させる/削除するのいずれかの方針が決定される。
- [ ] 配線する場合、import→export往復でこのfieldが保持されることを確認する。
- [ ] 削除する場合、`view_metadata.ts`のexport/import両方とテスト、`perspective.ts`とそのテストを整合的に除去する。

## 検証計画

- 実行する確認: 方針決定後、`npx vitest run src/export/view_metadata.test.ts`（配線する場合は新規のround-tripテストも追加）。
- 期待結果: 方針に応じて、fieldが正しく保持されるか、または関連コードが完全に除去されている。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第6ラウンド）で発見。同じ棚卸しでDocumentV1本体（`bundle_export.ts`が書き出すCard/Island/Edge/EvidenceLink等）については、対応するimport/validation側（`domain/validate.ts`・`domain/validate_doc.ts`）にこの種の静かな欠落がないことも併せて確認済み。
