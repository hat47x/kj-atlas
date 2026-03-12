# Project Progress Dashboard（DOC-OPS-03）

最終更新: 2026-03-12 (JST, human decision load minimization)

## 進捗サマリ

- Active issue は `HIL-RS-01` / `HIL-RS-01-A1` の2件（いずれも Open, Source Issue=N/A）で `01_Plans/issues/README.md` と一致。
- Decision Queue は未解決3件（`DQ-HIL-EXEC-01` / `DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01`）のみを掲載し、決定済みIDは再掲しない。
- 決定済みは `DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03` / `D1-D4` を決定ログへ集約済み。
- 依存順は `HIL-RS-01-A1（契約固定） -> A2（モック検証） -> A3（本実装）` の固定順を維持。
- 件数監査は総数43件（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25）で前回値から差分なし。

## 人間判断待ち（詳細）

### DQ-HIL-EXEC-01（A2/A3再開ゲート）
- 背景: `HIL-RS-01-A1` で契約IDは固定済みだが、再開判定の証跡フォーマットが issue 間で不一致。
- 現在の詰まり: 判定I/F `contractLinkLocked` / `sharedResourceFreeze` / `validatorPass` の必須入力条件が未固定。
- 放置リスク: 期限超過により A2/A3 着手が遅延し、A1再確認の手戻りと共有リソース競合が増加。
- 判断に必要な入力: Platform Architecture Owner がテンプレ版を承認、Frontend/Backend Lead が記入例を提出、期限は 2026-03-14 JST。

### DQ-FB-P2C-01（polygon tie-break規則）
- 背景: `FB-P2C-01-A1` は決定論要求まで固定済みで、競合時優先順位のみ未確定。
- 現在の詰まり: I/F項目 `deterministicTieBreakOrder` の固定値（評価順序）と QA受入閾値が未承認。
- 放置リスク: 期限超過で fixture 差分が収束せず、A2/A3 の再現性低下と再試験工数増加が発生。
- 判断に必要な入力: Architecture Owner が優先順位を決裁、QA Lead が3ケース再現結果を提出、期限は 2026-03-15 JST。

### DQ-OPS-SOURCE-01（Source Issue URL移行開始）
- 背景: 現在は `Source Issue: N/A` 運用で、GitHub Issues 正本への移行開始日が未宣言。
- 現在の詰まり: 判定条件 `開始宣言日時` / `A,R責任者確定` / `BacklogID->IssueURL対応表` が未充足。
- 放置リスク: トレーサビリティ欠落が継続し、監査説明遅延と移行時の一括手戻りが拡大。
- 判断に必要な入力: PM/Triage が開始宣言案とURL対応表を提出、Platform Architecture Owner がRACI確定、期限は 2026-03-18 JST。

## 対応案

### DQ-HIL-EXEC-01

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | 再開判定テンプレを3項目固定（`contractLinkLocked/sharedResourceFreeze/validatorPass`）し、2件の記入例を添付 | 判定の機械化で停止判断を統一できる | 初回整備に追加作業が発生 | `HIL-RS-01` / `HIL-RS-01-A1` / A2/A3再開ゲート | 高 |
| 案B | 現行の自由記述を維持し、レビュー会で都度判定 | 導入作業が最小 | 判定ぶれで再開可否が人依存になる | HIL運用全体 | 中 |
| 案C | A2/A3を先行再開し、問題発生時のみ停止 | 初速が最短 | 競合時の手戻りと停止回数が増える | 02_Architecture + 03_Implement | 低 |

- 推奨案Aの採用条件: 2件の記入例で3項目が全て true、validator 実行結果を同一PRで提示する。
- 推奨案Aの見送り条件: 1件あたり追記作業が15分超を恒常化し、期限 2026-03-14 JST を満たせない。

### DQ-FB-P2C-01

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | 優先順位を `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小` で固定 | A2/A3/fixture判定を決定論で統一 | 近似最適の探索自由度が下がる | `FB-P2C-01-A1/A2/A3` とQA fixture | 高 |
| 案B | `自己交差回避` を最上位に変更し安全側へ寄せる | 幾何破綻の検出率を上げられる | padding逸脱が増加する可能性 | geometry + QA | 中 |
| 案C | 実装時に都度選択し契約固定しない | 文書更新量が最小 | 再現不能で監査不適合になる | FB-P2C全体 | 低 |

- 推奨案Aの採用条件: QA再現3ケースで衝突0件、既存fixture差分理由を `FB-P2C-01-A1` に記録する。
- 推奨案Aの見送り条件: 上記3ケースでpadding違反が2件以上になり、受入閾値を満たさない。

### DQ-OPS-SOURCE-01

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | 2026-03内に開始宣言を確定し、Active memo から順に `N/A -> URL` を置換 | 監査追跡性を即時改善できる | 移行期間に更新作業が集中 | `issues/README.md` + Active memo | 高 |
| 案B | Openのみ先行移行し DraftはN/A維持 | 初期変更量を抑制 | 二重運用期間が延びる | Open運用領域 | 中 |
| 案C | 現行N/Aを継続し次四半期で再評価 | 直近工数が最小 | 追跡欠落と監査負債が継続 | Issue運用全体 | 低 |

- 推奨案Aの採用条件: A/R責任者確定、`BacklogID->IssueURL` 対応表完成、開始宣言日時をREADMEへ反映。
- 推奨案Aの見送り条件: AまたはRが未確定で開始宣言を発行できず、期限 2026-03-18 JST を満たせない。

## 決定ログ

| Date (JST) | Decision ID | 対象 | 決定内容 | 状態 |
|---|---|---|---|---|
| 2026-03-11 | DR-HIL-A1-01 | HIL-RS-01-A1 | Critique I/F必須項目とschemaVersion固定（案A） | 決定済み |
| 2026-03-11 | DR-HIL-A1-02 | HIL-RS-01-A1 | Review attribution必須項目とtwo-person固定（案A） | 決定済み |
| 2026-03-11 | DL-HIL-01 | HIL-RS-01 | A1完了前のA2/A3本実装停止を維持 | 決定済み |
| 2026-03-08 | DR-REQ-DEF-03 | REQ-DEF-03 | R3-P1 Approve / R3-P2 Conditional / R3-P3 Conditional | 決定済み |
| 2026-03-08 | DR-REQ-DEF-02 | REQ-DEF-02 | R2-P1 Reject / R2-P2 Conditional / R2-P3 Conditional | 決定済み |
| 2026-03-06 | D1-D4 | AUTH-OPS-03 | 承認順序/TTL/scope/代理承認/SLA固定値を確定 | 決定済み |

## 次の1手

1. 2026-03-14 JST: `DQ-HIL-EXEC-01` を決裁し、再開判定テンプレと記入例2件を同一PRで固定する。
2. 2026-03-15 JST: `DQ-FB-P2C-01` を決裁し、`deterministicTieBreakOrder` を `Fixed` に更新する。
3. 2026-03-18 JST: `DQ-OPS-SOURCE-01` を決裁し、採用時は移行Runbook 1〜6を実行、見送り時は次期限と責任者を同時に再設定する。

再開判定チェックリスト: [ ] 未固定箇所=0件 [ ] 依存タスクの契約リンク確定 [ ] 停止条件違反なし
