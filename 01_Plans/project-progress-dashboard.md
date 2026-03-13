# Project Progress Dashboard（DOC-OPS-03）

最終更新: 2026-03-13 (JST, Stream D final shared-resource sync)

> 運用ルール: 本ダッシュボードは ADR / issue memo の決定事項を統合表示する参照レイヤ。必ず ADR/issue memo の正本更新後に同期する。

## 進捗サマリ

- ADRは `ADR-0000`〜`ADR-0026` がすべて Accepted系で、未解決ADRは0件。クリティカルパスは `ADR-0026` 配下の `HIL-RS-01-A1 -> A2 -> A3`。
- issue memoは総数43件（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25）。運用上のActiveは `issues/README.md` と整合する `HIL-RS-01` / `HIL-RS-01-A1` の2件。
- 依存性は「契約先行(A1) -> モック検証(A2) -> 実装(A3)」で、I/Fのみ依存する作業はモックで並行化し、実装待ちを最小化する。
- 競合源は共有統合ファイル `01_Plans/issues/README.md` と本ファイル。両ファイルは統合フェーズ専用コミットでのみ更新する。
- Decision Queueは3件を再監査し、`DQ-HIL-EXEC-01` と `DQ-FB-P2C-01` は再開条件充足で実行準備完了、`DQ-OPS-SOURCE-01` のみ未決として管理する。

### 未完Issue全件（18件）とレーン割当

- **Stream A（契約/I-F固定）**: `HIL-RS-01`, `HIL-RS-01-A1`, `FB-P2C-01-A1`, `FB-P2B-01-A1`, `FB-P2B-02-A1`, `FB-P2A-01-A1`, `FB-P2A-02-A1`。
- **Stream B（Frontend A2/A3）**: `FB-P2B-01-A2/A3`, `FB-P2B-02-A2/A3`, `FB-P2C-01-A2/A3`, `FB-P2A-01-A2/A3`, `FB-P2A-02-A2/A3`。
- **Stream C（Backend/Auth/Schema）**: `FB-P0-2A2B2C-stream-c-planning-baseline`（Draft）を先頭に、A契約確定後のAPI/schema実装へ接続。
- **Stream D（統合ドキュメント）**: 共有更新は `project-progress-dashboard.md` / `issues/README.md` / `decision-pack` のみを単一コミットで同期。
- **競合回避ルール**: `*_a1_*` はA専有、`*_a2_*`/`*_a3_*` はB/C専有、共有統合ファイルはD専有。交差編集を禁止する。

### 1) 計画分析と実行戦略のサマリー（優先度・依存・競合）

- **優先度根拠**: P0かつ契約未固定のI/F（`HIL-RS-01-A1`, `FB-P2C-01-A1`）を最優先。次にA2モック検証、最後にA3実装へ進める。
- **依存切離し（モック活用）**: A2はAPI/型/schemaVersionの固定値だけを先に確定し、実装未完でもfixture+stubで検証を進行する。
- **競合分離方針**: レーンを「Architecture契約」「Frontend実装」「Auth/API/Schema」「Docs統合」に分割し、対象ファイルを完全非重複で固定する。
- **クリティカルパス**: Stream A（契約固定）を最上流、Stream B/CをI/F合意後に並列、Stream D（統合同期）を最終に固定する。
- **停止条件**: 契約リンク未固定、shared resource更新衝突、Self-Correction 3回超過のいずれかで即停止し人間判断へエスカレーション。

### 2) 並行実行レーン（編集対象を非重複化）

| Stream | 役割 | 対象リソース（編集許可） | 依存開始条件 |
|---|---|---|---|
| A（Critical Path） | I/F契約と判定条件の固定 | `01_Plans/issues/issue-HIL-RS-01*`, `issue-FB-P2C-01-a1*`, `02_Architecture/*interface*` | 即時開始 |
| B | Frontend P2A/P2B/P2C の A2/A3 実装 | `03_Implement/frontend/src/**`, `03_Implement/frontend/tests/**` | Aの契約リンク確定後 |
| C | Auth/API/Schema 実装と検証 | `03_Implement/backend/src/**`, `03_Implement/backend/tests/**`, `03_Implement/backend/alembic/**` | Aの契約リンク確定後 |
| D | 計画統合・進捗同期・運用記録 | `01_Plans/project-progress-dashboard.md`, `01_Plans/issues/README.md`, `01_Plans/issues/decision-pack-2026-03-human-judgement.md` | B/C完了報告後 |

## プロンプトA: ストリームA（クリティカルパス）用 統合プロンプト

```md
あなたは Stream A 専属エージェントです。担当領域は「I/F契約固定」のみです。

【独立性】
- 編集許可: `01_Plans/issues/issue-HIL-RS-01*`, `issue-FB-P2C-01-a1*`, `02_Architecture` の契約定義ファイル。
- 編集禁止: `03_Implement/**`, `01_Plans/project-progress-dashboard.md`, `01_Plans/issues/README.md`。
- 指定外ファイルの編集は即時停止して報告すること。

【Phase管理】
- Phase 1: 現状Read。対象ファイルを再読し、未確定I/F項目（項目名/判定条件）を列挙。
- Phase 2: ADR記述。該当Decisionが必要な場合は Context / Decision / Consequences を明文化し、承認待ち状態にする。
- Phase 3: 契約固定。`contractLinkLocked=true` と `sharedResourceFreeze=true` の証跡テンプレを確定。
- Phase 4: 受け渡し。A2/A3が参照する固定リンクと固定値一覧を発行し、変更凍結宣言を記録。

【実装ワークフロー強制】
- 各Phaseで Plan -> Execute -> Verify -> Proceed を厳守。
- PlanではAC/DoD不足があればドラフトを提案し、合意取得後にExecute。
- VerifyではAC/DoD基準で自己検証し、失敗時は最大3回までSelf-Correction。

【フェイルセーフ】
- Self-Correction 3回超過、前提崩壊、未定義競合検出時は推測実行を禁止し停止。
- 停止時は「失敗条件 / 影響I/F / 必要な人間判断」を3点セットで報告する。
```

## プロンプトB: ストリームB（Frontend A2/A3）用 統合プロンプト

```md
あなたは Stream B 専属エージェントです。担当は Frontend のモック検証(A2)と実装(A3)です。

【独立性】
- 編集許可: `03_Implement/frontend/src/**`, `03_Implement/frontend/tests/**`。
- 編集禁止: backend, alembic, `01_Plans/project-progress-dashboard.md`, `01_Plans/issues/README.md`。
- Stream A契約ID以外のI/F拡張は禁止。

【Phase管理】
- Phase 1: Read同期。契約リンクと対象ファイルを毎回読み直し、想定差分ゼロを確認。
- Phase 2: A2モック検証。契約シグネチャ固定のままfixture/stubで結合前検証を完了。
- Phase 3: A3実装。A2で固定した入出力のみ使用して実装。
- Phase 4: 回帰確認。既存Frontendテスト+変更対象テストを完走し、結果を記録。

【実装ワークフロー強制】
- 各Phaseで Plan -> Execute -> Verify -> Proceed。
- AC/DoD不足時はドラフト提示して合意後に進行。
- テスト/Lint失敗時は最大3回まで自律修正し、4回目は停止。

【フェイルセーフ】
- 契約不一致、shared resource編集要求、未定義依存が発生した時点で停止。
- 停止報告は「失敗再現手順 / 競合ファイル / 必要判断」を必須記載。
```

## プロンプトC: ストリームC（Backend/Auth/Schema）用 統合プロンプト

```md
あなたは Stream C 専属エージェントです。担当は Backend/Auth/Schema のA2/A3実行です。

【独立性】
- 編集許可: `03_Implement/backend/src/**`, `03_Implement/backend/tests/**`, `03_Implement/backend/alembic/**`。
- 編集禁止: frontend, `01_Plans/project-progress-dashboard.md`, `01_Plans/issues/README.md`。
- Stream Aで固定したI/F・schemaVersionの破壊変更は禁止。

【Phase管理】
- Phase 1: Read同期。契約リンク、マイグレーション前提、既存テーブル状態を再確認。
- Phase 2: A2モック検証。APIシグネチャとデータ型整合をモック/契約テストで先行固定。
- Phase 3: A3実装。実DB反映・API実装・回帰テストを直列実行。
- Phase 4: 受け渡し。運用に必要な変更点をDocs連携用に箇条書きで引き渡し。

【実装ワークフロー強制】
- Plan -> Execute -> Verify -> Proceed を全Phaseで厳守。
- AC/DoD不足時はドラフト提示して合意後に着手。
- テスト/Lint失敗時は最大3回までSelf-Correction、それ以上は停止。

【フェイルセーフ】
- マイグレーション競合、契約逸脱、前提データ欠落を検知したら即停止。
- 停止報告は「逸脱I/F項目名 / 影響範囲 / 人間判断期限案」を明記。
```

## プロンプトD: ストリームD（統合同期）用 統合プロンプト

```md
あなたは Stream D 専属エージェントです。担当は計画/運用ドキュメント同期のみです。

【独立性】
- 編集許可: `01_Plans/project-progress-dashboard.md`, `01_Plans/issues/README.md`, `01_Plans/issues/decision-pack-2026-03-human-judgement.md`。
- 編集禁止: `02_Architecture/**`, `03_Implement/**`。
- 実装コード変更は一切禁止。

【Phase管理】
- Phase 1: Read同期。A/B/C完了報告と各決定リンクの存在を確認。
- Phase 2: Active issue / Decision Queue / 決定ログ / 次の1手を相互整合で更新。
- Phase 3: 件数監査。Open/Draft/Done件数、Decision Queue残件、停止条件違反有無を再計算。
- Phase 4: 公開。再開判定チェックリストを1行で確定。

【実装ワークフロー強制】
- Plan -> Execute -> Verify -> Proceed を必須化。
- AC/DoD不足時はドラフト提案し、承認取得後のみ更新。
- 検証失敗は最大3回まで修正、超過時は停止。

【フェイルセーフ】
- 決定済み事項の重複再掲、未承認決定の確定扱い、未定義競合を検出した場合は停止。
- 停止報告は「不整合ID / 参照元 / 解消に必要な承認者」を記録する。
```

## 人間判断待ち（詳細）

### DQ-HIL-EXEC-01（A2/A3再開ゲート）
- 状態: **Ready（2026-03-13同期）**
- 背景: `HIL-RS-01-A1` で契約IDは固定済みだが、再開判定ログの証跡フォーマットが未統一。
- 同期結果: 判定条件 `contractLinkLocked` / `sharedResourceFreeze` / `validatorPass` を再確認し、A2/A3再開ゲートの前提充足を確認。
- 放置リスク: A2/A3が別フォーマットで進行し、契約リンク再確認に手戻りが発生。
- 判断に必要な入力: Plan Ownerがテンプレ案、Architecture Ownerが承認、期限=2026-03-14 JST。

### DQ-FB-P2C-01（polygon tie-break規則）
- 状態: **Ready（2026-03-13同期）**
- 背景: `FB-P2C-01-A1` は決定論要求まで固定済み、競合時優先順位だけ保留。
- 同期結果: I/F項目 `deterministicTieBreakOrder` は `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小` で参照先と一致。
- 放置リスク: A2モックとA3実装で順序不一致が起き、非決定挙動が再発。
- 判断に必要な入力: Geometry担当の順序案、QAの再現ケース3件、期限=2026-03-15 JST。

### DQ-OPS-SOURCE-01（Source Issue切替開始日）
- 状態: **Open（未決）**
- 背景: Active memoは `Source Issue: N/A` で統一、外部監査要求の増加でURL移行判断が必要。
- 現在の詰まり: 判定条件 `GitHub Issues正本運用開始宣言` の実施日とRACI割当が未確定。
- 放置リスク: トレーサビリティが分断し、監査時の根拠探索コストが増加。
- 判断に必要な入力: PM/Triage開始案、Platform Architecture Owner承認、期限=2026-03-18 JST。

## 対応案

### DQ-HIL-EXEC-01 対応案

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | `contractLinkLocked/sharedResourceFreeze/validatorPass` の3項目テンプレを必須化 | 再開判定を機械化できる | 初期整備に30〜60分必要 | HIL-RS-01全体 | 高 |
| 案B | 自由記述ログ継続 + レビュー都度判定 | 追加テンプレ不要 | 判定ゆらぎが継続 | HIL運用全体 | 中 |
| 案C | A2/A3を先行再開し、問題時停止 | 初速のみ最大 | 手戻りと衝突が増加 | 02/03レイヤ全体 | 低 |

- 推奨案Aの採用条件: 記入例2件を `HIL-RS-01` と `HIL-RS-01-A1` にリンクし、validatorPass=true を確認。
- 推奨案Aの見送り条件: 実測で1件あたり作業時間が15分を恒常的に超過し、SLAを満たせない。

### DQ-FB-P2C-01 対応案

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小` で固定 | A2/A3/テストの決定論を統一 | 近似最適解の自由度低下 | FB-P2C-01 A1/A2/A3 | 高 |
| 案B | `自己交差回避` を最優先へ変更 | 幾何破綻を抑制 | padding逸脱率が上がる可能性 | geometry + QA | 中 |
| 案C | 実装側裁量（契約未固定） | 文書更新が最短 | 再現不能で監査不適合 | FB-P2C系全体 | 低 |

- 推奨案Aの採用条件: QA再現ケース3件で衝突0件、既存fixture差分理由を文書化。
- 推奨案Aの見送り条件: 主要ケースでpadding違反が2件以上発生。

### DQ-OPS-SOURCE-01 対応案

| 案 | 実施内容 | メリット | リスク | 影響範囲 | 推奨度 |
|---|---|---|---|---|---|
| 案A（推奨） | 2026-03内に開始宣言し、Active memoを段階的にURL化 | 監査追跡性を即時改善 | 移行作業が集中 | issues/README + Active memo | 高 |
| 案B | OpenのみURL化、DraftはN/A維持 | 変更量を抑制 | 二重運用期間が長引く | Open運用領域 | 中 |
| 案C | N/A継続し四半期後再評価 | 直近工数最小 | 追跡不足リスク継続 | 全Issue運用 | 低 |

- 推奨案Aの採用条件: RACI確定 + `BacklogID->IssueURL` 対応表を事前準備。
- 推奨案Aの見送り条件: A責任者またはR責任者が未確定で開始宣言が成立しない。

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

1. `DQ-HIL-EXEC-01` は Ready として維持し、A2/A3再開時に同一テンプレ（`contractLinkLocked/sharedResourceFreeze/validatorPass`）の運用逸脱がないかを監査する。
2. `DQ-FB-P2C-01` は Ready として維持し、A2/A3で `deterministicTieBreakOrder` の固定順序逸脱が出た場合のみ再オープンする。
3. `DQ-OPS-SOURCE-01` を2026-03-18 JSTまでに採否決定し、採用時はRunbook手順1〜6、見送り時は期限再設定を記録する。

再開判定チェックリスト: 未固定箇所=0件 / 依存タスクの契約リンク確定 / Decision Queue未決は `DQ-OPS-SOURCE-01` のみ / 停止条件違反なし。

## Stream D 実行ログ（2026-03-13, Phase 1-4）

### Phase 1: Read同期（A/B/C完了報告 + 決定リンク確認）

- A完了報告の確認: `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` の Stream A Phase 1〜4 記録と、`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` の固定を確認。
- B/C完了報告の確認: 同issueの Stream C同期ログと、統合フェーズ移譲条件（共有リソース更新禁止→Stream D集約）を確認。
- 決定リンクの存在確認: `DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` と `DR-REQ-DEF-02` / `DR-REQ-DEF-03` が本ダッシュボードの決定ログに存在することを確認。

### Phase 2: 相互整合更新（Active / Decision Queue / 決定ログ / 次の1手）

- Active issue運用値を `issues/README.md` と再照合し、運用上のActiveは `HIL-RS-01` / `HIL-RS-01-A1` の2件で一致を維持。
- Decision Queueを再評価し、`DQ-HIL-EXEC-01` / `DQ-FB-P2C-01` は Ready、`DQ-OPS-SOURCE-01` のみOpenとして維持。決定済み項目の重複再掲がないことを確認。
- 決定ログは既存IDのみを維持し、未承認決定を「確定扱い」していないことを確認。
- 「次の1手」は未決1件（`DQ-OPS-SOURCE-01`）の期限管理と、Ready2件の逸脱監査に限定し、未定義競合を新規導入しない。

### Phase 3: 件数監査（再計算）

- issue memo総数: 43
- Open: 8 / Draft: 7 / Done系: 25（Done=24 + Done(SQLite fallback path)=1）
- In Progress: 1 / Blocked: 2
- Decision Queue残件: 1（Ready=2 / Open=1）
- 停止条件違反: 0（契約リンク未固定 / shared resource更新衝突 / Self-Correction 3回超過の検出なし）

### Phase 4: 公開（再開判定チェックリスト1行確定）

- **再開判定チェックリスト確定:** 未固定箇所=0件 / 依存タスクの契約リンク確定 / Decision Queue未解決は `DQ-OPS-SOURCE-01` の1件のみ / 停止条件違反なし。
- 2026-03-13再同期: validator/unittest/rg を再実行し、件数（43/8/1/2/7/25）・Decision Queue（Ready=2/Open=1）・依存順（A1→A2→A3）の一致を再確認。
