# Decision Pack (2026-03-05): 人間判断待ちの高優先項目

目的: Active issue memo（Draft/Open）で着手を止めている判断点を短時間で決定可能にする。

## 0. 対象と優先順位

1. **P0 / AUTH-OPS-03**: strict mode例外緩和 Runbook の承認運用境界（Q1〜Q10）
2. **P1 / ENV-ARCH-01**: `KJ_ATLAS_*` 移行実装の運用境界
3. **P1 / REQ-DEF-01〜03**: 要件定義フェーズ壁打ち結果の固定粒度（優先要求・責任分界・受入規約）

---

## 1. P0: AUTH-OPS-03（完了）

### 1-1. 決定結果（2026-03-06）

- D1〜D4 を確定: 承認順序/TTL=4h、scope=tenant/最大2h、代理承認なし、48hレビュー+15m/60mエスカレーション。
- `02_Architecture/strict_mode_exception_approval_flow.md` を正本として決裁を記録済み。

### 1-2. 確定済み決定セット

- D1: 承認順序 + 承認TTL
- D2: 適用スコープ + 例外最大継続時間
- D3: 復旧判定者 + 緊急時代理承認
- D4: 保存先 + 事後レビュー期限 + 違反時SLA

### 1-3. 完了アクション

1. `enterprise_architecture.md` / `operations.md` / `security.md` の相互リンクを同期済み。
2. dashboard と `issues/README.md` の状態を `Done` に同期済み。
3. 整合確認と docs-check 完了をもって AUTH-OPS-03 を Done 判定。

---

## 2. P1: ENV-ARCH-01（人間判断済み）

### 2-1. 決定結果

- E1: **Option B**（痕跡を残さない一括移行）
- E2: **Option C**（移行警告/監査痕跡を追加しない）
- E3: **考慮外**（期限ベース運用を採用しない）

### 2-2. 確定した実行方針

- `KJ_ATLAS_*` 以外を受理しない。
- 旧キー互換を実装しない。
- 新旧混在は不正設定として失敗させる。

### 2-3. 直近アクション

1. `settings.py` の旧キーalias削除。
2. compose / backend README / operations の旧キー記載削除。
3. 旧キー拒否をテストで固定。

---


## 3. P1: REQ-DEF-01〜03（新規）

### 3-1. 止まっている理由

- 要件定義フェーズの壁打ち結果をIssue化したが、Must/Should/Could分類と受入規約の拘束力をどこまで必須化するか未決定。
- 受入シナリオ規約を「推奨」に留めるか「必須」に引き上げるかで、後続Issue分割基準が変わる。

### 3-2. 必須決定セット（現況）

- R1: `REQ-DEF-01` の要求優先度分類（P-01〜P-07）をレビュー承認必須にするか。**→ 決定済み（Done）**
- R2: `REQ-DEF-02` のテンプレ反映方針（RACI削除、Go/No-Go条件適用、安全ゲート条件適用）。**→ 決定済み（Done）**
- R3: `REQ-DEF-03` の要求粒度↔検証粒度マッピングをテンプレ必須にするか。**→ 決定済み（Done）**

### 3-3. 決定項目（R2/R3確定）

#### 3-3-1) 「決めるべきこと」（Decision）

| Decision ID | Backlog | 論点 | 提案案 |
|---|---|---|---|
| R2-P1 | REQ-DEF-02 | `RACI` / `ContractImpact` を全Issueで必須化するか | **Reject**: RACI/責任分界点要件は削除（AIエージェント主体運用のため） |
| R2-P2 | REQ-DEF-02 | `Go/No-Go` 判定欄の適用開始時期 | **Approve (Conditional)**: 合理的に必要なIssueに限定して設置 |
| R2-P3 | REQ-DEF-02 | SafeMode/漏えい防止をレビューゲートへ接続する運用レベル | **Approve (Conditional)**: セキュリティ境界に影響するIssueのみ必須 |
| R3-P1 | REQ-DEF-03 | 要求粒度↔検証粒度マッピングをテンプレ必須化するか | R0〜R3のマッピング記述を新規Issueで必須 |
| R3-P2 | REQ-DEF-03 | 1Issue1検証責務の例外閾値 | 例外は「統合境界が2つ以上」の場合のみ許容 |
| R3-P3 | REQ-DEF-03 | 受入シナリオ最小テンプレの必須化範囲 | Process/Docs以外は必須、Docs-onlyは任意 |

#### 3-3-2) 「決めないと止まる後続作業」（Blocked work）

1. `01_Plans/issues/TEMPLATE.md` の必須項目固定（検証粒度/受入シナリオ + 条件付きGo/No-Go + 条件付きセキュリティゲート）。
2. `01_Plans/issues/README.md` の Active issue 起票手順（必須メタ定義）更新。
3. REQ-DEF-02/03 を参照する新規Issueのレビュー判定（Go/No-Go）自動化条件定義。

#### 3-3-3) R3-P1〜P3 詳細説明と推奨対応

| Decision ID | 背景（なぜ必要か） | 推奨対応 | 採用時の効果 / 非採用時のリスク |
|---|---|---|---|
| R3-P1 | 要求粒度（R0〜R3）と検証粒度（docs-check/unit/integration/e2e）の対応がIssueごとに揺れると、完了判定が人依存化する。 | **Approve（新規Issue必須）**: 新規Issueでは `要求粒度↔検証粒度` の明示を必須。既存Activeは段階適用。 | 採用時: 検証不足/過剰の両方を抑制。非採用時: 「どこまで検証すればDoneか」が再燃。 |
| R3-P2 | 1Issueに複数検証責務を混在させると、失敗時の原因切り分けと再開性が低下する。 | **Approve（条件付き）**: 原則は1Issue1検証責務。例外は「統合境界が2つ以上で分割不能」時のみ許容し、理由を `Validation plan` / `Decision Queue` に記録。 | 採用時: Issue分割の再現性と復旧性が向上。非採用時: 複合Issueが増え、レビュー工数が増大。 |
| R3-P3 | 受入シナリオの最小テンプレがないと、前提/操作/期待結果/除外の欠落が起きやすい。 | **Approve（条件付き）**: Process/実装系Issueは必須、Docs-onlyは任意（推奨）として運用。 | 採用時: 受入記述の欠落を抑制し起票品質が安定。非採用時: 受入観点のばらつきが残る。 |

> 推奨理由（総括）: R3は「人を増やすための管理」ではなく「AI主体運用でもDone判定を機械的に揃えるための検証規約」である。過剰拘束を避けるため、**R3-P1は必須化、R3-P2/R3-P3は条件付き必須**を推奨する。

### 3-4. Decision Record（確定案 / 承認待ち）

#### DR-REQ-DEF-02 (R2系)

- Context: REQ-DEF-02のテンプレ反映範囲（RACI/Go-No-Go/安全ゲート）をどう制度化するかが未確定だった。
- Decision (Final):
  - **R2-P1 = Reject**: RACI/責任分界点（ContractImpactを含む）を全Issue必須化しない。関連要件は削除する。
  - **R2-P2 = Approve (Conditional)**: Go/No-Go判定欄は合理的必要性があるIssueに限定して設置する。
  - **R2-P3 = Approve (Conditional)**: SafeMode/漏えい防止レビューゲートは、セキュリティ境界（SafeMode/share/export/import sanitize/公開設定）に影響するIssueのみ必須化する。
- Consequences:
  - R2-P1反映により、責務境界の形式管理コストを削減し、AIエージェント主体運用に合わせる。
  - R2-P2/R2-P3を条件付き必須にすることで、過剰なテンプレ拘束を避けつつ高リスク変更の安全ゲートを維持する。
- Approval status: **Approved (with mixed outcomes: Reject/Approve Conditional)**
- Approval log:
  - Date (JST): 2026-03-08
  - Decider: Human (repository operator)
  - Source statement: 「R2-P1削除」「R2-P2は必要Issueのみ」「R2-P3は条件付きApprove」

#### DR-REQ-DEF-03 (R3系)

- Context: REQ-DEF-03では検証粒度の考え方は固定済みで、テンプレ必須化/例外閾値の最終承認を行う段階だった。
- Decision (Proposal): `要求粒度↔検証粒度` と `AcceptanceScenario最小テンプレ` を新規Issue必須化し、例外は統合境界2つ以上のみ許容する。
- Consequences:
  - 採用時: 分割粒度と検証責務が明確になり、後続Issueの衝突を抑制できる。
  - 非採用時: docs-check対象の粒度判断が人依存で残り、分割ルールの再議論が継続する。
- Approval status: **Approved (R3-P1 Approve / R3-P2 Conditional Approve / R3-P3 Conditional Approve)**
- Approval log:
  - Date (JST): 2026-03-08
  - Decider: Human (repository operator)
  - Selected options: R3-P1 Approve / R3-P2 Approve (Conditional) / R3-P3 Approve (Conditional)
  - Effective from: 2026-03-08 JST
  - Notes: R3-P2/R3-P3 の条件は `TEMPLATE.md` と `issues/README.md` へ同日反映する。

### 3-5. 決定後アクション（承認後のみ実施）

1. REQ-DEF-01/02/03 は Done とし、共通I/F参照を維持する。
2. `01_Plans/issues/TEMPLATE.md` への必須反映範囲（R3-P1必須、R3-P2/R3-P3条件付き）を維持する。
3. `project-progress-dashboard.md` / `issues/README.md` / `TEMPLATE.md` の状態表示と必須項目定義を同日同期する。

## 4. 意思決定記録テンプレート

```md
[Decision Record]
- Date (UTC):
- Decider(s):
- Backlog ID:
- Selected options:
- Rationale:
- Effective from:
- Follow-up tasks:
```


## 5. 統合確認サマリ（1ページ）

### 整合点検結果

- `project-progress-dashboard.md`: AUTH-OPS-03/DOC-OPS-02/DOC-OPS-03/REQ-DEF-01/02/03 を Done に同期。
- `issues/README.md`: 上記4件を Completed issue memos へ移送し、Active一覧と実態を一致。
- decision-pack 本書: AUTH-OPS-03 を「完了」へ更新。

### 残課題（次スプリント持越し）

1. REQ-DEF-03決定内容（R3-P1〜P3）の運用定着をレビュー時に監査する。
2. DOC-OPS-02 ドリフト検知を定期運用（レビュー時チェック項目）へ組み込む。
3. REQ-DEF-02/03 の決定事項に基づくテンプレ運用の逸脱を検知した場合は是正Issueを起票する。

### 判定

- P0ボトルネック（AUTH-OPS-03 D1〜D4未確定）は解消。
- DOC-OPS-02 / DOC-OPS-03 / REQ-DEF-01/02/03 は Done へ遷移。REQ-DEF系のDecision Queueは解消済み。


## 6. P1: DOC-OPS-04（完了 / 参照記録）

### 6-1. 現在のゲート状態

- 判定: **Closed（A/B/C/D Accepted + 統合同期完了）**
- 分岐条件: `ADR-0022-doc-ops-04-documentation-information-interface.md`（A）と `ADR-0023/0024/0025`（B/C/D）がすべて `Accepted` であること。
- 現在値: 条件を満たし、`project-progress-dashboard.md` / `issues/README.md` / issue memo の同期を完了。

### 6-4. Stream D 追補監査（2026-03-14, Phase 1-4）

- Phase 2.5（FB-P2C Gate判定）: Gate 0承認Yes反映済みのため `FB-P2C-01-A2` は 再開、`A3` は A2結果同期後にProceed判定とする。

- Phase 1（Read同期）: Stream A/B/C完了報告の存在と決定リンク（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認。
- Phase 2（相互整合）: Active issue / Decision Queue / 決定ログ / 次の1手を再照合し、`DQ-HIL-EXEC-01` をReady、`DQ-FB-P2C-01`（Approved運用）と `DQ-OPS-SOURCE-01` をOpenとして更新。重複再掲・未承認決定の確定扱い・未定義競合の混入がないことを確認。
- Phase 3（件数監査）: issue memo総数43件、Open=8 / Draft=7 / Done系=25、Decision Queue未決=2（Ready=1 / Open=2）、停止条件違反0件を再計算。
- Phase 4（公開）: 再開判定チェックリストを1行確定（未固定箇所=0件 / 依存タスク契約リンク確定 / Queue未決は`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01` / 停止条件違反なし）。
- Phase 5（再同期追記）: 2026-03-14に validator/unittest/rg を再実行し、件数・Decision Queue・再開判定チェックリストの一致を維持。
- Phase 3 Verify追補（再同期）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、dashboard/README/decision-pack の相互整合（件数43、Queue Ready=1/Open=2）を再確認。
- Phase 3 Verify追補（rerun-2）: Read Gate（A/B/C完了報告・契約リンク固定・検証ログ受領）維持下で3共有ファイルを再同期し、validator/unittest/rg の成功で件数・Queue・再開判定の一致を再確認。

### 6-2. Stream D 最終同期メモ（2026-03-11）

1. Stream A/B/C の完了報告受領後に共有リソース同期を実施。
2. Active/Done件数、Decision Queue（Ready=1/Open=2）、Next actions の整合を再監査。
3. 本decision-packは履歴参照専用とし、現行ゲート状態の正本は `project-progress-dashboard.md` とする。

### 6-3. 次フェーズ開始条件（HIL-RS-01）

- `HIL-RS-01-A1` で最小I/F契約の未固定箇所を0件化する。
- A2/A3 は A1 の契約リンクを参照専用で固定し、共有リソース更新は統合フェーズへ集約する。
- validator / unittest / 同期監査（README vs dashboard）が成功した時点で Proceed とする。

### 6-5. Stream D Proceed更新（2026-03-13 rerun-3）

- Phase 1-4の再監査結果を維持し、Phase 5で次の1手を `DQ-HIL-EXEC-01`（Ready監査）/ `DQ-FB-P2C-01`（Open継続）/ `DQ-OPS-SOURCE-01`（Open継続）へ再同期。
- A1→A2→A3依存と停止条件（共有リソース同時更新違反・未承認決定の確定扱い・自己修復3回超過）は変更なし。
- Verify追補（rerun-3）として validator/unittest/rg 成功ログを反映し、dashboard/README/decision-pack のQueue・件数・再開判定チェックリスト一致を維持。
- Verify追補（rerun-4）: Stream D専有の共有資源3ファイル同期後に validator/unittest/rg を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を確認。
- Verify追補（rerun-5）: Stream A/B/C完了報告および決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、validator/unittest/rg を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。

- Verify追補（rerun-6）: Stream A/B/C完了報告および決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、validator/unittest/rg を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Verify追補（rerun-7）: Stream A/B/C完了報告および決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、validator/unittest/rg を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Verify追補（rerun-8）: Phase 1 Read Gate（A/B/C完了報告・契約リンク固定・検証ログ受領）を再確認後、共有統合3ファイルを同時更新し、validator/unittest/rg を再実行して件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Verify追補（rerun-9）: Stream A/B/C完了報告と決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）をRead同期で再確認後、validator/unittest/rg を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Verify追補（rerun-10）: Stream A/B/C完了報告と決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）をRead同期で再確認後、validator/unittest/rg を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Verify追補（rerun-11, Stream F）: Phase 1 Read Sync（3共有ファイル再読）→Phase 2 同期反映（件数/状態/依存/判断キュー）→Phase 3 validator/unittest/`rg` 検証→Phase 4 Closeout を完了し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行・停止条件違反0件を再確定。
- Verify追補（rerun-13, Stream F）: 起動条件（A〜E完了報告受領 / A1→A2→A3依存整合 / shared resource freeze解除）をRead Gateで再確認後、Phase 1-5（Read→Plan→Execute→Verify→Proceed）を実施。`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` の成功により、件数43・Active2・Done25・Queue Ready=1/Open=2・停止条件違反0件・未承認決定混入なしを再確定。

### 6-6. Stream G 監査ログ（Source Issue運用方針, 2026-03-14）

- Phase 1 Read: `README.md` と `01_Plans/issues/README.md` を再読し、`Source Issue` 運用は「GitHub Issues未運用の間は `N/A` 維持」「開始宣言確定後にURL移行」の方針を確認。
- Phase 2 Plan（イベント駆動の再判定条件）:
  1. **開始宣言イベント**: PM/Triage による「GitHub Issues正本運用開始」宣言（日時/RACI-I通知）が確定した時。
  2. **正本不整合イベント**: `Active issue memos` の `Source Issue` 列で `N/A` とURLが混在し、README運用規定と不整合が検知された時。
  3. **検証失敗イベント**: `validate_active_issue_memos.py` / unittest / `rg` により `Source Issue` 規約違反が検出された時。
  4. **運用境界変更イベント**: `01_Plans/issues/README.md` の Scope または Source Issue運用基準が改訂された時。
- AC/DoD ドラフト（Stream G提案）:
  - AC-1: 開始宣言未確定の間、Active memo の `Source Issue` は `N/A` のみである。
  - AC-2: 再判定時は「イベント種別 / 判定結果 / 根拠ファイル / 次アクション」を本decision-packへ1レコード追記する。
  - DoD-1: `README.md` と `01_Plans/issues/README.md` の双方と矛盾しない判定文である。
  - DoD-2: Fail-safe（開始宣言未確定でURL化しない）を満たし、Self-Correction上限（3回）を超えない。
- Phase 3 Execute: 現時点は **`Source Issue: N/A` 維持** とし、URL化は未実施（開始宣言未確定のため）。
- Phase 4 Verify: 運用方針との矛盾なし（README系記述と整合）。Self-Correction発生なし（0/3）。
- Phase 5 Proceed（Fレーン通知）: **反映要否=不要（No update required）**。理由: 判定はN/A維持継続であり、README本文更新を要する新事実なし。


### 6-7. Stream H 最終統合ログ（2026-03-14）

- Phase 1 Read同期: Stream A〜G完了報告、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を再確認。
- Phase 2 反映: shared resource 3ファイル（`issues/README.md` / `project-progress-dashboard.md` / 本decision-pack）で Active/Done/Queue/次の1手を同一方針へ同期。
- Phase 3 件数再監査: issue memo総数43件（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25）、運用集約値 Active=2 / Done=25、Decision Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）を再計算。
- Phase 4 公開（1行固定）: **再開判定チェックリスト確定** = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。
- Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を再実行し、3ファイル一致を確認。

### 6-8. Stream E 最終同期ログ（2026-03-14, Phase 1-5）

- Phase 1 Read同期: Stream A/B/C/D完了報告、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、shared resource以外の未マージ差分なしを再確認。
- Phase 2 Plan統合: Active/Done件数（Active=2 / Done=25）、issue memo総数43件（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25）、次アクション（Ready監査1件 + Open期限管理2件）を3ファイル共通値として固定。
- Phase 3 Execute: `project-progress-dashboard.md` / `issues/README.md` / 本decision-pack のみを単一変更セットで更新。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・依存順・再開判定1行の一致を確認。
- Phase 5 Proceed（公開ログ1行）: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-9. Stream F 最終同期ログ（2026-03-14 rerun-14, Phase 1-5）

- Phase 1 Read: Stream A〜E完了報告、依存順 `A1→A2→A3`、Decision Queue（Ready=1 / Open=2）、shared resource freeze解除、停止条件違反0件を再確認。
- Phase 2 Plan: 同期対象を `issues/README.md` / `project-progress-dashboard.md` / 本decision-pack の3ファイルに限定し、件数43・Active=2・Done=25・次アクション（Ready監査1件 + Open期限管理2件）を固定。
- Phase 3 Execute: 3ファイルを単一変更セットで同期し、Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）と再開判定チェックリスト1行を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・リンク整合の一致を確認。
- Phase 5 Publish: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-10. Stream F 再同期ログ（2026-03-14 rerun-15, Phase 1-5）

- Phase 1 Read: Stream A〜E完了報告、依存順 `A1→A2→A3`、Decision Queue（Ready=1 / Open=2）、Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）、停止条件違反0件を再確認。
- Phase 2 Plan: 反映差分を shared resource 3ファイルの rerun-15 同期ログ追記に限定し、件数43（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25）・Active=2・Done=25・次アクション（Ready監査1件 + Open期限管理2件）を固定。
- Phase 3 Execute: `project-progress-dashboard.md` / `issues/README.md` / 本decision-pack のみを単一変更セットで更新。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・依存順・再開判定1行の一致を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**



### 6-11. Stream E 再同期ログ（2026-03-14 rerun-16, Phase 1-4）

- Phase 1 Read同期: Stream A/B/C/D完了報告、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を再確認。
- Phase 2 反映: shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）の件数・状態・Decision Queueを `件数43 / Active=2 / Done=25 / Ready=1 / Open=2` へ同期。
- Phase 3 整合監査: 参照リンク、件数、依存順の一致を点検し、未承認決定の確定扱い・件数不整合・未定義競合の混入なしを確認。
- Phase 4 公開: **再開判定チェックリスト1行を確定**（未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし）。
- Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイルの公開値一致を再確認。


### 6-12. Stream F 最終再同期ログ（2026-03-14 rerun-17, Phase 1-5）

- Phase 1 Read Gate: Stream A〜E完了報告受領、依存順 `A1→A2→A3`、Decision Queue（Ready=1 / Open=2）、停止条件違反0件の証跡を再確認。
- Phase 2 Plan: 更新差分を shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）に限定し、件数43・Active=2・Done=25・次アクション（Ready監査1件 + Open期限管理2件）を固定。
- Phase 3 Execute: 3ファイルを単一変更セットで同期し、Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）と依存順 `A1→A2→A3` を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・依存順・再開判定1行の一致を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-13. Stream D 統合同期ログ（2026-03-14 rerun-18, Phase 1-5）

- Phase 1 Read Sync Gate: Stream A/B/C 完了報告・契約リンク（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）・検証ログ受領を再確認し、不足0件を確認。
- Phase 2 Plan: 公開値を `件数43（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25） / Active=2 / Done=25 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` に固定し、AC/DoD不足なしとして同期計画を確定。
- Phase 3 Execute: shared resource 3ファイル（`issues/README.md` / `project-progress-dashboard.md` / 本decision-pack）のみを単一変更セットで同期。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイルの件数・Queue・依存順・再開判定の一致を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-14. Stream F 共有資源再同期ログ（2026-03-14 rerun-19, Phase 1-5）

- Phase 1 Read Gate: Stream A〜E完了報告受領、依存順 `A1→A2→A3`、Decision Queue（Ready=1 / Open=2）、停止条件違反0件を再確認。
- Phase 2 Plan: 更新対象を shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）に限定し、件数43（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25）・Active=2・Done=25・次アクション（Ready監査1件 + Open期限管理2件）を固定。
- Phase 3 Execute: 3ファイルを単一変更セットで同期し、Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）と依存順 `A1→A2→A3` を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・依存順・再開判定1行の一致を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-15. Stream E 共有資源最終同期ログ（2026-03-14 rerun-20, Phase 1-5）

- Phase 1 Read同期: Stream A/B/C/D完了報告、依存順 `A1→A2→A3`、Decision Queue（Ready=1 / Open=2）、停止条件違反0件、shared resource以外の未マージ差分なしを再確認。
- Phase 2 Plan: 更新対象を shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）に限定し、公開値 `件数43（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25） / Active=2 / Done=25 / Decision Queue Ready=1 Open=2` を固定。
- Phase 3 Execute: 3ファイルを単一変更セットで同期し、Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）・依存順 `A1→A2→A3`・停止条件違反0件を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・依存順・再開判定1行の一致を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-16. Stream D 共有資源再同期ログ（2026-03-14 rerun-21, Phase 1-5）

- Phase 1 Read Gate: Stream A/B/C完了報告、契約リンク（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）、検証ログ受領を再確認し、不足0件を確認。
- Phase 2 Plan: 更新対象を shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）に限定し、公開値 `件数43（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25） / Active=2 / Done=25 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` と再開判定1行を固定。
- Phase 3 Execute: 3ファイルを単一変更セットで同期し、片側更新なしを維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・依存順・再開判定1行の一致を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**


### 6-17. Stream D 共有資源再同期ログ（2026-03-14 rerun-22, Phase 1-5）

- Phase 1 Read Gate: Stream A/B/C/E/F完了報告、依存順 `A1→A2→A3`、Decision Queue（Ready=1 / Open=2）、停止条件違反0件を再確認。
- Phase 2 Plan: 更新対象を shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）に限定し、公開値 `件数43（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25） / Active=2 / Done=25 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` と Source Issue=N/A 運用維持を固定。
- Phase 3 Execute: Active table / Decision Queue / Next actions / 集計値を単一変更セットで同期し、推測更新を行わない。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・依存順・再開判定1行の一致を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-18. Stream E 共有ファイル同期ログ（2026-03-14 rerun-23, Phase 1-5）

- Phase 1 Read Gate: Stream A/B/C/D完了報告受領、shared resource freeze解除、依存順 `A1→A2→A3`、Decision Queue（Ready=1 / Open=2）、停止条件違反0件を再確認。
- Phase 2 Plan: 更新対象を shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）に限定し、公開値を `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25） / Active=6 / Done=25 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` に固定。
- Phase 3 Execute: 3ファイルを単一変更セットで同期し、Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）・停止条件違反0件・Source Issue運用（Open=N/A / Draft=TBD）を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、件数・Queue・依存順・再開判定1行の一致を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-19. Stream D 共有資源同期ログ（2026-03-15 rerun-24, Phase 1-5）

- Phase 1 Read Gate: `issues/README.md` / `project-progress-dashboard.md` / 本decision-pack を再読し、件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25）、Active=6、Done=25、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を確認。
- Phase 2 Plan: 更新対象を shared resource 3ファイルに限定し、更新項目を「件数 / 状態 / 次の1手 / Source Issue運用」に固定。`Source Issue` は README 運用基準（Open=`N/A` / Draft=`TBD`）を維持。
- Phase 3 Execute: 3ファイルを単一変更セットで同時更新し、Active表・Decision Queue・再開判定チェックリストを同一値へ同期。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26|Source Issue" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、不一致0件を確認（self-correction 0/3）。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**


### 6-20. Stream E 共有統合同期ログ（2026-03-15 rerun-25, Phase 1-5）

- Phase 1 Read同期: Stream A/B/C/D 完了報告と証跡リンク（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認し、公開基準値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25） / Active=6 / Done=25 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` を確定。
- Phase 2 Plan: 反映対象を shared resource 3ファイルの Active表 / Queue / 次の1手 / 件数集計に限定し、AC/DoD不足なしを確認（未承認事項は確定扱いしない）。
- Phase 3 Execute: 3ファイルを同一ロジック・単一変更セットで同期し、Source Issue 運用基準（Open=`N/A` / Draft=`TBD`）と Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26|DR-HIL-A1-01|DL-HIL-01|DR-REQ-DEF-02" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、不一致0件（self-correction 0/3）を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-10. Stream F 同期ログ（2026-03-15 rerun-26, Phase 1-5）

- Phase 1 Read同期: shared resource 3ファイルを再読し、件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25）、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を確認。
- Phase 2 Plan: 単一変更セット対象を `issues/README.md` / `project-progress-dashboard.md` / 本decision-pack に限定し、Decision Queueと件数公開値の維持を計画。
- Phase 3 Execute: 3ファイルへ rerun-26 同期ログのみ追記し、未承認決定の確定扱いを行わないことを再確認。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-26|Decision Queue|A1→A2→A3|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` の成功を確認。
- Phase 5 Proceed（次回再開条件）: **A〜E完了報告と shared resource freeze解除が維持され、件数47・Decision Queue Ready=1/Open=2・依存順A1→A2→A3・停止条件違反0件が一致していること。**



### 6-21. Stream F 同期ログ（2026-04-11 rerun-27, Phase 1-5）

- Phase 1 Read同期: shared resource 3ファイルを再読し、件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25）・Active=6・Done=25・Decision Queue（Ready=1 / Open=2）・依存順 `A1→A2→A3`・停止条件違反0件を再確認。
- Phase 2 集約反映: Active issue / Decision Queue / 依存順 / 再開判定チェックリストを3ファイルで同期し、未承認決定を確定扱いしない方針を維持。
- Phase 3 検算: Open/Draft/In Progress/Done系件数、Queue残件2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）、参照リンク整合を再計算して不一致0件を確認。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-27|件数47|Active=5|Done=26|Decision Queue|A1→A2→A3|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し成功。
- Phase 5 Publish（次回再開条件）: **A〜E完了報告リンク維持 + shared resource freeze解除維持 + 件数47 / Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件が一致していること。**


### 6-22. Stream H 最終同期ログ（2026-04-12 rerun-28, Phase 1-5）

- Phase 1 Read: Stream A〜G 完了報告と証跡リンク、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を再確認。
- Phase 2 Plan: 反映対象を shared resource 3ファイル（`01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / 本decision-pack）に限定し、件数/状態/Decision Queue/次アクションを `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Ready=1 / Open=2` へ固定。
- Phase 3 Execute: 3ファイルを単一変更セットで同期し、Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）と Source Issue運用（Open=`N/A` / Draft=`TBD`）を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、不一致0件（self-correction 0/3）を確認。
- Phase 5 Proceed: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

### 6-23. Stream H 共有統合同期ログ（2026-04-12 rerun-29, Phase 1-5）

- Phase 1 Read同期: Stream A〜G 完了報告と証跡リンク、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を再確認。
- Phase 2 Plan: 更新対象を shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）に限定し、公開値を `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2` に固定。
- Phase 3 Execute: 3ファイルを単一変更セットで再同期し、Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`）と Source Issue運用（Open=`N/A` / Draft=`TBD`）を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、不一致0件（self-correction 0/3）を確認。
- Phase 5 Proceed（公開固定）: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**


### 6-25. Stream I 共有統合同期ログ（2026-04-14 rerun-31, Phase 1-5）

- Phase 1 Read: Stream A〜H 完了報告、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件、競合検知0件を再確認。
- Phase 2 Plan: 更新対象を shared resource 3ファイル（`project-progress-dashboard.md` / `issues/README.md` / 本decision-pack）に限定し、公開値を `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2` に固定。次の1手は `DQ-HIL-EXEC-01` Ready監査継続 + `DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` Open期限管理を維持。
- Phase 3 Execute: 3ファイルを単一変更セットで同期し、未承認決定の確定扱い禁止・Source Issue運用（Open=`N/A` / Draft=`TBD`）を維持。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26|rerun-31" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、不一致0件（self-correction 0/3）を確認。
- Phase 5 Proceed（公開固定）: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**


## 7. HIL-RS Contract Pack (Stream A, 2026-04-13)

### 7-1. Contract IDs（read-only handoff）
- Freeze Pack: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- A1 interface IDs: `A1-CRITIQUE-IF`, `A1-REDIFF-IF`, `A1-ATTR-IF`, `A1-ERROR-IF`
- CE0 guard IDs: `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05`

### 7-2. Fixed Values
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`

### 7-3. Proceed / NoGo Formula
- `Go = (A1 Done && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)`
- `NoGo = !Go`

### 7-4. Prohibited Operations
- Pending bypass
- A2/A3側での契約ID・固定値の再定義
- 未承認決定の確定化
- SafeMode後退 / review自動昇格 / direct write / auto-apply

### 7-5. Stop Conditions
- Self-Correction 3回超過
- 固定識別子不一致
- 未定義競合
- 前提崩壊（A1未完了またはQueue未解消）

### 7-6. Return Route
- 差分要求は常に `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差戻し。

### 6-13. Stream A Critical Path rerun-32（2026-04-14, 共有3ファイル正規化）

- Phase 1 Read: shared resource 3ファイルと HIL-RS 個票を再読し、Decision Queue（`Ready=1 / Open=2`）・依存順（`A1→A2→A3`）・個票Status（Open=4/Draft=1/Done=1）を再確認。
- Phase 2 ADR明文化判定: 新規Decision不要。承認待ちが必要な新規判断は発生せず、未承認決定の確定化を回避。
- Phase 3 正規化方針: lifecycleは `Draft/Open/In Progress/Done` の4状態のみを公開値として扱い、`Blocked` は `Open(hold)` に内包して集計。
- Phase 4 同期値（基準47件）: `Open=12（Open10+Blocked2） / In Progress=1 / Draft=8 / Done=26`、Decision Queueは `Ready=1 / Open=2` を維持。
- Phase 5 Verify: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` により3共有ファイルの一致を確認。

