# Issue Draft: DOC-OPS-09 doc-ops-05-01 のDone判定と実体の乖離調査

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`, `04_Documentation/canonicalization.md`
- Related ADR/Spec: `01_Plans/issues/issue-DOC-OPS-08-stale-governance-meta-acs-in-done-issues.md`, `AGENTS.md` §4
- Expected verification level: `docs-check`

## 課題

`issue-doc-ops-05-01-04doc-canonicalization.md` は `Status: Done` でありながら、その受入条件が要求する実体が確認できない、という疑いで調査を起票した。

- 未チェックのAC（5件）: Classification固定（Move internal / Improve external）、Audience/Goal/Public boundaryの本文追跡、docs-check手順明示、独立レーン条件、docs-only条件。
- 対象文書 `04_Documentation/canonicalization.md` を検索したところ、`Move internal` / `Improve external` / `Audience` / `Public boundary` の語彙が **0件** だった（2026-08-07 grep）。

## 調査結果（2026-08-07）: Done判定は妥当

**5件の「未チェックAC」は実装ACではなく、Stream G 共通ACテンプレのテンプレ定義である。**

- `issue-doc-ops-05-01` の「## 5) 受入条件 / Acceptance criteria」（7件）は全て `[x]` で、分類結果（Move internal）・根拠（Audience/Goal/公開境界）・変更先候補・検証整合が明記されている。
- 冒頭の「## Stream G 共通ACテンプレ（合意・DOC-OPS-05）」（AC-1..5 / DoD-1..2、計7行）は、DOC-OPS-05 シリーズ全体で共有する**テンプレ定義**であり、本issue単体の完了チェックボックスではない。`- [ ]` 表記だが、これはテンプレ本文の一部であって本issueのACではない。
- よって「5件の未チェックAC」は実体の乖離を意味しない。

**「Move internal」推奨は、後続の実際の配置判断で「対外改善（公開候補）」へ上書きされている。**

- `canonicalization.md` は現在「一般利用者/QA向け公開候補」と明記され、`02_Architecture/api.md`、`schemas.md`、`functional-dependency-integrity-2026-08-06.html` から参照されている。
- 本issueの7 ACは「分類結果を記録する」ことが完了条件であり、実際の移設実行は本issueの非目標（「このIssue単体で対象文書の全文改稿や実装仕様変更は行わない」）に該当する。移設ではなく対外改善として残ったことは、別issueの判断で処理された（または現状の公開候補配置が決定）。

## 結論

- `issue-doc-ops-05-01` の Done 判定は妥当であり、Statusを戻す必要はない。
- 5件の `- [ ]` はテンプレ定義（Stream G 共通ACテンプレ）であり、本issueのACではない。実体乖離ではない。
- `canonicalization.md` が「Move internal推奨」でありながら公開候補のまま残っている点は、配置判断の一貫性の確認対象としてDOC-OPS-08の追跡に含める（本issueでは解決不要）。

## 受入条件

- [x] `issue-doc-ops-05-01` の5件のACそれぞれについて、充足または未充足が判明している。→ 5件はテンプレ定義であり本issueのACではない。実体の7 ACは全て `[x]`。
- [x] Doneを維持する場合は証跡への参照が本文に追記され、取り消す場合はStatusを戻す。→ Done維持。本issueの調査結果を `DOC-OPS-09` に記録。
- [x] `python 01_Plans/docs_check.py` が通る。→ pass（2026-08-07）。

## 検証計画

- `grep -rn "Move internal\|Improve external\|Audience" 04_Documentation/canonicalization.md`（0件を確認）
- `grep -n "## 5) 受入条件" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`（7件すべて `[x]` を確認）
- `python 01_Plans/docs_check.py`
