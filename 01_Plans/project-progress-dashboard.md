# Project Progress Dashboard（DOC-OPS-03）

最終更新: 2026-03-12 (JST, strategic-execution refresh)

> 運用ルール: 本ダッシュボードは ADR / issue memo の決定事項を統合表示する参照レイヤであり、直接更新を起点にしない。必ず先に ADR または issue memo の正本を更新し、その差分を統合反映する。

## 進捗サマリ

- ADRは `ADR-0000`〜`ADR-0026` がすべて `Accepted` で、未解決ADRは0件（方針ボトルネックなし）。
- issue memo総数は43件（Open=2 / Draft=16 / Done系=25）で、クリティカルパスは `HIL-RS-01-A1` 契約固定→A2/A3再開。
- Active issueは `HIL-RS-01` と `HIL-RS-01-A1`、Draft群は `FB-P2A/P2B/P2C` の3段分割Issue（A1→A2→A3）として待機。
- 依存構造は「契約先行（A1）→モック検証（A2）→実装（A3）」で、I/F先行により実装依存を切り離す方針。
- リソース競合は `issues/README.md` と本ファイルに集中するため、更新は統合フェーズ専用コミットに限定する。
- Decision Queue は未決3件（HIL 1件 + FB 1件 + 運用 1件）で、決定済み項目は再掲せず決定ログへ集約済み。

### Active issue / Decision Queue（相互整合）

| 区分 | ID | 状態 | 現在焦点 | 依存 |
|---|---|---|---|---|
| Active issue | HIL-RS-01 | Open | 次フェーズ実行管理と停止条件維持 | ADR-0026 |
| Active issue | HIL-RS-01-A1 | Open | 最小I/F契約の単一正本維持 | HIL-RS-01 |
| Decision Queue | DQ-HIL-EXEC-01 | Pending | A2/A3再開ゲート（契約リンク固定証跡） | HIL-RS-01-A1 |
| Decision Queue | DQ-FB-P2C-01 | Pending | polygon tie-break優先順位の最終確定 | FB-P2C-01-A1 |
| Decision Queue | DQ-OPS-SOURCE-01 | Pending | Source Issue `N/A→URL` 切替開始時点 | issues/README.md |

## 人間判断待ち（詳細）

### 1) DQ-HIL-EXEC-01（A2/A3再開ゲート）
- 背景: `HIL-RS-01-A1` で契約ID自体は固定済みだが、A2/A3着手許可条件の運用証跡フォーマットが未統一。
- 現在の詰まり: 判定条件 `contractLinkLocked=true` と `sharedResourceFreeze=true` の同時成立をどのログ項目で証明するか未確定。
- 放置リスク: A2/A3が別解釈で進行し、`02_Architecture` と `03_Implement` の再同期手戻りが発生。
- 判断に必要な入力: Plan Owner（担当）から証跡テンプレ案、Architecture Owner（確認）、期限=2026-03-14 JST。

### 2) DQ-FB-P2C-01（polygon tie-break規則）
- 背景: `FB-P2C-01-A1` で決定論要求は明記済みだが、padding競合時の優先順位が `Pending`。
- 現在の詰まり: I/F項目 `deterministicTieBreakOrder` の固定値（順序列）未確定。
- 放置リスク: A2モックとA3実装で演算順が乖離し、E2Eで非決定挙動が再発。
- 判断に必要な入力: Geometry担当（候補順序案）、QA（再現ケース）、期限=2026-03-15 JST。

### 3) DQ-OPS-SOURCE-01（Source Issue運用切替）
- 背景: 現運用は `Source Issue: N/A` 維持だが、Open/Draft増加で外部トレーサビリティ要求が増大。
- 現在の詰まり: 判定条件 `GitHub Issues正本運用開始宣言` の実施日とRACI割当が未確定。
- 放置リスク: 監査時にIssue追跡が分断され、決定根拠の探索コストが増加。
- 判断に必要な入力: PM/Triage（開始宣言案）、Platform Architecture Owner（承認）、期限=2026-03-18 JST。

## 対応案

### DQ-HIL-EXEC-01 対応案

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | 再開判定テンプレを `contractLinkLocked/sharedResourceFreeze/validatorPass` 3項目で固定 | A2/A3開始条件を機械判定化できる | 初回整備コストが増える | 01_Plans/02_Architecture/03_Implement | 高 |
| 案B | 現状の自由記述ログを維持し、レビュー時に都度判定 | 追加文書が不要 | 判定ぶれが残る | HIL運用全体 | 中 |
| 案C | A2/A3を先行再開し、問題発生時に停止 | 目先の速度は最速 | 手戻りと競合が最大化 | HIL + 実装層 | 低 |

- 推奨案Aの採用条件: 3項目テンプレの記入例2件が提出され、`HIL-RS-01` と `HIL-RS-01-A1` にリンクされること。
- 推奨案Aの見送り条件: 記入負荷が1件あたり15分超で、運用SLAを継続的に満たせないこと。

### DQ-FB-P2C-01 対応案

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | tie-breakを `padding遵守>自己交差回避>面積最小変動>頂点数最小` で固定 | A2/A3/テストの決定論が揃う | 近似最適解の自由度が下がる | FB-P2C-01 A1/A2/A3 | 高 |
| 案B | `自己交差回避` を最優先にして他は同順 | 幾何破綻耐性が高い | padding逸脱率が上がる | geometry + QA | 中 |
| 案C | 実装段でアルゴリズムに委譲（契約未固定） | 仕様文書の作成が最短 | 再現性欠落で監査不可 | FB-P2C-01全体 | 低 |

- 推奨案Aの採用条件: QA再現ケース3件で順序衝突が0件、既存fixtureとの差分理由を説明できること。
- 推奨案Aの見送り条件: 既存主要ケースでpadding違反が2件以上発生すること。

### DQ-OPS-SOURCE-01 対応案

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | 2026-03内に開始宣言を出し、Active memoから段階移行 | 追跡性と監査性が即時改善 | 移行作業が集中する | issues/README.md と Active memo | 高 |
| 案B | Open issueのみ先行URL化、DraftはN/A維持 | 変更量を抑制できる | 二重運用期間が長期化 | Open系運用 | 中 |
| 案C | N/A運用を継続し、四半期後に再評価 | 直近工数は最小 | トレーサビリティ不足が継続 | 全Issue運用 | 低 |

- 推奨案Aの採用条件: RACI（A/R/C/I）割当確定と `BacklogID→Issue URL` 対応表の準備完了。
- 推奨案Aの見送り条件: PM/TriageまたはA責任者が未確定で開始宣言を成立できないこと。

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

1. DQ-HIL-EXEC-01を先行解消し、A2/A3再開ゲート証跡テンプレを `HIL-RS-01` / `HIL-RS-01-A1` にリンク固定する。
2. DQ-FB-P2C-01を確定し、`FB-P2C-01-A1` の `DecisionStatus` を `Fixed` へ更新してA2へ引き渡す。
3. DQ-OPS-SOURCE-01の採否を決定し、採用時はREADME Runbook手順1〜6を開始、見送り時は期限再設定を記録する。

再開判定チェックリスト: 未固定箇所=0件 / 依存タスクの契約リンク確定 / 停止条件違反なし。
