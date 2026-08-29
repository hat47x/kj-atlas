# Issue: FB-RM-I18N-04 動的翻訳キーのカタログ網羅性を固定する

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/i18n/dynamic_key_coverage.test.ts`
- Related ADR/Spec: `01_Plans/issues/done/issue-FB-RM-I18N-02-locale-json-fallback-order.md`
- Expected verification level: `unit`

## 課題

静的な `t("key")` は既存テストで検査される一方、13 source fileにあるテンプレートリテラル形式の動的呼出しはカタログ欠落を検出できなかった。欠落時は翻訳キー文字列がそのままUIへ表示される。

## 対応

- production sourceを走査し、動的な `t(`...${value}...`)` のテンプレートを収集するテストを追加した。
- 現在到達可能な23テンプレートの値domainを列挙した。複数変数を持つContext Queryも有効な組合せだけを明示した。
- すべての到達可能キーがja/en両カタログに存在することを検査した。現時点の欠落キーは0件だったため、locale JSONの変更はない。
- 新しい動的テンプレートをsourceへ追加した場合、domain宣言を追加するまでテストがfailする。

## Acceptance

- [x] 13 source fileすべての動的キーについて、到達可能な値を監査した。
- [x] 到達可能な全キーがja/en両方に存在することを確認した。
- [x] 将来の未監査な動的テンプレート追加とカタログ欠落を検出する回帰テストを追加した。

## Validation

- `vitest run src/i18n/dynamic_key_coverage.test.ts`: 2 passed
- `vitest run src/i18n`: 61 passed
- `vitest run`: 1,269 passed（220 files）
- `tsc --noEmit`: passed
- `eslint`単体実行は依存packageが存在せず未実施。repositoryの`lint` scriptは`typecheck`と同一であり、上記で実施済み。
