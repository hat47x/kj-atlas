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

### D5. HIL-RS凍結I/F（Contract/Governance）

- Freeze Pack ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Contract IDs（変更禁止）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`
- Fixed identifiers（変更禁止）:
  - `schemaVersion=1.0.0`（Critique / Attribution / TieBreak / Error）
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- SSOT（単一参照先）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`

### D6. 固定状態遷移 / 停止条件

- State transitions（固定）:
  - A2/A3公開判定: `Draft -> Open` は `A1 Done` かつ `DecisionQueue Pending=0` のときのみ許可。
  - Decision Queue: `Pending -> Approved` または `Pending -> Rejected` のみ許可。
- 禁止遷移:
  - `Pending` を経由しない確定化。
  - A1完了前の A2/A3 `Draft -> Open`。
- Stop conditions（即停止）:
  1. 契約ID / schemaVersion / overridePolicy / SSOT の不一致。
  2. SafeMode既定ON、share/export漏えい防止、`human_dual_control_only` の後退要求。
  3. 凍結対象共有リソース（dashboard/README）への未承認更新要求。

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

## Stream J Audit（ADR連動監査: active issue基準）

### Read

- `01_Plans/issues` の active status（Draft/Open/In Progress）と `triage_actionable_plans.py` の逆引き結果で、監査対象ADRを抽出した。
- 対象: `ADR-0026` / `ADR-0027`（active issue 直結）。

### ADR/CDC

- 監査対象2件について `Context` / `Decision` / `Consequences` の欠損有無を確認した。
- 判定: 欠損なし（未処理ADR 0件）。

### Plan

- 欠損ADRがある場合のみ、該当ADRへ欠損見出しを最小追記する。
- 欠損がない場合は、active issue 連動観点で「追加補完不要」を本文に固定する。

### Execute

- 今回は CDC 欠損が0件のため、補完項目の宣言と判定記録のみを最小追記した。

### Verify

- docs-check を `validator + unittest + triage` の組み合わせで再実行し、監査記録と整合することを確認する。

### Proceed（issue逆引き表）

| Active issue | 連動ADR | CDC欠損 | 対応 |
| --- | --- | --- | --- |
| `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis` | `ADR-0026` | なし | 追加補完不要 |
| `issue-HIL-RS-02-next-phase-delivery-plan` | `ADR-0027` | なし | 追加補完不要 |

## Traceability

- Related: `01_Plans/next-phase-planning-minutes-2026-03-14.md`
- Related: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Related: `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
- Related: `01_Plans/issues/issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`
- Related: `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Derived-from: `ADR-0026`


## Stream A serial execution update（2026-04-29）

### Plan（対象/非対象宣言）
- 対象: `ADR-0026/0027` と HIL-RS-01/02 issue（allowlist内）
- 非対象: 実装コード、dashboard、allowlist外issue。

### Execute（HIL-RS-01-A1 -> HIL-RS-02-A1 -> next-phase）
1. HIL-RS-01-A1 契約固定の再確認（fixed keys driftなし）。
2. HIL-RS-02-A1 統治ゲート（Pending bypass禁止・NoGo return path固定）を再確認。
3. next-phase計画は `Approval Record` 完了まで Draft/Conditional を維持。

### Verify（AC/DoD照合）
- AC: fixed keys diff=`0`、`unlockRule` 一致、`Pending -> Approved/Rejected` 以外の遷移追加なし。
- DoD: `Plan -> Execute -> Verify -> Proceed` を維持し、self-correction は `0/3`。
- Gate結果: **Conditional**（承認待ち継続）。
