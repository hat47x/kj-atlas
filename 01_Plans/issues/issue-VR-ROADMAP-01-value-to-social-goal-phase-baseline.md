# Issue Draft: VR-ROADMAP-01 価値→社会的目標 実現フェーズのベースライン

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: TBD（A=Productization Program Owner / R=Plan Owner）
- Scope: `01_Plans/` only（`02_Architecture/value_traceability.md` / `AGENTS.md` は本Streamでは変更提案のみ）
- Related Backlog: `VR-ROADMAP-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0036-value-to-social-goal-realization-roadmap.md`, `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: VR-ROADMAP-01
- RequirementStatement: 価値ループ V0–V4 を社会的目標まで一直線に並べた VR0–VR5 フェーズ系列を、既存issueの再配置として固定し、各フェーズの Entry/Exit Gate と担当issueを追跡可能にする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ADR-0035がProposedで存在する / 操作=VR0–VR5の担当issueとExit Gateを value_traceability と突合する / 期待結果=各VRに正担当issueとExit条件が1対1で対応し、未接続フェーズが0件 / 除外=新しい価値原則の追加、実装着手。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode（非後退の確認のみ）
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0036`

## 1) 課題 / Problem statement

- フェーズ定義が `ADR-0002` / `ADR-0028` / `ADR-0007` / `ROADMAP.md` / `ADR-0001` に分散し、「価値→社会的目標」を一本で説明できない。
- 個人・チームの共有(V4)の先にある社会的普及層が未フェーズ化で、何が残っているか判断できない。

## 2) 背景 / Context

- `ADR-0036` が VR0–VR5 と社会的目標の北極星表現を固定した（本issueはその実行ベースライン）。
- `ADR-0032` は V0–V4ループと観測契約を、`value_traceability.md` は価値→設計→検証の対応を持つ。
- VR4/VR5の新規作業は `ADR-0037` / `ADR-0038` と各新規issueへ委譲済み。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 価値→社会的目標の優先順位を単一背骨で固定し、スコープドリフトを防ぐ。
- 安全（THREAT_MODEL / SafeMode）: 全VR共通の非後退不変条件（SafeMode既定ON等）を明示し、フェーズ進行で弱めない。
- 企業・行政要件（enterprise_architecture）: 「どのフェーズに何の説明責任があるか」を組織導入時に提示できる。
- 後方互換（schemas）: ドキュメント層の再配置に限定し、スキーマ・実装を変更しない。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（`value_traceability.md` への VR系列追記、`AGENTS.md` のADR参照範囲更新、本issueでの追跡）。
- 変更の最小単位: VR0–VR5 ごとに「正担当issue / Entry / Exit / 非後退条件」を1行で対応づける。
- 非目標: 新しい価値原則の追加、UI/Backend/Schema実装、既存フェーズ体系（CE/FB/PRODUCT-UX）の置換。

## 5) 受入条件 / Acceptance criteria

- [ ] VR0–VR5 の各フェーズに、正担当issue（既存または新規）が1件以上対応している。
- [ ] 各VRの Exit Gate が、対応issueの受入条件またはKPIへ追跡できる。
- [ ] 全VR共通の非後退不変条件（SafeMode既定ON / `human_reviewed`人手昇格 / patch+approval / `provider=none`既定）が明文化されている。
- [ ] `value_traceability.md` と `AGENTS.md` の更新が必要な場合は、本Streamでは直接編集せず変更提案として記録されている。
- [ ] 本ベースラインは `ADR-0036` がAcceptedになるまで実装着手を要求しない（docs-only）。
- [ ] 検証（docs-check）として validator / triage / `rg` の実行結果が記録される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 VR0–VR5 と既存issue/新規issueの対応表を確定する。
- [ ] T2 各VRの Exit Gate を対応issueのAC/KPIへリンクする。
- [ ] T3 `value_traceability.md` に社会的目標接続節を追記する変更提案を記録する（本Streamでは未編集）。
- [ ] T4 `AGENTS.md` のADR参照範囲を更新する変更提案を記録する（本Streamでは未編集）。
- [ ] T5 docs-check（validator/triage/rg）で整合を確認する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `rg -n "VR0|VR1|VR2|VR3|VR4|VR5|社会的目標" 01_Plans 02_Architecture AGENTS.md`
- 期待結果:
  - validator成功、triage stopper=none、VR系列が検索可能。
- 未実施時の理由・代替検証:
  - Python未導入時は `rg` と目視レビューで代替し理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既存フェーズ体系のまま運用する。価値→社会的目標の接続が曖昧なまま残るため不採用。
- 代替案B: 既存フェーズADRを全面改訂して統合する。意思決定境界が壊れ履歴追跡性が落ちるため、索引ADR（ADR-0036）方式を採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: VR系列が既存フェーズと二重管理になり、どちらが正本か曖昧化する。
- 影響範囲: `01_Plans`、`value_traceability.md`、`AGENTS.md`。
- ロールバック手順: VR系列を `ADR-0036` 内の索引のみへ戻し、value_traceability追記を撤回する。

## 10) Additional context

- 関連: VR4は `VALUE-MEASURE-01/02`、VR5は `SOCIAL-DIFFUSION-01..04` が新規担当。VR0–VR3は既存 `PRODUCT-VALUE-*` / `PRODUCT-UX-*` / `CE*` を再利用。
- ADR化が必要になる条件: VR系列をプロジェクト恒久のフェーズ正本へ昇格し、既存フェーズADRをsupersedeする場合。


## 11) Stream H phase baseline（2026-06-13）

| VR | State | Primary issues | Exit condition | Open / activation condition |
| --- | --- | --- | --- | --- |
| VR0 | Active | CE0 / safety policy / threat model lineage | SafeMode default ON, `provider=none` default, patch+approval, and manual `human_reviewed` promotion remain non-regressed. | Already active as invariant backbone; only regression-fix issues open. |
| VR1 | Active | `PRODUCT-VALUE-01`, `PRODUCT-UX-01` | First-use path reaches meaningful card placement plus grouping/hold state. | Product-value/UX issues may open when their AC and docs-check/unit scope are fixed. |
| VR2 | Active | `PRODUCT-VALUE-02`, `PRODUCT-UX-02`, CE1/CE2, DOMAIN-EXPR sequence | Hold/Critique/Evidence/Contradiction can be retained as work state and not auto-resolved. | Domain-expression issues may open in phase order; schema changes must be separately approved. |
| VR3 | Active | `PRODUCT-VALUE-03`, `PRODUCT-UX-03`, CE3 | Reviewable outcome package preserves confirmed, held, unreviewed, and evidence-linked information with safe return path. | Outcome-package issues may open when SafeMode/share-export AC are explicit. |
| VR4 | Deferred | `VALUE-MEASURE-01`, `VALUE-MEASURE-02`, `MVP-EXIT-01`, `PRODUCT-QA-01` | Measurement harness and scorecard are defined as reproducible planning artifacts. | Open only after real-user/cooperator milestone or maintainer-approved surrogate evidence; not a solo pre-release blocker. |
| VR5 | Deferred | `SOCIAL-DIFFUSION-01..04`, CE4, public roadmap operations | Reproducibility, revisability, evidence-anchored diffusion, and non-surveillance signals are defined without mandating external participants. | Open only after safe sharing/publishing path and real-user/cooperator milestone exist. |

### Cross-stream guardrails

- Do not edit `02_Architecture/value_traceability.md`, `AGENTS.md`, `03_Implement/`, or `04_Documentation/` from this Stream; record proposals only.
- VR4/VR5 remain directionally accepted but activation-deferred under `ADR-0039`; do not convert them into release blockers.
- Solo OSS/pre-release governance stays lightweight: Maintainer ownership is sufficient unless a later activation milestone introduces real participants.
