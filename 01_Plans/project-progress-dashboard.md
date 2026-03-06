# Project Progress Dashboard（DOC-OPS-03）

最終更新: 2026-03-06 (JST)

このダッシュボードは、`01_Plans/` 配下の進捗と意思決定待ちを1ファイルで確認するための運用入口。

## 1) 進捗サマリ（Phase / Backlog）

| 観点 | 状態 | 根拠 |
|---|---|---|
| 計画整備（DOC-OPS系） | 進行中 | `DOC-OPS-02` が Draft、`DOC-OPS-03` が Open。 |
| 認証運用（AUTH-OPS） | 判断待ちを含む進行中 | `AUTH-OPS-03` は Draft で人間判断待ち項目あり。 |
| 環境変数移行（ENV-ARCH） | 実装フェーズへ移行準備 | `ENV-ARCH-01` は Open、decision packで方針は人間判断済み。 |

## 2) Active issue 集約（Draft / Open / In Progress）

参照元: `01_Plans/issues/README.md` の Active issue memos。

| Backlog ID | Status | 要点 | メモ |
|---|---|---|---|
| AUTH-OPS-03 | Draft | strict mode例外緩和の承認運用境界が未確定。 | `01_Plans/issues/issue-AUTH-OPS-03-strict-mode-exception-relaxation-runbook-plan.md` |
| ENV-ARCH-01 | Open | `KJ_ATLAS_*` への移行方針に沿った実装追従が必要。 | `01_Plans/issues/issue-ENV-ARCH-01-global-env-prefix-migration.md` |
| DOC-OPS-02 | Draft | 文書横断改善計画の整理と優先度確定が必要。 | `01_Plans/issues/issue-DOC-OPS-02-cross-document-improvement-plan-from-human-decisions.md` |
| DOC-OPS-03 | Open | 本ダッシュボード整備と導線追加を実施中。 | `01_Plans/issues/issue-DOC-OPS-03-project-progress-dashboard-planning.md` |

## 3) 人間判断待ち（Decision Queue）

| Priority | Backlog ID | 判断テーマ | 必要な決定 |
|---|---|---|---|
| P0 | AUTH-OPS-03 | strict mode例外緩和 runbook の承認運用境界 | 承認順序/TTL、適用スコープ、代理承認、違反時SLA |
| P1 | DOC-OPS-02 | 文書横断改善の適用順序 | 先行適用文書と同期順序の最終決定 |

補助資料: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`

## 4) 決定ログ（Recent Decisions）

| Date | Backlog ID | 決定内容 | 状態 |
|---|---|---|---|
| 2026-03-05 | ENV-ARCH-01 | Option B/C 採択（旧キー互換なし・監査痕跡追加なし）。 | 決定済み |
| 2026-03-05 | AUTH-OPS-03 | 2者承認責務は確定、運用境界の最終決裁が未完了。 | 一部決定 |

## 5) 次の1手（実行チェックリスト）

1. `AUTH-OPS-03` の必須決定セット（D1〜D4）を人間レビューで確定。
2. 確定内容を `strict_mode_exception_approval_flow.md` と関連運用文書へ同期。
3. `ENV-ARCH-01` の実装追従（旧キー拒否・ドキュメント同期）を完了。
4. `DOC-OPS-02` の文書横断改善タスクを優先度順に再配列。

## 6) 再開コマンド（docs-check）

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
rg -n "DOC-OPS-03|Project Progress Dashboard|進捗サマリ|人間判断待ち" 01_Plans
```
