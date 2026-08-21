# Issue: FB-RM-I18N-05 マージ適用・文書検証のドメインエラーがi18n対象外

- Type: Bug
- Status: Done
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

- [x] `merge_apply.ts`のドメインエラー/警告コード体系のi18nマッピング方針が決定される。
- [x] `document_import.ts`の検証エラー詳細（`formatValidationErrors`）の翻訳方針が決定される。

## 検証計画

- 実行する確認: 対応後、`npm run test`（frontend、i18n関連）および該当のマージ適用・取込検証テスト。
- 期待結果: 新しい翻訳キーが両ロケールで解決され、既存の`i18n/key_consistency.test.ts`等が通過する。

## 対応記録（2026-08-21）

**方針**: 各`error.code`は変更せず（既存の`[code] message`表示形式を維持し、コードはサポート/デバッグ用の
言語非依存識別子として残す）、`message`のみを`t()`経由の翻訳文へ置き換える。パラメータ（entity ID・
cardId・count・conflict reasonなど）は全て`t()`の補間パラメータとして扱う。`path`（JSON pointer風の
技術的文字列）は翻訳対象としない（識別子であり文章ではないため）。

**対象範囲を実装中に確定した**（issueの当初想定より正確化）:
- `merge_apply.ts`: M001〜M006・M101〜M105、計9メッセージ。
- `schema_validation.ts`: V001〜V005、計12メッセージ（`document_import.ts`が実際に呼ぶ`validateDocument()`
  からのみ到達可能な経路に限定。同ファイルの`validateView`/V101・V102は`document_import.ts`から
  到達不能なため対象外）。
- `domain/validate.ts`の`validateImportedDocument()`が返す9件の静的文字列（`mapUpgradeErrorToValidationError`
  経由でV001/V002へ束ねられる）。
- `document_import.ts`の`formatValidationErrors`のラッパー文言（見出し・"...and N more"相当）。
- `conflict_detect.ts`の`buildReason()`が返す3件のラベル（"both modified"等）を、M006の`{reason}`補間値として
  翻訳。**`buildReason()`自体は変更していない**——`conflict_detect.test.ts`が生の英語文字列を安定値として
  直接assertしているため、翻訳は消費側（`merge_apply.ts`）でのみ行う。

**実装中に発見した2つの実バグ**（機械的な置き換えでは踏まなかった）:
1. `Document cards must be an array of {id, text, x, y}.`という原文が、翻訳キーの値としてそのまま
   `{id, text, x, y}`という文字列を含んでいた。`isTemplateWellFormed()`は単一識別子の`{name}`のみを
   除去してから残存する`{`/`}`をチェックするため、この記法は**不正形式と判定され、翻訳が解決される代わりに
   生のキー文字列がそのまま利用者に表示されていた**。波括弧記法を使わない文章へ書き換えて解消した。
2. `mapUpgradeErrorToValidationError`が`error.toLowerCase().includes("transform"/"version"/"cards")`という
   部分文字列一致でpath/codeを振り分けていたが、これは異なる9つの静的メッセージのうち複数が同じ分岐へ
   落ちる（例: "cards"を含む2つの異なるメッセージが同じ分岐）ため、そのままでは1つの分岐に2つ以上の
   翻訳を対応させられなかった。9件の原文との**完全一致**テーブルへ置き換えて解消した（未知の原文が
   将来追加された場合は、翻訳せず元の英語文字列へ安全側で縮退する——クラッシュや空文字列にはしない）。

**テスト**: 新規`src/i18n/domain_error_keys.test.ts`（72件、ja/en双方で全キーが生のキー文字列へ
縮退しないことを直接確認）を追加。既存`merge_apply.test.ts`・`document_import.test.ts`の関連テストへ、
実際のコード経路が返す`message`が期待する翻訳済み日本語文字列と一致することを確認する assertion を追加した
（4件）。既存の`untranslated_key_inventory.test.ts`（全`t()`呼び出しのキーがja/en両方の辞書に存在することを
ソース全体から検証する既存の安全網）・`key_consistency.test.ts`も通過を確認した。

**検証**: `npm run typecheck`（0 errors）。対象範囲のvitest 166件 pass（新規72件含む）。
フルスイート実行（Node 20）: 1536 passed・1 failed / 240 files passed・2 files failed。
失敗2件は`issue-DX-CI-TEST-01`として既知・別追跡の環境依存ギャップ（`~/kjnative-fe`が
`04_Documentation`・`02_Architecture/design/...`という兄弟ディレクトリをミラーしていないため発生する
`ENOENT`/`repo root not found`）であり、本変更による退行ではないことを、失敗するテスト名・原因の完全一致で
確認した。

## 補足

- 発見経緯: 第12ラウンドの棚卸し（i18n hardcode観点）で発見。同じ観点で見つかった`document_import.ts`/`view_import.ts`の末端リテラル（`Invalid JSON in document.json`等、4件）と`App.tsx`の文章化ハンドラ2件は、既存の翻訳キー命名パターンをそのまま踏襲するだけの機械的な修正だったため、本ラウンドで直接対応済み。
