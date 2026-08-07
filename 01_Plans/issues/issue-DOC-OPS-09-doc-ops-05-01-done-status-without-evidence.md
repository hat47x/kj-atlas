# Issue Draft: DOC-OPS-09 doc-ops-05-01 のDone判定と実体の乖離調査

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`, `04_Documentation/canonicalization.md`
- Related ADR/Spec: `01_Plans/issues/issue-DOC-OPS-08-stale-governance-meta-acs-in-done-issues.md`, `AGENTS.md` §4
- Expected verification level: `docs-check`

## 課題

`issue-doc-ops-05-01-04doc-canonicalization.md` は `Status: Done` でありながら、その受入条件が要求する実体が確認できない。

- 未チェックのAC（5件）: Classification固定（Move internal / Improve external）、Audience/Goal/Public boundaryの本文追跡、docs-check手順明示、独立レーン条件、docs-only条件。
- 対象文書 `04_Documentation/canonicalization.md` を検索したところ、`Move internal` / `Improve external` / `Audience` / `Public boundary` の語彙が **0件** だった（2026-08-07 grep）。
- これはDOC-OPS-08で追跡中の「廃止済み礼式のmeta-AC」とは別の問題: 実装AC（分類・境界追跡）が要求されているにも関わらず、その成果物が見当たらない可能性がある。

`AGENTS.md` §4 の「固定5フェーズ不要」はプロセス礼式の話であり、**実装ACそのものの妥当性は別問題**である。本issueの対象AC（Classification / Audience / Public boundary を固定する）は、プロセス廃止とは独立に満たすべき内容を含む。

## 対応方針（案）

- (a) `canonicalization.md` に分類・境界追跡の実体がない場合: `issue-doc-ops-05-01` のStatusを `Done` から `In Progress` へ戻し、5件のACを実際に満たす（文書へ分類語彙を追記）か、明示的にスコープ外として記録する。
- (b) 実体が別ファイルにある場合: 該当箇所を特定し、ACの証跡として本文へ参照を追記してチェックオフする。

## 受入条件

- [ ] `issue-doc-ops-05-01` の5件のACそれぞれについて、充足（証跡あり）または未充足（スコープ外記録）が判明している。
- [ ] Doneを維持する場合は証跡への参照が本文に追記され、取り消す場合はStatusを戻す。
- [ ] `python 01_Plans/docs_check.py` が通る。

## 検証計画

- `grep -rn "Move internal\|Improve external\|Audience" 04_Documentation/canonicalization.md`
- `git diff --check`
