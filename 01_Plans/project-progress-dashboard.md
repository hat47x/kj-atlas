# Project Progress Dashboard（DOC-OPS-03）

最終更新: 2026-03-08 (JST)

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
| 計画整備（DOC-OPS系） | 部分完了 | `DOC-OPS-02`/`DOC-OPS-03` は Done、`DOC-OPS-04` は Open。`REQ-DEF-01` は Done、`REQ-DEF-02/03` は Open。 |
| 認証運用（AUTH-OPS） | 完了 | `AUTH-OPS-03` は D1〜D4固定値と停止条件を 01/02/04 で同期し Done。 |
| 環境変数移行（ENV-ARCH） | 実装フェーズへ移行準備 | `ENV-ARCH-01` は Open、decision packで方針は人間判断済み。 |

## 2) Active issue 集約（Draft / Open / In Progress）

参照元: `01_Plans/issues/README.md` の Active issue memos。

| Backlog ID | Status | 要点 | メモ |
|---|---|---|---|
| DOC-OPS-04 | Open | 文書可視性・可読性ガバナンスの整備を進行。 | `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md` |
| REQ-DEF-02 | Open | 共通Requirement meta I/Fを前提に、RACI/契約境界を固定してOpen化。 | `01_Plans/issues/issue-REQ-DEF-02-responsibility-boundary-and-contract-checkpoints.md` |
| REQ-DEF-03 | Open | 共通Requirement meta I/Fを前提に、受入シナリオ/検証粒度を固定してOpen化。 | `01_Plans/issues/issue-REQ-DEF-03-acceptance-scenarios-and-issue-splitting.md` |

## 3) 人間判断待ち（Decision Queue）

| Priority | Backlog ID | 判断テーマ | 必要な決定 |
|---|---|---|---|
| P1 | REQ-DEF-02 | 責任分界点の固定粒度 | 役割RACIと契約変更判定欄の必須化範囲 |
| P1 | REQ-DEF-03 | 受入シナリオ規約の拘束力 | 要求粒度↔検証粒度マッピングを必須化するか |

補助資料: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`

## 4) 決定ログ（Recent Decisions）

| Date | Backlog ID | 決定内容 | 状態 |
|---|---|---|---|
| 2026-03-05 | ENV-ARCH-01 | Option B/C 採択（旧キー互換なし・監査痕跡追加なし）。 | 決定済み |
| 2026-03-06 | AUTH-OPS-03 | D1〜D4（承認順序/TTL、scope、代理承認、SLA）を固定。 | 決定済み |

## 5) 次の1手（実行チェックリスト / Proceed）

1. REQ-DEF-02/03 の未確定項目（テンプレ必須化範囲）を Decision Queue で決裁する。
2. DOC-OPS-04 の可視性改善を Active issue として継続し、dashboardへ反映する。
3. `issues/README.md` と decision-pack の状態表示を毎更新で同期する。
4. 不一致が出た場合は self-correction（最大3回）で修正し、未解消なら停止して判断待ちに戻す。

## 6) 再開コマンド（docs-check）

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
rg -n "DOC-OPS-03|Project Progress Dashboard|進捗サマリ|人間判断待ち" 01_Plans
```
