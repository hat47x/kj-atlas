# Issue: DOC-ADR-01 ADR-0000のSupersedes参照が存在しないファイルを指している

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Documentation
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/adr/ADR-0000-adr-governance.md`
- Related ADR/Spec: N/A
- Expected verification level: `docs-check`

## 課題

- 現在の問題: `01_Plans/adr/ADR-0000-adr-governance.md:110`に`- Supersedes: \`01_Plans/adr/ADR-0020-issue-context-lifecycle.md\``という記載があるが、そのファイルは`01_Plans/adr/`配下に存在しない（`ADR-0020`という番号自体は既存だが、実際のファイルは全く無関係な`ADR-0020-oidc-saml-mock-idp-sp-profile.md`）。`git log --all --follow`でこのパスの履歴を確認したが一度もコミットされたことが無く、リネームや削除の痕跡でもない。
- 利用者または開発への影響: `docs_check.py`の`check_relative_links`はMarkdownリンク形式のみを検証し、バッククォートで囲まれた地の文（プレーンテキストのパス参照）は検知しないため、この壊れた参照はCIで検出されずに残っている。実害は軽微（ADR-0000を読んだ人が存在しないファイルを探すことになる）。
- 判断が必要な理由: これは既存の別ADR（ADR-0020）への単純なタイプミス・番号のずれではない。「issue context lifecycle」という内容のADRがそもそも起草されずに番号だけ予約されたのか、一度は存在したが別の形で統合・破棄されたのかが不明なため、この行を削除すべきか、参照先を別の形で復元すべきかはMaintainerの判断が必要。

## 対応方針

- 実施すること: この`Supersedes`行が指していた本来の決定内容を確認し、（a）その決定が別のADR/issueに統合済みなら本行を削除する、（b）まだ記録されていない決定なら適切な形で復元するかを決定する。
- 実施しないこと: 行の削除や参照先の書き換えそのもの。存在するが無関係なADR-0020に誤って repoint するのは明確な誤りになるため、機械的には対応しない。

## 受入条件

- [ ] `Supersedes`行の扱い（削除/復元）が決定される。
- [ ] 対応後、`python3 01_Plans/docs_check.py`が通過することを確認する。

## 検証計画

- 実行する確認: 対応後、`python3 01_Plans/docs_check.py`。
- 期待結果: 既存の文書契約チェックに影響がないことを確認する。

## 補足

- 発見経緯: 第10ラウンドの棚卸し（ADR/issue相互参照観点）で発見。
