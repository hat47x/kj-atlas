# Issue Draft: DOC-OPS-10 doc-ops-05-02..14 の礼式AC/DoD一括整理

- Type: Process
- Status: Done
- Source Issue: `01_Plans/issues/done/issue-DOC-OPS-08-stale-governance-meta-acs-in-done-issues.md`
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/issues/issue-doc-ops-05-02..14-*.md`
- Related ADR/Spec: `01_Plans/lean_operations_inventory.md`（P1）, `AGENTS.md` §4, `01_Plans/issues/done/issue-DOC-OPS-08-stale-governance-meta-acs-in-done-issues.md`, `01_Plans/issues/done/issue-DOC-OPS-09-doc-ops-05-01-done-status-without-evidence.md`
- Expected verification level: `docs-check`

## 課題

`issue-doc-ops-05-02..14`（11件）は DOC-OPS-05 Set1 の固定5フェーズprotocol（AGENTS.md §4で廃止）に由来する AC/DoD テンプレートを含む。`DOC-OPS-08` の追跡で同型と確認済み。ただしdoc-ops-05-01とは構造が異なり、一括機械変換できない。

## 構造の多様性（2026-08-07 調査）

| issue | 実AC（§5） | 礼式AC/DoD | 分類決定 |
|---|---|---|---|
| 05-02 | なし（礼式AC/DoDのみ） | AC1-4/DoD1-2（`- [ ]`） | Move internal（維持） |
| 05-03 | あり（§5が全て未チェック） | 冒頭テンプレ＋Open化準備5件 | Improve external |
| 05-04 | あり（§5が全て未チェック） | 同左 | Improve external |
| 05-05 | 別形式 | Stopper/ProceedDecision | Move internal |
| 05-06 | 別形式 | U1 等 | Improve external |
| 05-07 | 別形式 | AC-1/DoD-2 | Move internal |
| 05-08..10, 12 | あり（§5未チェック） | 冒頭テンプレ | Improve external |
| 05-13, 14 | なし（未チェック0件） | なし | Improve external（解決済み） |

## 判断が必要な点

- **05-03/04/08/09/10/12**: 実AC（§5、7件）が全て未チェック。しかしDone statusは「Open化準備メモの完了」（分類決定の記録）を意味しており、§5は実装ACではなくDOC-OPS-05共通の受入テンプレの可能性がある。**Done statusの意味合い**（実装完了 vs 計画メモ完了）を個別に判定する必要がある。
- **05-02/05/06/07**: 実AC（§5）が存在せず礼式AC/DoDのみ。分類決定は本文に記録済み。
- **05-13/14**: 未チェック0件で解決済み。作業不要。

## 対応方針（案）

- 各issueで「礼式AC/DoDブロック」を `- [ ]` のまま残すか、DOC-OPS-09と同じく「テンプレ定義」注記へ変換するかを、実ACの有無とDone statusの意味合いに応じて個別判断する。
- 実AC（§5）が存在するissueは、実ACが実装ACなのかテンプレなのかを判定してから対処する。機械的削除はしない。

## 受入条件

- [x] 11件それぞれで、礼式AC/DoDの扱い（撤去 or テンプレ注記 or 維持）が決定され、本文に反映される。→ 2026-08-07に全14件（05-01..14）の未チェック0件へ整理完了。§5テンプレACは証跡付き`[x]`、T1-T3は証跡付き`[x]`、RG/H/U/AC-R/DoD-R/Open化準備リストは注記へ変換。
- [x] 各issueの分類決定（Move internal / Improve external）は失われない。→ 全issueの Classification / 推奨アクション節を維持。
- [x] 05-13/14（解決済み）は変更しない。→ 元々未チェック0件、変更なし。
- [x] `python 01_Plans/docs_check.py` が通る。→ pass（active_memos=62, tracked_markdown=482）。

## 検証計画

- `python 01_Plans/docs_check.py`
- `git diff --check`
- `grep -c '\- \[ \]' 01_Plans/issues/issue-doc-ops-05-*.md`（各issueの残件数の記録）
