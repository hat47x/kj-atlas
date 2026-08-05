# Issue Draft: SOCIAL-DIFFUSION-04 非監視型の採用シグナル

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD（A=Productization Program Owner / R=Security Officer）
- Scope: `01_Plans/`, `02_Architecture/value_traceability.md`, `04_Documentation/security.md`, `04_Documentation/data_handling.md`
- Related Backlog: `SOCIAL-DIFFUSION-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0038-social-diffusion-of-explainable-consensus.md`, `01_Plans/adr/ADR-0037-value-measurement-harness-and-scorecard.md`, `01_Plans/adr/ADR-0032-product-value-realization-model.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: SOCIAL-DIFFUSION-04
- RequirementStatement: 社会的普及の採用・価値を、個人追跡・行動スコアリング・監視テレメトリを用いず、opt-in・集計・ローカルファースト・成果物ベースの非監視シグナルで観測する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=社会配布が運用される / 操作=非監視シグナル（成果物に含まれる保留/根拠要素の充足率、再オープン可能性の自己診断など）を定義し取得する / 期待結果=採用傾向が個人を追跡せず観測でき、観測自体が漏洩経路にならない / 除外=個人追跡、行動スコアリング、外部送信を前提とする監視テレメトリ。
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / public-exposure
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0038`

## 1) 課題 / Problem statement

- 「説明可能な合意が社会へ広がっているか」を知るには観測が要るが、個人追跡・監視は本プロダクトの明確な非目標である。
- 非監視のまま採用・価値を観測する方法が未定義のため、社会的目標の達成度を安全に語れない。

## 2) 背景 / Context

- `ADR-0038` 柱4が非監視型採用シグナルを要件化した。
- `domain.md` / `ROADMAP.md` / `ADR-0032` は個人追跡・行動スコアリング・監視テレメトリ・SNS型公開を非目標とする。
- `VALUE-MEASURE-02` の二軸スコアカードと整合し、社会軸の観測を補完する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 価値観測は監視へ転用しない範囲でのみ、社会的目標の達成度を語れる。
- 安全（THREAT_MODEL / SafeMode）: 観測が新たな外部送信・漏洩経路を作らないことを最優先する。
- 企業・行政要件（enterprise_architecture）: プライバシー既定（local-first）を崩さずに導入説明できる。
- 後方互換（schemas）: 既存の診断・export形式の範囲で集計し、新規追跡データを持たない。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（非監視シグナルの定義、取得方法、禁止事項）。
- 変更の最小単位: 成果物ベース・集計・opt-in・ローカルファーストの観測項目を列挙し、各々が監視に当たらない根拠を添える。
- 非目標: 個人追跡、行動スコアリング、外部送信前提の監視テレメトリ、利用者識別。

## 5) 受入条件 / Acceptance criteria

- [ ] 採用シグナルが成果物ベース・集計・opt-in・ローカルファーストで定義される。
- [ ] 各シグナルについて「監視・個人追跡に当たらない」根拠が明記される。
- [ ] 観測が SafeMode 境界を越えず、新たな外部送信・漏洩経路を作らない。
- [ ] 個人追跡・行動スコアリング・監視テレメトリ拡張を行わない非目標が明記される。
- [ ] docs-check（validator/triage/rg）でシグナル定義の整合が確認される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 非監視シグナル候補（保留/根拠要素充足率、再オープン可能性の自己診断等）を列挙する。
- [ ] T2 各シグナルの取得方法（集計/opt-in/local）と非監視根拠を定義する。
- [ ] T3 禁止事項（個人追跡/行動スコアリング/監視テレメトリ）を明記する。
- [ ] T4 `security.md` / `data_handling.md` / `value_traceability.md` と同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `rg -n "非監視|opt-in|個人追跡|テレメトリ|採用シグナル" 01_Plans 02_Architecture 04_Documentation`
- 期待結果:
  - validator成功、triage stopper=none、非監視シグナル定義が検索可能。
- 未実施時の理由・代替検証:
  - 実観測前は、シグナル定義の安全レビュー（外部送信ゼロ確認）で代替し理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 一般的なアナリティクスを導入する。個人追跡・監視の非目標に反するため不採用。
- 代替案B: 採用観測を行わない。社会的目標の達成度を安全にも語れなくなるため、非監視範囲での観測を採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 非監視シグナルが徐々に個人追跡へ拡張される。
- 影響範囲: 診断、export、公開文書。
- ロールバック手順: シグナルを成果物内充足率の自己診断のみへ縮退し、収集系の追加を停止する。

## 10) Additional context

- 関連: 観測運用は `VALUE-MEASURE-02`、安全配布は `SOCIAL-DIFFUSION-03`。
- ADR化が必要になる条件: 採用シグナルを配布契約や公開ダッシュボードの恒久指標として固定する場合。


## 11) Stream H deferred activation lock（2026-06-13）

| Item | Planning decision |
| --- | --- |
| Classification | Hold / deferred-open-ready（VR5 direction retained, activation postponed） |
| Direction retained | opt-in・集計・ローカルファースト・成果物ベースの採用シグナルだけを候補にする。 |
| Activation condition | 個人追跡を伴わない採用シグナル設計と、漏洩経路にならない確認手順が存在する。 |
| Open condition | Real-user/cooperator milestone exists, SafeMode/share-export impact is explicitly reviewed, and this issue can remain docs/planning-first. |
| Explicit non-goal | 個人追跡、行動スコアリング、管理者中心の監視KPI。 |
| Deferral reason | `ADR-0039` keeps social-diffusion work out of mandatory implementation until social participants or a safe pilot exist. |

### Safe-diffusion guardrails

- Do not require real external participants while none exist.
- Do not add surveillance telemetry, user-level adoption scoring, or administrator-centered monitoring.
- Preserve evidence, hold, review, and SafeMode/share-export states in any future handoff.
