# Issue Draft: HIL-RS-02 A2 Frontend 可逆統合フロー適用

- Type: Implementation
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: TBD
- Priority: P1
- Owner: Frontend Owner
- Scope: `03_Implement/frontend/`
- Related Backlog: `HIL-RS-02`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`
- Dependencies: `HIL-RS-02`
- Expected verification level: `unit`

## 1) 背景

- HIL-RS-02の実装フェーズで、可逆差分の提示と人間確定UIを契約準拠で導入する必要がある。

## 2) 目的

- A1契約を変更せず、候補比較と手動確定のUI導線を実装する。

## 3) スコープ

- frontendの候補比較UI、差分表示、確定操作の監査イベント出力。
- 確定操作を「信頼できる人間操作（trusted click）」に限定するUI境界を追加する。

## 4) 非スコープ

- 自動確定、ランキング、単一正解提示。
- SafeMode default OFF化。

## 5) 受入条件

- AC-1: SafeMode既定ONでの動作が維持される。
- AC-2: 確定操作は人間操作時のみ発火する（trusted event check）。
- AC-3: 回帰テスト（unit）を追加し、既存機能の破壊がない。
- AC-4: 確定ボタンは理由入力後にのみ有効化され、無根拠クリックで確定導線へ到達しない。
- AC-5: 非目標（auto-confirm / ranking誘導 / SafeMode後退）をUI文言とテストで明示し、導線を作らない。

## 6) 検証方法

- `npm --prefix 03_Implement/frontend test -- src/ui/MergeSuggestionsPanel.test.ts src/ui/HilRsWorkflowPanel.test.ts`
- `npm --prefix 03_Implement/frontend run lint`

## 6.1) DoD（A2最小）

- [x] trusted event境界が `MergeSuggestionsPanel` の確定操作に適用されている。
- [x] `isReadOnly=true` で確定操作が無効化される。
- [x] 確定理由入力なしで確定ボタンを押せない。
- [x] 「自動確定しない」文言がUIに残り、テストで回帰監視される。
- [x] A1契約（contractId/schemaVersion/overridePolicy）への変更がない。

## 7) 依存関係

- `issue-HIL-RS-02-A1-governance-contract-hardening.md` 完了

## 8) リスク

- UI導線の追加で既存レビュー機能と競合する可能性。

## 9) 着手順

1. Plan: 契約とAC/DoDを確認し、A2 I/F固定値を維持する。
2. Execute: UIの確定操作導線にtrusted event境界を適用する。
3. Verify: unit/lintを通し、可逆ワークフロー表示と確定導線の回帰を確認する。
4. Proceed: 残課題を次タスクへハンドオフする。

## 10) CDC（Context / Decision / Consequences）

### Context

- HIL-RS-02 A2は、A1固定契約を変更せず「可逆統合の最終確定を人間に限定」する責務を持つ。
- `event.isTrusted` 境界なしでは、スクリプト実行や非意図的なUI自動化が確定導線に到達しうる。
- SafeMode既定ON・非目標（自動確定禁止）を守るには、確定導線の入口を明示的に狭める必要がある。

### Decision

- 確定操作（Accept / Partially accept / Reject / Defer）は trusted event + 非 read-only の時のみ実行する。
- 確定理由（decision reason）を正規化後に必須化し、未入力時は確定ボタン自体を無効化する。
- UI文言として「自動確定しない」「trusted human interaction が必要」を維持し、回帰テストで固定する。

### Consequences

- UX影響: 理由入力が1ステップ増えるが、誤確定や無根拠確定の抑止が強化される。
- 運用影響: 監査イベントの説明可能性が向上し、レビュー時の再現性が高まる。
- 監査影響: 非trusted操作と理由欠落の確定記録を防ぎ、監査証跡の品質を安定化できる。

## 11) Phase Log（Read -> Plan -> Execute -> Verify -> Proceed）

### Phase 1: Read

- A2 issue本文を再読し、AC/非目標を抽出。
- `03_Implement/frontend/src/ui/HilRsWorkflowPanel.tsx` を再読し、trusted human confirmation導線文言を確認。
- `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx` を再読し、確定操作のtrusted境界適用点を確認。
- `03_Implement/frontend/src/domain/hil_rs_trusted_boundary.ts` を再読し、trusted event判定のSSOTを確認。
- `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` を参照し、A1契約不変更制約を再確認。

### Phase 2: Plan

- AC/DoD不足を補完（AC-4, AC-5, DoD追加）。
- 実装単位を3つに分割:
  1. UI境界: 理由未入力時の確定ボタン無効化
  2. イベント検証: 既存trusted boundary関数の継続利用
  3. 回帰テスト: 非目標と境界文言の固定化

### Phase 3: ADR明文化（CDC）

- ADR追加なし。Issue内CDCとして Context/Decision/Consequences を記録。

### Phase 4: Execute

- `MergeSuggestionsPanel` で確定理由が空の間は確定ボタンを無効化。
- 既存 `evaluateMergeDecisionTrustBoundary` を維持し、trusted human操作限定を保持。
- auto-confirm / ranking誘導 / SafeMode後退の導線追加は実施しない。

### Phase 5: Verify

- unit + lint を実行して回帰を確認（結果は本Issue更新時に追記）。
- 失敗時は最大3回まで自己修復し、失敗継続時は停止報告。
- 実行結果:
  - `npm --prefix 03_Implement/frontend test -- src/ui/MergeSuggestionsPanel.test.ts src/ui/HilRsWorkflowPanel.test.ts` ✅
  - `npm --prefix 03_Implement/frontend run lint` ✅

### Phase 6: Proceed

- A3へ渡す残課題:
  - 運用文書側で「理由必須 + trusted限定」の監査観点を反映する際、A1契約値は固定参照のまま記載する。
- A1差し戻し要否:
  - 現時点で契約変更要求なし（差し戻し不要）。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream B Sync Snapshot（2026-05-04 / Read&Gap→ADR→Dependency-cut→Verify）

### 1) Dependency / Ready / Blocker 再検証
- dependency_state: `contract-first` を維持（実装完了待ちを Ready 条件に含めない）。
- ready_contract: `freezeContractId/schemaVersion/overridePolicy/safeModeDefault` 一致。
- ready_execution: `approved_by/approved_at/evidence` 充足かつ `Decision Queue Pending=0`。
- blockers_normalized:
  - `approval_pending`
  - `decision_queue_pending`
  - `contract_mismatch`
  - `out_of_scope_request`

### 2) AC/DoD 不足補完ドラフト（合意用）
- AC-draft-1: Ready 判定を `contract-ready` と `execution-ready` に二分し、両方の結果を記録する。
- AC-draft-2: Blocker は正規化4分類のみ使用し、自由記述のみで終わらせない。
- DoD-draft-1: `mock parallelizable items` を最低1件以上列挙する。
- DoD-draft-2: verify の自己修復回数を `<=3` で記録し、`>=4` は停止報告とする。

### 3) 依存切断（実装依存→契約依存）
- replace_rule: 実装依存の待ち条件は、同等の契約キー検証へ置換する。
- mock_parallelizable_items:
  1. Contract ID / fixed key 一致検証
  2. Gate 式（Go/Conditional/No-Go）の入力完全性検証
  3. Audit 4点セット（`query/bundle/proposal/apply`）欠損検知

### 4) Verify（triage再実行）
- command: `python 01_Plans/triage_actionable_plans.py`
- note: Ready/Blocked/Unlocks は triage 出力を正本とし、本Issue記録はその解釈補助とする。
- self_correction: `0/3`（本更新時点）


## Stream B Verification Refresh（2026-05-10）

- Phase 1 (Read): `MergeSuggestionsPanel` / `HilRsWorkflowPanel` / `hil_rs_trusted_boundary` とA2 Issue本文を再読し、A1契約不変更・trusted境界・理由必須を再確認。
- Phase 2 (Plan): A2 AC/DoDは不足なしと判断。trusted interaction限定・reason必須・SafeMode既定ON維持を継続方針として固定。
- Phase 3 (Execute): `hil_rs_client_apply.integration.test.ts` の `Document` fixture型を `DocumentV2` へ整合化し、契約外キー（`schemaVersion`）依存を除去。
- Phase 4 (Verify):
  - `npm --prefix 03_Implement/frontend test -- src/ui/MergeSuggestionsPanel.test.ts src/ui/HilRsWorkflowPanel.test.ts src/domain/hil_rs_client_apply.integration.test.ts` ✅
  - `npm --prefix 03_Implement/frontend run lint` ✅
  - 自己修復回数: `1/3`（typecheck失敗をfixture修正で解消）
- Phase 5 (Proceed): 変更は `03_Implement/frontend/**` と本Issueのみ。`contractId/schemaVersion/overridePolicy` の契約値変更なし。

## Stream D handoff-only boundary（2026-06-13）

### A1/A2 boundary
- A2 は Frontend実装issueであり、Stream D は実装・UI仕様確定・E2E追加を行わない。
- Stream D から渡す契約は read-only の `HIL_RS_DECISION_GATE_V1`, `HIL_RS_PATCH_PROPOSAL_V1`, `HIL_RS_APPLY_JUDGEMENT_V1` とする。
- A2 は `Approval Record=Pending` の間、`executeAllowed=false` と `proposal-only` を維持する。

### Implementation pre-read conditions
- 実装Streamは着手前に ADR-0026/0027/0028 と A1/RS-02-A1 issue の最新契約を再読する。
- `rollbackRef`, `riskLabels[]`, `query|bundle|proposal|apply` audit events の扱いを、実装前の受入条件に落とす。
- SafeMode既定ON、auto-apply禁止、AIによる `human_reviewed` 昇格禁止を非交渉条件にする。

### Stop conditions for A2 handoff
- `pendingDecisionQueueCount>0` のまま Proceed Go を求める。
- Frontend実装で A1固定キーを再定義する。
- 未承認proposalを自動適用・自動公開・レビュー済み化する。

### Handoff classification
- Stream D 判定: **handoff record only**。
- A2の実装可否は別Frontend Streamが A1承認・queue zero・固定キーdrift 0 を検証して判断する。
