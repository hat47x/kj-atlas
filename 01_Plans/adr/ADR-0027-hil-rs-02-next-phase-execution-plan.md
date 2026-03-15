# ADR-0027: HIL-RS-02 次フェーズ実行計画（議論→決定→文書化→同期）

- Status: Accepted
- Date: 2026-03-14
- Deciders: Project Maintainers
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/frontend/`, `04_Documentation/`
- Source Issue: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Related: `ADR-0026`, `00_Prompt/domain.md`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`, `01_Plans/next-phase-planning-minutes-2026-03-14.md`

## Context

`ADR-0026` は HIL-RS-01 の価値軸と A1→A2→A3 の契約先行を固定した。
一方で、次フェーズ着手に必要な「会議ログの定型」「Decision Queueの未確定管理」「dashboard同期手順」は単一文書として固定されていない。
このままでは、議論と実行ログが分散し、再開時に判断根拠が追跡しづらい。

## Decision

次フェーズを **HIL-RS-02** とし、以下を固定する。

### D1. 実行境界

- HIL-RS-02は「議論→意思決定→文書化→進捗同期」を1サイクルで完結させる計画フェーズとする。
- 変更はDocs/Planを主対象とし、実装変更はA2/A3 issueがOpen化されるまで行わない。

### D2. 安全・統治制約（非機能）

- SafeMode既定ON、share/export漏洩防止、責務分離（human_dual_control_only）を後退させない。
- 未確定項目はDecision Queueへ記録し、確定扱いしない。

### D3. 依存順序

1. Umbrella issue（HIL-RS-02）でAC/非スコープ/検証計画を固定する。
2. A1（Governance contract hardening）をOpen化し、A2/A3の着手条件を明示する。
3. A2（frontend適用）/A3（ops & docs同期）はDraftで先行準備し、A1完了後にOpen化する。

### D4. Exit Criteria

- EC-1: 議事録が作成され、論点ごとの「提案・懸念・反証・結論」を含む。
- EC-2: ADRに Context/Decision/Consequences/Alternatives/Rollback が存在する。
- EC-3: issue分解が最小実行単位（umbrella + A1/A2/A3）で作成される。
- EC-4: `project-progress-dashboard.md` と `issues/README.md` の Active / Decision Queue / 次の1手が同期される。
- EC-5: docs-check（validator + unittest + diff check）が成功する。

## Consequences

- 期待効果:
  - 計画フェーズの判断根拠が1サイクルで追跡可能になる。
  - A1依存を明示することで、A2/A3の手戻りを抑制できる。
- 副作用/制約:
  - Active issue数が増え、同期ドキュメントの更新コストが増加する。
  - 実装速度より監査容易性を優先するため短期速度は低下する。

## Alternatives

- 代替A（不採用）: HIL-RS-02を1 issueに集約する。
  - 不採用理由: 依存/責務境界が見えず、停止条件判定が不安定。
- 代替B（不採用）: A2/A3を即Open化して並列開始する。
  - 不採用理由: A1契約差分による再作業リスクが高い。

## Rollback

- ロールバック条件:
  1. 上位層（00〜02）との矛盾が検出された場合
  2. SafeMode/漏洩防止/責務分離の後退が必要になった場合
- ロールバック手順:
  1. HIL-RS-02-A2/A3をDraft維持またはOpenからDraftへ戻す。
  2. A1 issueへ変更要求を差し戻し、Decision Queueへ未確定として登録。
  3. 必要時は本ADRを Superseded とし、上位ADR改訂後に再起票する。

## Traceability

- Related: `01_Plans/next-phase-planning-minutes-2026-03-14.md`
- Related: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Related: `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
- Related: `01_Plans/issues/issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`
- Related: `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Derived-from: `ADR-0026`
