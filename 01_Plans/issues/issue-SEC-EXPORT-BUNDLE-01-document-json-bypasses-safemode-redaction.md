# Issue: SEC-EXPORT-BUNDLE-01 document.json内でSafeModeの秘匿保証が完全にバイパスされる

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/export/bundle_export.ts`, `03_Implement/frontend/src/export/bundle_export.test.ts`, `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/i18n/locales/{en,ja}.json`
- Related ADR/Spec: `AGENTS.md`（SafeMode既定ONは最優先の安全境界）, `02_Architecture/architecture.md`, `THREAT_MODEL.md`
- Expected verification level: `unit`

## 課題

- 現在の問題:
  - `buildExportBundle`/`buildExportBundleWithWorkers`（`03_Implement/frontend/src/export/bundle_export.ts:254,313`）は、バンドル内の `outline.md`・`diagnostics.md`・`evidence_trace_*.md`・`contradiction_trace_*.md`・`trace_analytics_*.md` にはすべて `safeMode` を引き渡してマスク処理（`SafeModePolicy`）を適用しているが、同じバンドルに常に含まれる `document.json`（`toJsonFile(`${root}/document.json`, doc)`）だけは `resolveShareDocument()` を経由するのみで、これは `includeSourceReferences` が無効な場合に `card.meta`（source参照）を削るだけであり、`card.text` / `island.summaryText` / `relationSummaries[].text` などSafeModeが本来マスク対象とする本文はいっさい加工されずそのまま出力される。
  - `SharePanel` のUIには `safe_mode.locked_contexts`（`en.json`/`ja.json` 行92: "Locked redaction contexts: Share / Review Pack (cannot be disabled)." / "固定マスク対象: 共有 / レビューパック（無効化できません）。"）という、共有コンテキストでは秘匿が強制され無効化できないと明言する文言が表示されるが、`document.json` に関しては実態としてこの保証が成立していない。ユーザーへの開示文言と実装が矛盾している。
  - 既存テスト `bundle_export.test.ts:387`「defaults to safe mode for exports when context.safeMode is omitted」は `docWithSecret`（card.text / island.summaryText に `"SECRET_TEXT_DO_NOT_LEAK"` を仕込む）を使い safeMode省略（既定true）でバンドルを構築するが、検証対象を `files.filter(file => file.mime === "text/markdown")` に限定しており（`bundle_export.test.ts:413-417`）、`mime: "application/json"` の `document.json` はこのリーク検証から除外されている。そのため現状のテストスイートはこのバイパスを検出できない。
- 利用者または開発への影響:
  - SafeMode ON（既定値）のまま「エクスポート」や「共有」操作を行っても、生成されたバンドルの `document.json` を開けば未レビューの島サマリーや、レビューパック/共有を意図していないカード本文がすべて平文で読めてしまう。
  - `SharePanel` の開示文言（共有/レビューパックのマスクは無効化不可）を信頼したユーザーが、実際には全文が漏洩したバンドルを配布してしまうリスクがある。これは `AGENTS.md` が最優先の安全境界と位置づけるSafeMode既定ONの実質的な無効化に相当する。

## 対応方針

- 実施すること（次のいずれか、または組み合わせを人間が判断して選択する）:
  - (a) `document.json` 自体をSafeModePolicyに沿ってフィールド単位でマスクする専用のシリアライズ経路を用意する（ただし `document.json` は再インポート/ラウンドトリップ用途を兼ねている可能性があり、マスクすると復元不能になる懸念がある。`zip_import.ts` 側の期待フォーマットとの整合を要確認）。
  - (b) SafeMode ON時は `document.json` をバンドルから除外する、または明示的なオプトイン操作を要求する。
  - (c) 上記のいずれも採用しない場合は、`safe_mode.locked_contexts` の文言を実態に合わせて修正し（例:「本文の生データを含む document.json は対象外」等の注記を追加）、UIにも明示する。
  - 採用した方針に対して、`bundle_export.test.ts:387` のテストを `document.json` を含む全ファイルに対するリーク検証に修正する（`mime` によるフィルタを外す、または `document.json` 専用の否定的アサーションを追加する）。
- 実施しないこと:
  - `document.json` の全体スキーマ変更や、SafeMode以外の既存の共有/レビューパックフローの再設計。

## 受入条件

- [ ] SafeMode ONで生成されたバンドルの `document.json` が、`SharePanel` の開示文言（共有/レビューパックのマスクは無効化不可）と矛盾しない内容になっている。
- [ ] `bundle_export.test.ts` に、`document.json`（またはバンドル内の全ファイル）を対象にしたリーク検証テストが追加され、意図した挙動（マスクされる／除外される／文言が実態を正しく説明する、のいずれか採用した方針）を担保する。
- [ ] 関連する安全・互換性を損なわない（特に既存の正規インポート/ラウンドトリップフローが壊れないことを確認する）。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認:
  - `npx vitest run src/export/bundle_export.test.ts`
  - 採用した方針に応じて `src/import/zip_import.test.ts` も実行し、ラウンドトリップ（インポート）に回帰がないことを確認する。
- 期待結果:
  - 新規/更新したテストがSafeMode ON時の `document.json` の扱い（マスク・除外・文言修正のいずれか）を正しく検証し、全テストが green になる。

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - リスク: `document.json` は既存のバックアップ/再インポート機能が読む可能性が高いフォーマットであるため、単純にマスクすると正規のオーナー自身の再読込を壊す恐れがある。方針決定には `zip_import.ts` / `public_pack_manifest.ts` 側の期待仕様の確認が必須。
  - ADR化が必要になる条件: `document.json` のSafeMode下での扱い（マスク付き別ファイル化、除外、生データのまま許容など）が既存の共有/エクスポート契約（schemas.md, THREAT_MODEL.md）に影響する場合は新規ADRでトレードオフを固定する。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
