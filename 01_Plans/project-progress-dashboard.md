# Project Progress Dashboard（DOC-OPS-03）

最終更新: 2026-03-09 (JST, DOC-OPS-04整流化: ADR-0022ドラフト群Superseded同期)

このダッシュボードは、`01_Plans/` 配下の進捗と意思決定待ちを1ファイルで確認するための運用入口。

## 0) 運用プロトコル（DOC-OPS-03）

1. **Plan**: 変更対象と受入条件（AC）/完遂条件（DoD）を先に固定する。
2. **Execute**: 許可スコープ内の差分だけを実装し、非対象ファイルは変更しない。
3. **Verify**: `docs-check` を実行し、期待結果との差分を確認する。
4. **Proceed**: 問題なければ次のBacklogへ進む。問題があれば自己修正する。

- Self-Correction は **最大3回** とし、4回目が必要な場合は人間判断待ちへ切り替える。
- Active issue / Decision Queue / decision-pack の状態に矛盾を検知した場合は更新を停止し、競合として記録する。

## 1) 進捗サマリ（Phase / Backlog）

| 観点 | 状態 | 根拠 |
|---|---|---|
| 計画整備（DOC-OPS系） | 部分完了 | `DOC-OPS-02`/`DOC-OPS-03`/`DOC-OPS-04` は Done。`REQ-DEF-01/02/03` は Done。R2/R3 Decision Queueは解消済み。 |
| 認証運用（AUTH-OPS） | 完了 | `AUTH-OPS-03` は D1〜D4固定値と停止条件を 01/02/04 で同期し Done。 |
| 環境変数移行（ENV-ARCH） | 実装フェーズへ移行準備 | `ENV-ARCH-01` は Done、decision packでの方針採択を反映済み。 |

## 1.1) 全Issueサマリ（Active/Done）

- issue memo 総数: **23**
- Active: **0**
- Done: **23**（AUTH / FB-RM / DOC / REQ / ENV / QA 系を含む）
- 優先度上のクリティカルパス: **なし（DOC-OPS-04完了）**

根拠: `01_Plans/issues/README.md` の Active issue memos と Completed issue memos 集計。

## 2) Active issue 集約（Draft / Open / In Progress）

参照元: `01_Plans/issues/README.md` の Active issue memos。

| Backlog ID | Status | 要点 | メモ |
|---|---|---|---|

## 2.1) Phase Gate 状態（REQ-DEF-02/03）

- Gate判定: **Open (Phase 2/3 Proceed Enabled)**
- 分岐条件: DR-REQ-DEF-02 と DR-REQ-DEF-03 の Approval status が双方 `Approved` の場合のみ Phase 2 へ進行。
- 現在値: DR-REQ-DEF-02/03 ともに `Approved (mixed outcomes)`。Phase 2/3 の着手条件を充足。

## 2.2) DOC-OPS-04 Gate 状態（ADR-A依存）

- Gate判定: **Closed (A/B/C/D Accepted で完了同期済み)**
- 分岐条件: A=`ADR-0022-doc-ops-04-documentation-information-interface.md` が `Accepted`、かつ B/C/D=`ADR-0023/0024/0025` が `Accepted` であること（充足済み）。
- 完了条件:
  1. A（`ADR-0022-doc-ops-04-documentation-information-interface.md`）=`Accepted` を維持
  2. B/C/D（`ADR-0023/0024/0025`）がすべて `Accepted`
  3. 統合ファイル3点の状態同期と検証が完了
- 現在値: A（情報I/F ADR）と B/C/D（ADR-0023/0024/0025）は `Accepted`。旧 `ADR-0022-documentation-*` 3件は `Superseded` へ整流化済み。

## 2.3) ADR完了サマリ（DOC-OPS-04系）

完了（Accepted）のADRは以下3件。

1. `ADR-0023-doc-ops-04-readability-baseline.md`（ADR-B）
2. `ADR-0024-doc-ops-04-quality-gates-boundary.md`（ADR-C）
3. `ADR-0025-doc-ops-04-change-governance.md`（ADR-D）

依存関係:

- **Aは `Accepted` を維持する。AのI/F語彙に変更兆候が出た場合は B/C/D を即停止し、A再承認後に再開する。**
- B/C/D は編集境界を分離し、統合ファイル（README/dashboard/issue-DOC-OPS-04）は統合フェーズ以外で同時更新しない。

停止/再開条件（統合フェーズ固定）:

- 停止条件:
  1. A（`ADR-0022-doc-ops-04-documentation-information-interface.md`）のI/F語彙に追加・削除・改名の変更兆候が出た場合
  2. B/C/D作業中に統合ファイル3点（README/dashboard/issue-DOC-OPS-04）の同時更新が必要になった場合
- 再開条件:
  1. Aの再承認が完了していること
  2. 統合ファイル修正を統合フェーズ専用コミットで完了していること
  3. `validate_active_issue_memos.py` と unittest が成功していること

## 3) 人間判断待ち（Decision Queue）

| Priority | Backlog ID | 判断テーマ | 必要な決定 |
|---|---|---|---|
| P1 | REQ-DEF-02 | 責任分界点の固定粒度 | 決定済み（R2-P1 Reject / R2-P2 Conditional Approve / R2-P3 Conditional Approve） |
| P2 | REQ-DEF-03 | 受入シナリオ規約の拘束力 | 決定済み（R3-P1 Approve / R3-P2 Conditional Approve / R3-P3 Conditional Approve） |

補助資料: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`（DOC-OPS-04の判断履歴参照用。現行ゲート状態は本dashboardを正本とする）

## 4) 決定ログ（Recent Decisions）

| Date | Backlog ID | 決定内容 | 状態 |
|---|---|---|---|
| 2026-03-08 | REQ-DEF-03 | R3-P1 Approve、R3-P2/R3-P3 Conditional Approve。 | 決定済み |
| 2026-03-08 | REQ-DEF-02 | R2-P1 Reject、R2-P2/R2-P3 Conditional Approve。 | 決定済み |
| 2026-03-05 | ENV-ARCH-01 | Option B/C 採択（旧キー互換なし・監査痕跡追加なし）。 | 決定済み |
| 2026-03-06 | AUTH-OPS-03 | D1〜D4（承認順序/TTL、scope、代理承認、SLA）を固定。 | 決定済み |

## 5) 次の1手（実行チェックリスト / Proceed）

1. DOC-OPS-04 は A（情報I/F ADR）`Accepted`、B/C/D（`ADR-0023/0024/0025`）`Accepted`、旧 `ADR-0022-documentation-*` 3件 `Superseded` の整合を維持監視する。
2. 追加変更が発生した場合は、統合ファイル3点の同期を単一フェーズで実施する。
3. 不一致が出た場合は self-correction（最大3回）で修正し、未解消なら停止して判断待ちに戻す。

## 6) 再開コマンド（docs-check）

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
rg -n "DOC-OPS-03|Project Progress Dashboard|進捗サマリ|人間判断待ち" 01_Plans
```
