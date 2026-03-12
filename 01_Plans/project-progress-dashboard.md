# Project Progress Dashboard（DOC-OPS-03）

最終更新: 2026-03-12 (JST, 人間判断負荷最小化フォーマット)

> 運用ルール: 本ダッシュボードは ADR / issue memo の決定事項を統合表示する参照レイヤであり、直接更新を起点にしない。必ず先に ADR または issue memo の正本を更新し、その差分を統合反映する。

## 進捗サマリ

- Active issue は `HIL-RS-01` と `HIL-RS-01-A1` の2件で、次フェーズの契約固定がクリティカルパス。
- 件数スナップショット（Stream D統合）: issue memo 総数=27（Active=2 / Done=25）。
- Decision Queue（DQ-HIL-A1-01, DQ-HIL-A1-02）は解消済みで、両件とも案Aで確定した。
- 決定ログは「既決のみ」を掲載し、Decision Queue へ既決項目を再掲していない。
- 次の1手は確定したA1契約（案A）をA2/A3の実装・運用同期へ反映することに移行した。
- 停止条件: 未固定I/Fが1件以上、または契約リンク未確定の場合は Proceed しない（現時点: 未固定I/F 0件）。
- 依存順は **A1 → A2 → A3** を固定し、2026-03-11時点で Stream A/B/C 完了報告受領済みを前提に共有リソース同期を維持する。
- 2026-03-12 の再同期確認で、件数（27/2/25）・Decision Queue=0・依存順（A1→A2→A3）が維持されていることを再確認した。

### Active issue（同期対象）

| Backlog ID | Status | 現在の焦点 | 依存 |
|---|---|---|---|
| HIL-RS-01 | Open | HIL-RS全体計画の進行管理とA1完了判定 | ADR-0026 |
| HIL-RS-01-A1 | Open | 最小I/F契約（Critique入力/再提案差分/レビュー帰属）の固定 | HIL-RS-01 |

### Decision Queue（未決のみ）

- 現在の未決キュー: 0件（DQ-HIL-A1-01 / DQ-HIL-A1-02 は案Aで確定済み）

## 人間判断待ち（詳細）

- 現在は該当なし（未決キュー0件）。
- DQ-HIL-A1-01 は案Aで確定済み（`intent/evidenceRefs/riskClass` 必須 + schemaVersion `v1.0`）。
- DQ-HIL-A1-02 は案Aで確定済み（`reviewerId/reviewStage/approvedAt/overrideReason` 必須 + `overridePolicy=two-person`）。

## 対応案

### DQ-HIL-A1-01 対応案（Critique入力I/F）

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | `intent/evidenceRefs/riskClass` を必須化し schemaVersion を `v1.0` で凍結 | A2/A3の入力契約が即時一致し判定が単純化 | 必須項目増加で入力側の準備工数が増える | A1/A2/A3, docs-check, review log | 高 |
| 案B | `riskClass` を任意、残り2項目を必須化して `v0.9` 暫定運用 | 既存入力資産を流用しやすい | v1.0移行時に再検証が再発 | A1/A2中心、A3は追随更新 | 中 |
| 案C | 3項目すべて任意で先行し、A2実装後に必須化判定 | 初期着手が最短 | 手戻りと監査不整合が最大化 | A2/A3/監査ドキュメント全体 | 低 |

- 推奨案Aの採用条件: `missingFieldImpact` と `consumerCompatibility` が期限内提出され、欠落ケースが0件。
- 推奨案Aの見送り条件: 期限内に2入力のどちらかが未提出、または互換性欠陥が1件以上。

### DQ-HIL-A1-02 対応案（レビュー帰属I/F）

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | `reviewerId/reviewStage/approvedAt/overrideReason` を必須化し `overridePolicy=two-person` 固定 | 監査証跡の欠落を防ぎ責務分離を維持 | 記録項目増加で運用負荷が上がる | A1, security docs, approval flow | 高 |
| 案B | `overrideReason` を任意化し、`overridePolicy=single-owner` を条件付き許可 | 緊急時の運用速度が上がる | 責務分離が弱まり監査是正が増える | A1, 運用手順, 監査レビュー | 中 |
| 案C | 帰属情報をログ外部保存に切替え、I/Fは最小化 | 実装I/Fは単純 | 参照分断で追跡性が低下 | backend連携, docs, 監査運用 | 低 |

- 推奨案Aの採用条件: `auditRetentionWindow` と `operatorWorkflowImpact` が期限内提出され、SLA違反想定が0件。
- 推奨案Aの見送り条件: 運用負荷が閾値（1レビューあたり+15分）を超過、または責務分離を満たせない。

## 決定ログ

| Date (JST) | Decision ID | Backlog | 決定内容 | 状態 |
|---|---|---|---|---|
| 2026-03-11 | DR-HIL-A1-01 | HIL-RS-01-A1 | DQ-HIL-A1-01 は案Aを採用（`intent/evidenceRefs/riskClass` 必須 + schemaVersion `v1.0` 凍結） | 決定済み |
| 2026-03-11 | DR-HIL-A1-02 | HIL-RS-01-A1 | DQ-HIL-A1-02 は案Aを採用（`reviewerId/reviewStage/approvedAt/overrideReason` 必須 + `overridePolicy=two-person` 固定） | 決定済み |
| 2026-03-11 | DL-HIL-01 | HIL-RS-01 | 次フェーズ計画を Open で継続し、A1完了前のA2/A3本実装を停止 | 決定済み |
| 2026-03-11 | DL-HIL-02 | HIL-RS-01-A1 | A1で最小I/F契約を先行固定し、契約リンク確定後のみA2/A3を再開 | 決定済み |
| 2026-03-08 | DR-REQ-DEF-03 | REQ-DEF-03 | R3-P1 Approve / R3-P2 Conditional Approve / R3-P3 Conditional Approve | 決定済み |
| 2026-03-08 | DR-REQ-DEF-02 | REQ-DEF-02 | R2-P1 Reject / R2-P2 Conditional Approve / R2-P3 Conditional Approve | 決定済み |
| 2026-03-06 | D1-D4 | AUTH-OPS-03 | 承認順序/TTL/scope/代理承認/SLA の固定値を確定 | 決定済み |

## 次の1手

1. `HIL-RS-01-A1` および関連Architecture文書へ案A確定内容を同期し、A2/A3の参照契約をロックする。
2. A2/A3の着手時に「案A前提」の回帰観点（必須項目欠落・責務分離逸脱）を検証計画へ追加する。
3. docs-check を再実行し、Active issue / Decision Queue / 決定ログ / 次の1手の件数整合を確認する。

- [x] 再開判定: 未固定箇所=0件 / 依存タスクの契約リンク確定 / 停止条件違反なし

## docs-check

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
rg -n "HIL-RS-01|HIL-RS-01-A1|DQ-HIL-A1" 01_Plans/project-progress-dashboard.md 01_Plans/issues/README.md
```
