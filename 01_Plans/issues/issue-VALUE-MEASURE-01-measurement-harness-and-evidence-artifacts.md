# Issue Draft: VALUE-MEASURE-01 価値観測ハーネスと証拠成果物

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: TBD（A=Productization Program Owner / R=QA Lead）
- Scope: `01_Plans/`, `02_Architecture/value_traceability.md`, `03_Implement/frontend/e2e/`, `04_Documentation/acceptance_check.md`
- Related Backlog: `VALUE-MEASURE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0037-value-measurement-harness-and-scorecard.md`, `01_Plans/adr/ADR-0036-value-to-social-goal-realization-roadmap.md`, `01_Plans/adr/ADR-0032-product-value-realization-model.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: VALUE-MEASURE-01
- RequirementStatement: 価値ループ V0–V4 の各価値仮説を `Hypothesis → Action(操作列) → Evidence(証拠ID) → Decision` の再実行可能な観測単位として束ね、証拠成果物の形式と再測定手順を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=PRODUCT-VALUE-01..03 の価値仮説とKPIが存在する / 操作=各価値ループの操作列をE2E名または手動手順へ割当て、証拠ID・形式・保存先・再測定一致条件を定義する / 期待結果=同一手順で同一種類の証拠が再取得でき、版間比較が可能 / 除外=個人追跡、行動スコアリング、監視テレメトリ。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode（観測が漏洩経路にならないこと）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0037`

## 1) 課題 / Problem statement

- `ADR-0032` の観測モデルと各VALUE issueのKPIは「記述契約」止まりで、観測を実際に回す成果物（再現手順・証拠形式・再測定手順）が存在しない。
- このため機能完了と価値実感の乖離が観測されず、Go/No-Goの根拠が宣言ベースになる。

## 2) 背景 / Context

- `ADR-0037` が VR4 の観測ハーネスを定義し、本issueはその実装入口（docs-firstで手順と形式を固定）。
- `PRODUCT-VALUE-01..03` は `Hypothesis→Action→Evidence→Decision` とKPIを既に保持している（再利用する）。
- `ADR-0019` がE2E確認方針、`acceptance_check.md` が利用者向け受入確認の正本。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 価値実感を再現可能に観測でき、価値実現の進捗を事実で示せる。
- 安全（THREAT_MODEL / SafeMode）: 観測が未レビュー本文や機微情報の新たな漏洩経路にならないことを要件化する。
- 企業・行政要件（enterprise_architecture）: 監査可能な証拠成果物が、組織導入時の説明責任を支える。
- 後方互換（schemas）: 既存E2E/受入手順を壊さず、観測単位と証拠IDの対応のみ追加する。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs first（観測単位カタログ、証拠成果物の形式定義、再測定手順）。実装はE2E名の割当のみで、新規UI/Schemaは作らない。
- 変更の最小単位: 価値ループ1つにつき「観測単位ID / 操作列 / 証拠ID / 形式 / 保存先 / 再測定一致条件」を1行で定義する。
- 非目標: 個人追跡、行動スコアリング、監視テレメトリ拡張、新規永続テーブル追加。

## 5) 受入条件 / Acceptance criteria

- [ ] V0–V4 の各価値仮説に、再実行可能な観測単位（操作列+証拠ID）が対応する。
- [ ] 証拠成果物の形式が版間比較可能な固定形式で定義される。
- [ ] 再測定手順と「再測定一致条件」が明文化される。
- [ ] 観測が SafeMode 境界を越えず、未レビュー本文・機微情報を新たに出力しない。
- [ ] `KJ_ATLAS_LLM_PROVIDER=none` 既定構成でも観測単位が実行可能である。
- [ ] docs-check（validator/triage/rg）で観測単位カタログの整合と検索可能性が確認される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 V0–V4 の観測単位カタログ（ID/操作列/証拠ID）を作成する。
- [ ] T2 証拠成果物の固定形式と保存先を定義する。
- [ ] T3 再測定手順と再測定一致条件を明文化する。
- [ ] T4 SafeMode非後退と非監視制約のチェック項目を追加する。
- [ ] T5 `value_traceability.md` / `acceptance_check.md` と同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `rg -n "観測単位|Evidence|証拠ID|再測定" 01_Plans 02_Architecture 04_Documentation`
- 期待結果:
  - validator成功、triage stopper=none、観測単位カタログが検索可能。
- 未実施時の理由・代替検証:
  - 実E2E実行前は、操作列とE2E名の割当・証拠形式レビューで代替し理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 各VALUE issueのKPI記述のみで運用する。再現手順と証拠形式が固定されず比較不能なため不採用。
- 代替案B: テレメトリで自動計測する。監視・個人追跡の非目標に反するため不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 観測項目が増えすぎ、計測が監視的になる。
- 影響範囲: E2E、受入手順、value_traceability。
- ロールバック手順: 観測単位を代表シナリオ最小セットへ縮退し、証拠形式を既存E2E成果物の範囲へ戻す。

## 10) Additional context

- 関連: 集計運用（スコアカード）は `VALUE-MEASURE-02`、Program Gate入力は `MVP-EXIT-01` / `PRODUCT-QA-01`。
- ADR化が必要になる条件: 証拠成果物を新しい永続契約（保存形式/保管期限）として固定する場合。


## 11) Stream H planning lock（2026-06-13）

| Item | Planning decision |
| --- | --- |
| Classification | Hold / deferred-open-ready（VR4 direction retained, activation postponed） |
| Measurement target | Value Hypothesis, User Action, Evidence Artifact, Decision Gate linkage for VR1–VR3 outcomes. |
| Evidence artifact types | Issue text, mock/synthetic scenario notes, proposed evidence IDs, command logs, and manual review notes; no implementation artifact is required now. |
| Go condition | Real-user/cooperator milestone or maintainer-approved surrogate-evidence milestone exists, and SafeMode/share-export invariants are represented in every gate. |
| No-Go condition | Frontend E2E implementation is required by this planning issue, real-user KPI is fixed before users exist, or telemetry expands into individual tracking. |
| Deferral reason | `ADR-0039` keeps VR4 observation mechanisms deferred during solo OSS/pre-release to avoid heavyweight governance. |

### Non-goals

- Do not require `03_Implement/` changes, Playwright scenario creation, telemetry, or real participant recruitment.
- Do not make the harness a release blocker before activation.
