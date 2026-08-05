# Issue Draft: DOC-OPS-07 issue memoのOwnerに架空のRACI役職が32件残存

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/issues/issue-*.md`
- Related ADR/Spec: `ADR-0039`
- Expected verification level: `docs-check`

## 課題

32件のissue memoが `Owner:` に、実体を伴わない組織役職を記載している。例: `Security Officer + System Owner + Platform Operator`、`Platform Architecture Owner + Security Officer`、`QA Lead`、`Product Owner + QA Owner`、`Frontend Team`、`Data Schema Lead（Backend/DB）`、`Auth Architecture Lead（Security/Identity）`、`TBD（A=Productization Program Owner / R=QA Lead）`。

`ADR-0039` のContextは、この正確なパターンを解消対象として名指ししている（「仮想多役割のRACI...実体は1名で、多くがTBDまたはCodex」）。`Owner` フィールドは正準の最小項目セットにも含まれない: `AGENTS.md` §6 は `Type / Status / Source Issue / Priority / Scope / Related ADR / Expected verification level / Acceptance / Validation` を最小項目として列挙し、`Owner` を含まない。`validate_active_issue_memos.py` の `REQUIRED_FIELDS`（29〜38行）も同様に `Owner` を含まず、このフィールドの値はどのツールからも読まれていない。

## 論点（人的判断が必要な理由）

`Lifecycle` フィールド撤去や `Authoring Checklist` 撤去（本セッションで既に実施）と異なり、この項目は**純粋な重複や無情報ではなく、意味内容を持つ**。`Owner: Security Officer + System Owner + Platform Operator` という記載は、そのissueが複数の観点からのレビューを要すると読者へ伝える情報でもある。単純に全件 `Maintainer` へ置換すると、この文脈情報が失われる。

選択肢:
(a) 全件を `Maintainer` へ一括置換する（ADR-0039の文言に最も忠実）。
(b) `Owner` フィールド自体を削除し、複数観点のレビューが必要な旨は本文（課題・論点セクション）へ必要に応じて記載する運用にする。
(c) 現状維持し、`Owner` は「誰が書いたかの記録」ではなく「どの観点からのレビューが望ましいかのメモ」として明示的に再定義する。

上記のどれを採るかは、今後 `Owner` フィールドに期待する情報の性質についての判断であり、機械的な重複除去とは性質が異なるため、起票のみとし実施は見送った。

## 影響

低リスク（表示上の記載の問題であり、実行時の挙動や検証には影響しない）。ただし架空の役職表記は、実際には一人で運営されている個人OSSプロジェクトの実態と乖離した印象を与える。

## Acceptance

- [ ] 上記(a)/(b)/(c)のいずれかを選択し、32件のissue memoへ一貫して適用する。
- [ ] `AGENTS.md` の運用ガイダンスが選択した方針と整合する。

## Validation

- `grep -c "^- Owner:" 01_Plans/issues/issue-*.md` で全件が新方針に従っていることを確認する。
- `python 01_Plans/issues/validate_active_issue_memos.py` が変更後も通過することを確認する。
