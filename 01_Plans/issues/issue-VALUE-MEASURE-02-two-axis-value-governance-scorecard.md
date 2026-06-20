# Issue Draft: VALUE-MEASURE-02 価値KPI×統治の二軸スコアカード運用

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD（A=Productization Program Owner / R=QA Lead）
- Scope: `01_Plans/`, `01_Plans/project-progress-dashboard.md`, `04_Documentation/`
- Related Backlog: `VALUE-MEASURE-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0037-value-measurement-harness-and-scorecard.md`, `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0036-value-to-social-goal-realization-roadmap.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: VALUE-MEASURE-02
- RequirementStatement: 価値KPI軸（活性化/曖昧さ保持/成果物レビュー可能性）と統治軸（SafeMode境界/review帰属/証拠再現性）の二軸スコアカードを、`MVP-EXIT-01` Program Gate と `PRODUCT-QA-01` の判定入力として運用化する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=VALUE-MEASURE-01の証拠成果物が取得できる / 操作=二軸へKPIと統治チェックを集約し、`Go / Conditional Go / No-Go` を `candidate/date/reviewer/decision/artifactId/re-decision` 付きで記録する / 期待結果=判定がスコアカードから再現でき、統治軸の後退時は即No-Goになる / 除外=自動Go/No-Go確定、個人追跡。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export（統治軸の後退検知）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0037`

## 1) 課題 / Problem statement

- `ADR-0032` の二軸スコアカードは契約として固定されたが、誰がどの入力で集計し、Program Gate/Release判定へどう渡すかの運用が未定義。
- 価値KPIだけを見て統治後退（SafeMode緩和/review自動昇格）を見落とすリスクがある。

## 2) 背景 / Context

- `ADR-0037` が二軸スコアカードの運用方針を定義し、本issueはその集計運用の入口。
- `MVP-EXIT-01` は Program判定、`PRODUCT-QA-01` は Release Readiness判定を担い、判定式 `Go / Conditional Go / No-Go` は既存。
- KPIは `PV01-K1 / PV02-K1 / PV03-K1` を価値KPI軸の代表とし、各VALUE issueを正本とする。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 価値と統治を同一カードで突合し、価値追求が安全を損なわないことを保証する。
- 安全（THREAT_MODEL / SafeMode）: 統治軸の後退を即No-Goにする判定規則を固定する。
- 企業・行政要件（enterprise_architecture）: 監査可能な判定記録（candidate/date/reviewer/decision）が説明責任を支える。
- 後方互換（schemas）: 既存判定式・ゲート定義を再利用し、新しいスコア序列UIを導入しない。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（スコアカード様式、集計手順、判定記録テンプレ、ダッシュボード反映ルール）。
- 変更の最小単位: 1判定 = 二軸の集計 + `Go/Conditional/No-Go` + 監査フィールド。
- 非目標: 自動判定確定、利用者の序列化・スコアリングUI、監視テレメトリ。

## 5) 受入条件 / Acceptance criteria

- [ ] 価値KPI軸と統治軸の集計様式が定義され、各KPIが定義可能・再測定可能・比較可能を満たす。
- [ ] 統治軸の後退（safeMode緩和 / `human_reviewed`自動昇格 / 証拠欠落）検知時は即No-Goとする規則が明文化される。
- [ ] 判定記録に `candidate / date / reviewer / decision / artifactId / re-decision condition` が必須化される。
- [ ] スコアカードが `MVP-EXIT-01` / `PRODUCT-QA-01` の入力として参照される導線が定義される。
- [ ] 自動でGo/No-Goを確定せず、判定は人間がDecision Queueへ記録する。
- [ ] docs-check（validator/triage/rg）で様式と判定テンプレの整合が確認される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 二軸スコアカード様式（行=観測対象、列=KPI/判定/証拠）を定義する。
- [ ] T2 統治軸の即No-Go規則を明文化する。
- [ ] T3 判定記録テンプレ（監査フィールド付き）を定義する。
- [ ] T4 `MVP-EXIT-01` / `PRODUCT-QA-01` への入力導線を記述する。
- [ ] T5 `project-progress-dashboard.md` への反映ルール（正本更新後に同期）を記述する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `rg -n "スコアカード|価値KPI軸|統治軸|Go / Conditional Go / No-Go" 01_Plans 04_Documentation`
- 期待結果:
  - validator成功、triage stopper=none、スコアカード様式と判定テンプレが検索可能。
- 未実施時の理由・代替検証:
  - 実判定前は、様式レビューとサンプル判定の机上適用で代替し理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 価値KPIのみで判定する。統治後退を見落とすため不採用。
- 代替案B: 単一総合スコアに集約する。反スコアリング原則（P-02）と矛盾するため不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: スコアカードが重くなり判定運用が形骸化する。
- 影響範囲: Program Gate、Release判定、ダッシュボード。
- ロールバック手順: 二軸の必須項目を代表KPI+統治チェック最小セットへ縮退する。

## 10) Additional context

- 関連: 観測単位と証拠は `VALUE-MEASURE-01`、社会的普及の観測は `SOCIAL-DIFFUSION-04`（非監視シグナル）。
- ADR化が必要になる条件: 判定式やゲート閾値そのものを変更する場合（本issueは様式・運用のみ）。


## 11) Stream H scorecard lock（2026-06-13）

| Item | Planning decision |
| --- | --- |
| Classification | Hold / deferred-open-ready（VR4 scorecard direction retained, activation postponed） |
| Scorecard axes | Value realization evidence × governance/safety guardrail evidence. |
| Minimal evidence while deferred | One row per candidate gate with evidence ID, owner=Maintainer, Go/No-Go wording, and rollback/hold destination. |
| Activation condition | Measurement-harness artifacts exist and there is a real-user/cooperator or maintainer-approved surrogate-evidence milestone. |
| No-Go condition | Scorecard is treated as mandatory release blocker, introduces individual scoring, weakens SafeMode/share-export, or requires multi-role RACI before collaborators exist. |
| Lightweight governance | Maintainer is sufficient A/R in solo OSS/pre-release; expand roles only after activation. |

### Non-goals

- Do not require dashboards, telemetry collection, admin-centered KPI monitoring, or external-participant metrics before activation.
