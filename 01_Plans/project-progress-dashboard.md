# Project Progress Dashboard（DOC-OPS-03）

最終更新: 2026-03-11 (JST, Stream D 統合フェーズ最終同期を反映)

このダッシュボードは、`01_Plans/` 配下の進捗と意思決定待ちを1ファイルで確認するための運用入口。

## 0) 運用プロトコル（DOC-OPS-03）

1. **Plan**: 変更対象と受入条件（AC）/完遂条件（DoD）を先に固定する。
2. **Execute**: 許可スコープ内の差分だけを実装し、非対象ファイルは変更しない。
3. **Verify**: `docs-check` を実行し、期待結果との差分を確認する。
4. **Proceed**: 問題なければ次のBacklogへ進む。問題があれば自己修正する。

- Self-Correction は **最大3回** とし、4回目が必要な場合は人間判断待ちへ切り替える。
- Active issue / Decision Queue / decision-pack の状態に矛盾を検知した場合は更新を停止し、競合として記録する。

### 0.1) AC/DoDドラフト補完（Plan）

- AC最小セット: 変更対象、非対象、検証コマンド、停止条件を先に明記する。
- DoD最小セット: docs-check（validator/unittest）成功、統合ファイル整合、再開手順を記録する。
- 合意ログ: 未確定項目が残る場合は `Proceed` へ進まず、`Decision Queue` へ戻す。

### 0.2) DOC-OPS-02 同期チェック（用語・役割・導線・固定値）

- 用語: `正本 / 暫定メモ / 決裁入力 / 例外承認` を `ADR-0022` と一致させる。
- 役割: `Security Officer / System Owner / Platform Operator`（AUTH-OPS-03）と、`Platform Architecture Owner / Plan Owner / Architecture Owner`（DOC-OPS-04審査）を混同しない。
- 導線: `02_Architecture/strict_mode_exception_approval_flow.md` → `04_Documentation/operations.md` / `04_Documentation/security.md` → `01_Plans/*` の順で同期する。
- 固定値（D1〜D4）: `承認順序=Security Officer先行 + 承認TTL=4h / scope=tenant最大2h / 代理承認なし / 48hレビュー + 15m一次 + 60m二次` を変更しない。

## 1) 進捗サマリ（Phase / Backlog）

| 観点 | 状態 | 根拠 |
|---|---|---|
| 計画整備（DOC-OPS系） | 部分完了 | `DOC-OPS-02`/`DOC-OPS-03`/`DOC-OPS-04` は Done。`REQ-DEF-01/02/03` は Done。R2/R3 Decision Queueは解消済み。 |
| 認証運用（AUTH-OPS） | 完了 | `AUTH-OPS-03` は D1〜D4固定値と停止条件を 01/02/04 で同期し Done。 |
| 環境変数移行（ENV-ARCH） | 完了 | `ENV-ARCH-01` は phase exit評価で Close 判定済み。 |
| 次フェーズ計画（HIL-RS） | 実行中（A1） | `ADR-0026` は Accepted。`HIL-RS-01` と `HIL-RS-01-A1`（Open）を起点に、契約先行でA2/A3着手条件を固定する。 |

## 1.1) 全Issueサマリ（Active/Done）

- issue memo 総数: **27**
- Active: **2**（`HIL-RS-01`, `HIL-RS-01-A1`）
- Done: **25**（AUTH / FB-RM / DOC / REQ / ENV / QA / DX-CODEX 系を含む）
- 優先度上のクリティカルパス: **HIL-RS-01（次フェーズ起点）**

根拠: `01_Plans/issues/README.md` の Active issue memos と Completed issue memos 集計。

## 1.2) ADRステータス監査（Accepted以外）

- `ADR-0022-documentation-readability-baseline.md`: `Superseded`（後継: `ADR-0023`）
- `ADR-0022-documentation-quality-gates.md`: `Superseded`（後継: `ADR-0024`）
- `ADR-0022-documentation-change-governance.md`: `Superseded`（後継: `ADR-0025`）

判定: **未解決ADR（Accepted以外）は存在するが、いずれも `Superseded` のため実装待ちタスクは発生していない。**


## 1.3) 依存グラフ（ADR→Issue / Issue→Issue / 共有リソース）

- ADR-0022旧3件（Superseded）→ 後継 ADR-0023/0024/0025（Accepted）
- ADR-0023/0024/0025 → Active Issue 依存: なし（`HIL-RS-01` は次フェーズ計画起点であり DOC-OPS-04 系依存なし）
- Issue→Issue 依存: `HIL-RS-01-A1` は `HIL-RS-01` に従属。A2/A3 は A1契約固定後に契約参照で独立着手。
- 共有リソース: `01_Plans/issues/README.md`（Active index 正本）, `01_Plans/project-progress-dashboard.md`（進捗正本）

## 2) Active issue 集約（Draft / Open / In Progress）

参照元: `01_Plans/issues/README.md` の Active issue memos。

| Backlog ID | Status | 要点 | メモ |
|---|---|---|---|
| HIL-RS-01 | Open | 次フェーズ（Human-in-the-loop可逆統合）計画。ADR-0026 Accepted と連動し、A1/A2/A3の実行順を管理する。 | P1 / docs-check |
| HIL-RS-01-A1 | Open | Architecture最小I/F（Critique入力/再提案差分/レビュー帰属）を固定し、A2/A3並列可能条件を明文化する。 | P1 / docs-check |

## 2.0) 状態同期監査ログ（2026-03-11）

- 監査結果: `issues/README.md` と本dashboardで `HIL-RS-01` / `HIL-RS-01-A1` の Active 状態が一致していることを確認。
- 同期値: issue memo 総数=27 / Active=2 / Done=25。
- 依存順: **A1→A2→A3** を固定し、A1完了報告が揃うまで A2/A3 は着手しない。
- 競合回避: Stream A/B/C の完了報告受領後に Stream D が共有リソース（README/dashboard）を統合同期する。
- 受領状況: 2026-03-11 JST に Stream A/B/C 完了報告を確認済み。
- Stream D最終同期: Active/Done集計、Decision Queue、Next actions を再監査し、矛盾ゼロを確認。
- Stream D再検証（同日追補）: A/B/C完了報告受領済みを前提に、共有リソース2点の同期値（27/2/25、Decision Queue=0、A1→A2→A3）を再確認。
- 検証ログ: validator / unittest / `rg` 整合監査を再実行し、結果はすべて成功。

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

停止/再開条件（統合フェーズ固定 / ADR-0025 D3連動）:

- 停止条件:
  1. A不整合: A（`ADR-0022-doc-ops-04-documentation-information-interface.md`）のI/F語彙に追加・削除・改名の変更兆候が出た場合
  2. 統合ファイル更新必要: B/C/D作業中に統合ファイル3点（README/dashboard/issue-DOC-OPS-04）の同時更新が必要になった場合
  3. SoD違反: 承認者と実行者の兼務が検出された場合
  4. Self-Correction 3回超過: 修正ループで未解消のまま4回目が必要になった場合
- 再開条件:
  1. Aの再承認と Deciders 再確認が完了していること
  2. 統合ファイル修正を統合フェーズ専用コミット（または専用PR）で完了していること
  3. 役割分離の再検証ログを追記し、`validate_active_issue_memos.py` と unittest が成功していること

## 3) 人間判断待ち（Decision Queue）

| Priority | Backlog ID | 判断テーマ | 現在の詰まり | 必要な決定 | 期限目安 |
|---|---|---|---|---|---|
| P1 | HIL-RS-01-A1 | A2/A3着手前のI/F契約未固定箇所の有無確認 | **決定済み**（案A採用）。A1で最小I/F契約チェックリストを先行固定し、A2/A3は参照専用で着手する。 | A1 AC達成（未固定箇所0件）の実績確認と、A2/A3起票時の契約リンク固定確認。 | 2026-03-11 決定済み |

注記: `REQ-DEF-02/03` は決定ログで `決定済み` を維持し、Decision Queue（人間判断待ち）には再掲しない。

補助資料: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`（DOC-OPS-04の判断履歴参照用。現行ゲート状態は本dashboardを正本とする）

### 3.1) 人間判断待ち処理フロー（詳細）

人間判断待ちは「止まっている作業の可視化」ではなく、**誤実装を防ぐために停止条件を守る制御点**として運用する。

1. **Intake（起票）**
   - 起票時に `判断テーマ / 未確定点 / 影響範囲 / 期限目安` を1行で記録する。
   - A1のような契約先行タスクでは、未確定点を `I/F項目名` 単位で列挙し、曖昧語（例: 「必要に応じて」）を禁止する。
2. **Triage（分類）**
   - `仕様未確定` / `役割未確定` / `受入判定未確定` の3分類で詰まりを明示する。
   - 48h以内に判断が必要なものをP1として Queue 先頭へ固定する。
3. **Decision Session（判断会）**
   - 判断入力は「採用案・非採用案・理由・適用開始時刻」をセットで残す。
   - 結論が条件付きの場合は、条件を AC に直接追記して再解釈の余地をなくす。
4. **Apply（反映）**
   - 反映先は `issue memo` → `dashboard` → `decision-pack` の順で同期し、同日更新を原則とする。
   - 反映後は docs-check を実行し、Queue残件と決定ログの矛盾がないことを確認する。
5. **Release Gate（再開判定）**
   - 再開条件は「未固定箇所=0件」「依存タスクが参照する契約リンク確定」「停止条件違反なし」の3点セット。
   - 1つでも満たさない場合は再開せず、Decision Queue に戻す。

### 3.2) HIL-RS-01-A1 向けの対応案（実行可能な選択肢）

| 案 | 内容 | メリット | リスク / 注意点 | 推奨度 |
|---|---|---|---|---|
| 案A（推奨） | A1で `最小I/F契約チェックリスト` を先に確定し、A2/A3は参照専用で着手する。 | 契約ドリフトを最小化し、A2/A3の手戻りを抑えられる。 | A1のレビュー密度が一時的に上がる。 | ★★★ |
| 案B | A2/A3を限定スコープで先行し、未確定I/Fはstubで吸収する。 | 体感進捗は早い。 | 契約確定後の差し替えが増え、統合時の衝突確率が上がる。 | ★★☆ |
| 案C | 判断会までA2/A3を完全停止し、A1のみを短期集中で完了する。 | ガバナンス上は最も安全で、判定が明快。 | 並列性が落ち、総リードタイムが延びる。 | ★★☆ |

運用決定（2026-03-11）:

1. **案Aを正式採用**し、`HIL-RS-01-A1` は最小I/F契約チェックリストの先行固定を完了条件として進める。
2. A2/A3 は A1で固定した契約を参照専用で利用し、契約差分の独自解釈を禁止する。
3. A1完了までに SafeMode/公開境界の未確定点が再発した場合は、A2/A3を停止して Decision Queue に差し戻す。

## 4) 決定ログ（Recent Decisions）

| Date | Backlog ID | 決定内容 | 状態 |
|---|---|---|---|
| 2026-03-11 | HIL-RS-01 | 次フェーズBacklogをOpen化し、ADR-0026（Accepted）で目的/非目標/ゲートを確定。 | 決定済み |
| 2026-03-11 | HIL-RS-01-A1 | **対応案Aを採用**。A1で最小I/F契約チェックリストを先行固定し、A2/A3は契約参照専用で着手する運用を確定。 | 決定済み |
| 2026-03-08 | REQ-DEF-03 | R3-P1 Approve、R3-P2/R3-P3 Conditional Approve。 | 決定済み |
| 2026-03-08 | REQ-DEF-02 | R2-P1 Reject、R2-P2/R2-P3 Conditional Approve。 | 決定済み |
| 2026-03-05 | ENV-ARCH-01 | Option B/C 採択（旧キー互換なし・監査痕跡追加なし）。 | 決定済み |
| 2026-03-06 | AUTH-OPS-03 | D1〜D4（承認順序/TTL、scope、代理承認、SLA）を固定。 | 決定済み |

## 5) 次の1手（実行チェックリスト / Proceed）

1. `HIL-RS-01-A1`（案A採用）で契約未固定箇所を0件化し、A2/A3並列着手条件（契約参照・共有リソース分離）を運用固定する。
2. A2（Frontend）/A3（Documentation）をA1契約参照で起票し、共有リソース更新は統合フェーズへ集約する。
3. docs-check（validator/unittest + 同期確認）を各フェーズ完了時に再実行し、dashboardへ反映する。

### 5.0) Stream D 統合更新宣言（2026-03-11 JST）

- 更新対象: `01_Plans/issues/README.md`, `01_Plans/project-progress-dashboard.md` のみ。
- 同期内容: 件数（27/2/25）、Active一覧（`HIL-RS-01`, `HIL-RS-01-A1`）、Decision Queue（未解決0件）、次アクション（A1→A2→A3）を再監査。
- 判定: Active/Done件数、Status、依存順序、Decision Queue の不整合は **0件**。
- 反映条件: Stream A/B/C の完了報告受領後に Stream D が単一コミットで同期（受領確認済み）。

### 5.1) 直列クリティカルパス固定（監査→同期→検証）

再開時の最優先シーケンスは次の3段階を固定する。

1. **ADR整合監査**（`Superseded` / `Accepted` の整流維持）
2. **Issue index整合監査**（`01_Plans/issues/README.md` の Active/Done 集計）
3. **Dashboard整合監査**（本ファイルの反映）

競合停止条件（固定）:

- `01_Plans/issues/README.md` と `01_Plans/project-progress-dashboard.md` を同一時刻に別作業で編集しない。
- 共有リソース更新が重なった場合は、先行作業を停止して統合フェーズへ集約する。

### 5.2) 再開時の並列化ガード（契約先行 + モック吸収）

Active issue が再発生した場合のみ、次の条件を満たすタスクを並列化する。

- 並列条件:
  1. 依存関係が解消済み、または API/Schema 契約を先に固定済みである。
  2. 実装側は fixture / stub を使い、契約差分をモック層で吸収できる。
  3. Auth系（backend contract）と Frontend系（export/worker/ui）の編集境界が分離されている。
- 禁止条件:
  1. 同一リソース（`issues/README.md`, `project-progress-dashboard.md`）の同時編集。
  2. 契約未固定のまま本実装を先行させる変更。

実装順テンプレ（固定）:

1. 契約先行（APIシグネチャ / 型 / schema）
2. モック実装（fixture / stub）
3. 本実装へ差し替え
4. 統合フェーズで共有リソースを一括同期

## 6) 再開コマンド（docs-check）

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
rg -n "Active issue memos|Completed issue memos|Superseded|Accepted" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/adr
```
