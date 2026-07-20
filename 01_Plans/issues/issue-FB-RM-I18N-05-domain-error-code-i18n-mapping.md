# Issue: FB-RM-I18N-05 マージ適用・文書検証のドメインエラーがi18n対象外

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/diff/merge_apply.ts`, `03_Implement/frontend/src/import/document_import.ts`
- Related ADR/Spec: `issue-FB-RM-I18N-04-dynamic-key-catalog-coverage-audit.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: 次の2箇所は、コード化されたドメインエラー/警告メッセージがハードコードされた英語文字列のまま`setStatusMessage`等に渡り、ロケールに関わらず英語のまま表示される。
  1. `diff/merge_apply.ts`（M001〜M105相当のコード付きメッセージ、`59`/`70`/`78`/`95`/`104`/`249`/`256`/`277`/`301`/`308`行など10箇所以上）。`App.tsx`側で`applyResult.errors.map((error) => \`[${error.code}] ${error.message}\`).join("\n")`として`setStatusMessage`に渡される。
  2. `import/document_import.ts`の`formatValidationErrors`（`Document validation failed:\n${details}${suffix}`）。スキーマ検証エラーの`error.code`/`error.path`/`error.message`をそのまま英語の技術的詳細として連結する。
- 利用者または開発への影響: 日本語ロケールで利用していても、マージ適用時の警告・エラーや文書取込検証エラーの詳細部分だけ英語のまま表示される。既存の`t()`呼び出しパターン（周辺の成功/失敗メッセージは全て`t()`経由）との一貫性が崩れている。

## 対応方針

- 実施すること: 各エラー/警告コード（`error.code`）を`t()`キーへマッピングする設計を決定する。パラメータ（entity ID、件数、conflict reasonなど）をどこまで翻訳キーの補間パラメータとして扱うか、コード自体をUIに表示し続けるかを含めて判断する。
- 実施しないこと: 個々のメッセージを機械的に`t()`で包むこと。10箇所以上にまたがるコード体系全体のi18n境界設計が必要で、一部だけ対応すると却って一貫性を欠く。

## 受入条件

- [ ] `merge_apply.ts`のドメインエラー/警告コード体系のi18nマッピング方針が決定される。
- [ ] `document_import.ts`の検証エラー詳細（`formatValidationErrors`）の翻訳方針が決定される。

## 検証計画

- 実行する確認: 対応後、`npm run test`（frontend、i18n関連）および該当のマージ適用・取込検証テスト。
- 期待結果: 新しい翻訳キーが両ロケールで解決され、既存の`i18n/key_consistency.test.ts`等が通過する。

## 補足

- 発見経緯: 第12ラウンドの棚卸し（i18n hardcode観点）で発見。同じ観点で見つかった`document_import.ts`/`view_import.ts`の末端リテラル（`Invalid JSON in document.json`等、4件）と`App.tsx`の文章化ハンドラ2件は、既存の翻訳キー命名パターンをそのまま踏襲するだけの機械的な修正だったため、本ラウンドで直接対応済み。
