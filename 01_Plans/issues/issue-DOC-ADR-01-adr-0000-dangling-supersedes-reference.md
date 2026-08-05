# Issue: DOC-ADR-01 ADR-0000のSupersedes参照が存在しないファイルを指している

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Documentation
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/adr/ADR-0000-adr-governance.md`
- Related ADR/Spec: N/A
- Expected verification level: `docs-check`

## 課題

- 現在の問題: `01_Plans/adr/ADR-0000-adr-governance.md:110`に`- Supersedes: \`01_Plans/adr/ADR-0020-issue-context-lifecycle.md\``という記載があるが、そのファイルは`01_Plans/adr/`配下に存在しない（`ADR-0020`という番号自体は既存だが、実際のファイルは全く無関係な`ADR-0020-oidc-saml-mock-idp-sp-profile.md`）。`git log --all --follow`でこのパスの履歴を確認したが一度もコミットされたことが無く、リネームや削除の痕跡でもない。
- 利用者または開発への影響: `docs_check.py`の`check_relative_links`はMarkdownリンク形式のみを検証し、バッククォートで囲まれた地の文（プレーンテキストのパス参照）は検知しないため、この壊れた参照はCIで検出されずに残っている。実害は軽微（ADR-0000を読んだ人が存在しないファイルを探すことになる）。
- 判断結果: `git blame` と導入コミット `b0608593`（`docs(plans): fold issue lifecycle policy into ADR-0000`）を確認した結果、issue lifecycle policy は別ADRを経ずにADR-0000へ直接追加されていた。したがって、存在しないADRを置換したという記録ではなく、誤った追跡情報と判断した。

## 対応方針

- 実施したこと: 誤った`Supersedes`行を削除し、ADRの追跡欄から`01_Plans/adr/`配下を参照する場合は実在ファイルを要求する`DC-ADR-002`を追加した。既存の`DC-ADR-001`とともに統合入口`docs_check.py`へ接続した。
- 実施しないこと: 無関係な実在ADR-0020への付け替え、および置換済みで削除された旧計画文書を指す既存`Supersedes`記録の禁止。

## 受入条件

- [x] `Supersedes`行の扱い（削除）が決定される。
- [x] 対応後、`python3 01_Plans/docs_check.py`が通過することを確認する。

## 検証計画

- 実行する確認: 対応後、`python3 01_Plans/docs_check.py`。
- 期待結果: 既存の文書契約チェックに影響がないことを確認する。

## Validation

- `python -m unittest discover -s 01_Plans/tests -p "test_*.py"`
- `python 01_Plans/docs_check.py --root .`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## 補足

- 発見経緯: 第10ラウンドの棚卸し（ADR/issue相互参照観点）で発見。
