# Issue Draft: REQ-DEF-02 責任分界点と契約チェックポイントの要求定義

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner + Security Officer
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0011`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`, `02_Architecture/enterprise_architecture.md`
- Expected verification level: `docs-check`


## Requirement meta I/F（REQ-DEF共通キー）

> REQ-DEF-01/02/03 で共通利用する要求メタ項目。後続再編集競合を防ぐため、このキーセットを先に固定する。

- Requirement ID
- Requirement statement
- Priority class（Must / Should / Could）
- RACI（A/R/C/I）
- Contract impact（schema/api/policy/ops: あり/なし）
- Acceptance scenario（前提/操作/期待結果/除外）
- Verification level（docs-check / unit / integration / e2e）
- Decision status（Fixed / Pending）
- Decision queue ref（未確定時の参照先）

### B-3. I/Fキー実装（本Issueの独立実行範囲）

> 独立実行可能理由: B-3のI/Fキーに RACI / Contract impact 判定を埋める専任タスクとして切り出し可能。

| Key | このIssueでの確定値 | 備考 |
|---|---|---|
| Requirement ID | `REQ-DEF-02` | 固定 |
| Priority class | `Must` | 監査説明責任の成立条件 |
| RACI（A/R/C/I） | **A:** Platform Architecture Owner / **R:** Security Officer / **C:** Product Owner, Implementer / **I:** Reviewer, Operations | RACIを要求定義時点で先に固定 |
| Contract impact | **schema:** なし / **api:** なし / **policy:** あり / **ops:** あり | 契約判定を明示 |
| Verification level | `docs-check` | ドキュメント整合のみ |
| Decision status | `Fixed` | B-3は本Issueで確定 |
| Decision queue ref | `Pending-2`, `Pending-3` | 全Issue必須化は別判断 |

## 1) 課題 / Problem statement

- 要件定義フェーズで「誰がどこまで決めるか（責務境界）」が明示されないと、実装Issueで設計判断が再燃する。
- Architecture文書とOperations文書で責任分界の言い回しがずれると、受入判定責任が曖昧になる。
- 契約正本（schema/API/policy）と運用手順の境界が曖昧なままだと、後方互換判断が遅れる。

## 2) 背景 / Context

- AGENTS.md は上流整合（00〜02）を実装着手条件としている。
- `schemas.md` は互換性判断の単一正本であり、要件段階で変更有無を宣言する必要がある。
- `enterprise_architecture.md` は組織要件（役割分離/監査）の根拠であり、責任分界点の要求定義に必須。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Human-in-the-loop の成立には責任分界の可視化が前提。
- 安全（THREAT_MODEL / SafeMode）: 責務不明確は例外運用の拡大を招き、安全境界が緩む。
- 企業・行政要件（enterprise_architecture）: 監査説明責任を満たすため、決定権限を明文化する必要がある。
- 後方互換（schemas）: 契約変更の判定ゲートを要求定義で先に固定できる。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（責任分界点要求・契約チェックポイント定義）。
- 変更の最小単位:
  - T1: 役割別責務（Product/Architecture/Security/Implementer/Reviewer）を要求文脈で定義。
  - T2: 契約チェックポイント（Schema/API/SafeMode/Export）を要求テンプレに追加。
  - T3: 「要件確定前に実装へ進まない」停止条件を明文化。
- 非目標:
  - 認可ロジックやAPI仕様の変更。
  - CI設定や運用ツールの導入。

## 5) 受入条件 / Acceptance criteria

- [x] 役割ごとの決定責務と承認責務が要求文書で判読可能になる。
- [x] 契約チェックポイント（schema/API/policy/ops）が要求定義テンプレに追加される。
- [x] 各要求に「契約変更あり/なし」の判定欄がある。
- [ ] SafeMode・漏えい防止・監査要件の境界が必須項目として保持される。
- [ ] docs-check でメタ情報と参照整合を確認できる。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 責任分界点のRACI表（要求定義向け）を作成する。
- [x] T2: 契約チェックポイントの定義表を作成する。
- [x] T3: 要件未確定時の停止基準（Go/No-Go）を作成する。
- [ ] T4: 後続Issueテンプレへ責任分界点項目を反映する。

### Plan → Execute → Verify（本実施ログ）

1. **Plan**
   - B-3のI/Fキーに `RACI` と `Contract impact` の確定値を埋める。
   - 許可スコープ外（REQ-DEF-01/03本文、運用文書）へは変更を拡張しない。
2. **Execute**
   - 本Issue内に B-3専用セクションを追加し、RACI/契約判定を表形式で固定。
   - T1〜T3の完了をこのIssue内でチェック済みに更新。
3. **Verify**
   - `validate_active_issue_memos.py` と unit test で体裁・必須項目整合を確認。
   - 文言追跡は `rg` で確認。

### 自己修復ログ（最大3回）

- Attempt 1: validator実行（失敗時は不足項目を修正）。
- Attempt 2: unit test実行（失敗時はフォーマット/期待値差分を修正）。
- Attempt 3: `rg` によるキーワード存在確認（不足時は追記）。
- **Fail-safe停止条件**: 3回の自己修復で整合が回復しない場合は、変更を最小化して停止し未解決点を `Decision Queue` に記録する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "REQ-DEF-02|責任分界|契約チェックポイント|Go/No-Go" 01_Plans 02_Architecture 04_Documentation`
- 期待結果:
  - issue memo validator が成功し、責任分界点の要求が文書上で追跡できる。
- 未実施時の理由・代替検証:
  - Python未導入時は `rg` による存在確認で代替し、未実施理由を残す。

## 8) 代替案 / Alternatives considered

- 代替案A: 実装担当者の裁量で責任分界を都度決める。
  - 却下理由: 監査説明責任と再現性が確保できない。
- 代替案B: Architecture更新のみを先行し、Issueテンプレ更新を行わない。
  - 却下理由: 実務の起票時に責任分界点が抜け落ちる。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 責任分界点が細かすぎて運用負荷を上げる。
- 影響範囲: 要求定義作業、レビュー会運営、文書同期作業。
- ロールバック手順: 必須項目を最小セット（決定責務/承認責務/契約変更判定）へ縮退する。

## 10) Additional context

- 実装前に責任分界点を固定することで、後工程の論点再燃を抑制する。
- ADR化が必要になる条件（トレードオフ閾値）:
  1. RACIを全フェーズ必須ルールとして固定する場合。
  2. 契約チェックポイントをCIゲートへ接続する場合。


## Decision Queue（残る未確定）

- Pending-1: `01_Plans/issues/TEMPLATE.md` へ共通I/Fキー（RACI/Contract impact）を必須化する範囲。
- Pending-2: `Go/No-Go` 判定欄を全Issue共通必須にする適用開始時期。
- Pending-3: 監査境界（SafeMode/漏えい防止）をレビューゲートへ接続する運用レベル。
