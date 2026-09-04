# issue-DOC-ISSUE-METADATA-01 — 必須メタデータの空値をvalidatorで拒否する

- Type: Process / Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Scope: `01_Plans/issues/validate_active_issue_memos.py`, `01_Plans/issues/tests/`
- Related ADR/Spec: `ADR-0000`, `DOC-ISSUE-LIFECYCLE-01`
- Expected verification level: `unit`

## 課題

必須メタデータ検証が一部の項目でラベル文字列の存在だけを確認しており、空値を拒否できない。また `extract_field_value()` の `\s*` が改行を含むため、空欄の次のメタデータ行を値として誤読し得る。

## 対応

- メタデータ抽出を行単位に限定し、空値を `None` として扱う。
- Active issue memoの全必須メタデータに非空値を要求する。
- verification levelはバッククォート有無に依存せず値を抽出し、許可集合を検査する。
- 空欄の行跨ぎ誤読と各必須項目の空値を回帰テストで固定する。

## 受入条件

- 空の必須メタデータがvalidatorを通過しない。
- 空欄が次行の値を取り込まない。
- `docs-check / unit / integration / e2e` 以外のverification levelを表記形式によらず拒否する。
- 既存のissue validatorテストと実リポジトリ検証が成功する。

## 検証結果

変更ブランチで `python -m unittest discover -s 01_Plans/issues/tests -p "test_*.py"` と `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行して確認する。
